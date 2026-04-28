# `config.py` — All Environment Configuration

## Two Dataclasses

**`CogMemRuntimeConfig`**: Service-level config — used by `main.py`, `server.py`:
- `database_url`, `database_schema`, `host`, `port`, `log_level`, `workers`
- `llm_provider`, `llm_model`, `llm_api_key`, `llm_base_url`, `llm_timeout`
- `retain_llm_timeout`, `reflect_llm_timeout`
- `judge_llm_*` fields (separate judge config)

**`CogMemConfig`**: Engine-level config — used by `memory_engine.py`, `retrieval.py`, etc.:
- `graph_retriever` — `bfs` | `link_expansion` | `mpfp`
- `bfs_refractory_steps`, `bfs_firing_quota`, `bfs_activation_saturation`
- `retain_extraction_mode`, `retain_chunk_size`, `retain_two_pass_enabled`, etc.

## Why the Split?

`get_config()` (which engine modules call) builds `CogMemConfig` by extracting engine-relevant fields from `CogMemRuntimeConfig`. The split reflects the **service vs engine** boundary.

## `get_config()` — Cached Singleton

```python
_cached_config: CogMemConfig | None = None

def get_config() -> CogMemConfig:
    global _cached_config
    if _cached_config is None:
        runtime = _get_raw_config()
        _cached_config = CogMemConfig(...)
    return _cached_config
```

The cache is populated on first call and reused for the process lifetime. Changing `.env` requires restarting the server.

## Key Implementations

**`_read_graph_retriever()`** validates against `ALLOWED_GRAPH_RETRIEVERS = {"bfs", "link_expansion", "mpfp"}`. Invalid values fall back to `bfs` (since S20, the SUM+guards contribution).

**`_read_bool()`** accepts `{"1", "true", "yes", "y", "on"}` as True and `{"0", "false", "no", "n", "off"}` as False.

**`@dataclass(frozen=True)`** makes instances immutable. Accidental mutation of config values at runtime would be a very hard-to-debug production issue.

## All Environment Variables

| Variable | Default | What It Controls |
|----------|---------|-----------------|
| `COGMEM_API_DATABASE_URL` | `pg0` | DB connection (`pg0` = embedded postgres) |
| `COGMEM_API_GRAPH_RETRIEVER` | `bfs` | Graph traversal strategy |
| `COGMEM_API_RETAIN_CHUNK_SIZE` | `3000` | Single-pass chunk size |
| `COGMEM_API_RETAIN_TWO_PASS_ENABLED` | `True` | Enable two-pass extraction |
| `COGMEM_API_BFS_REFRACTORY_STEPS` | `1` | Cycle guard 1: refractory period |
| `COGMEM_API_BFS_FIRING_QUOTA` | `2` | Cycle guard 2: max fires per node |
| `COGMEM_API_BFS_ACTIVATION_SATURATION` | `2.0` | Cycle guard 3: max activation |

## Verify Commands

```bash
uv run python -c "
from cogmem_api.config import get_config
c = get_config()
print('graph_retriever:', c.graph_retriever)
print('bfs_refractory_steps:', c.bfs_refractory_steps)
print('bfs_firing_quota:', c.bfs_firing_quota)
print('retain_two_pass_enabled:', c.retain_two_pass_enabled)
"
```
