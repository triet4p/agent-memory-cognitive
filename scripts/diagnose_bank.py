"""Entity diagnostic script: search facts by entity keyword in a memory bank.

Usage:
    python scripts/diagnose_bank.py <bank_id> <entity_keyword> [--fact-type <type>] [--limit 20]

Example:
    python scripts/diagnose_bank.py e7_full "Spitfire" --limit 50
    python scripts/diagnose_bank.py e7_full "Tiger I" --fact-type experience
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any


async def _resolve_db_url() -> str:
    db_url = os.getenv("COGMEM_API_DATABASE_URL", "pg0")
    return db_url


async def _run_diagnose(
    bank_id: str,
    keyword: str,
    fact_type: str | None,
    limit: int,
) -> dict[str, Any]:
    import asyncpg

    db_url = await _resolve_db_url()

    if db_url == "pg0" or db_url.startswith("pg0"):
        print("ERROR: pg0 embedded database is not supported by this script. "
              "Set COGMEM_API_DATABASE_URL to a postgresql:// URL.", file=sys.stderr)
        sys.exit(1)

    # asyncpg uses postgresql:// directly (strip +asyncpg driver suffix if present)
    asyncpg_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    pool = await asyncpg.create_pool(asyncpg_url, min_size=1, max_size=5)

    try:
        async with pool.acquire() as conn:
            keyword_pattern = f"%{keyword}%"

            if fact_type:
                rows = await conn.fetch(
                    """
                    SELECT mu.id, mu.fact_type, mu.text, mu.document_id, mu.chunk_id,
                           mu.raw_snippet IS NOT NULL AS has_snippet,
                           mu.created_at
                    FROM memory_units mu
                    WHERE mu.bank_id = $1
                      AND mu.fact_type = $3
                      AND (mu.text ILIKE $2 OR EXISTS (
                          SELECT 1 FROM unit_entities ue
                          JOIN entities e ON ue.entity_id = e.id
                          WHERE ue.unit_id = mu.id AND e.name ILIKE $2
                      ))
                    ORDER BY mu.created_at DESC
                    LIMIT $4
                    """,
                    bank_id,
                    keyword_pattern,
                    fact_type,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT mu.id, mu.fact_type, mu.text, mu.document_id, mu.chunk_id,
                           mu.raw_snippet IS NOT NULL AS has_snippet,
                           mu.created_at
                    FROM memory_units mu
                    WHERE mu.bank_id = $1
                      AND (mu.text ILIKE $2 OR EXISTS (
                          SELECT 1 FROM unit_entities ue
                          JOIN entities e ON ue.entity_id = e.id
                          WHERE ue.unit_id = mu.id AND e.name ILIKE $2
                      ))
                    ORDER BY mu.created_at DESC
                    LIMIT $3
                    """,
                    bank_id,
                    keyword_pattern,
                    limit,
                )

            results = []
            for row in rows:
                results.append({
                    "id": str(row["id"]),
                    "fact_type": row["fact_type"],
                    "text": row["text"],
                    "document_id": row["document_id"],
                    "chunk_id": row["chunk_id"],
                    "has_snippet": row["has_snippet"],
                    "created_at": str(row["created_at"]) if row["created_at"] else None,
                })

            chunk_id_null = await conn.fetchval(
                "SELECT COUNT(*) FROM memory_units WHERE bank_id = $1 AND chunk_id IS NULL",
                bank_id,
            )
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM memory_units WHERE bank_id = $1",
                bank_id,
            )

            return {
                "bank_id": bank_id,
                "keyword": keyword,
                "fact_type_filter": fact_type,
                "total_units": total,
                "chunk_id_null_count": chunk_id_null,
                "chunk_id_populated_count": total - chunk_id_null,
                "matches": results,
            }
    finally:
        await pool.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnose entity presence in a memory bank.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("bank_id", help="Memory bank ID to diagnose")
    parser.add_argument("entity_keyword", help="Keyword or entity name to search for")
    parser.add_argument(
        "--fact-type",
        dest="fact_type",
        default=None,
        choices=["world", "experience", "opinion", "habit", "intention", "action_effect"],
        help="Filter by fact type",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max results to return (default: 20)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON (no formatting)",
    )

    args = parser.parse_args()

    result = asyncio.run(
        _run_diagnose(
            bank_id=args.bank_id,
            keyword=args.entity_keyword,
            fact_type=args.fact_type,
            limit=args.limit,
        )
    )

    if args.json:
        print(json.dumps(result))
    else:
        print(f"\n=== Diagnostic Report ===")
        print(f"Bank: {result['bank_id']}")
        print(f"Keyword: {result['keyword']}")
        if result["fact_type_filter"]:
            print(f"Fact type filter: {result['fact_type_filter']}")
        print(f"\nTotal units: {result['total_units']}")
        print(f"chunk_id populated: {result['chunk_id_populated_count']}")
        print(f"chunk_id NULL: {result['chunk_id_null_count']}")
        print(f"\nMatches: {len(result['matches'])}")

        for i, match in enumerate(result["matches"], 1):
            snippet_preview = ""
            if match["has_snippet"]:
                snippet_preview = " [snippet=YES]"
            else:
                snippet_preview = " [snippet=NO]"
            print(
                f"\n  [{i}] {match['fact_type']} | chunk={match['chunk_id'] or 'NULL'} | doc={match['document_id']}{snippet_preview}"
            )
            print(f"      {match['text'][:120]}{'...' if len(match['text']) > 120 else ''}")

    sys.exit(0)


if __name__ == "__main__":
    main()
