import json
import re
import random
from pathlib import Path
from collections import defaultdict, Counter

# --- UTILS CHO LOCOMO ---
def parse_locomo_evidence(ev_str):
    """Parse 'D1:7' thành (session_idx, turn_idx) để tính toán khoảng cách"""
    try:
        # Format: D<session>:<turn>
        match = re.match(r"D(\d+):(\d+)", ev_str)
        if match:
            return int(match.group(1)), int(match.group(2))
    except:
        pass
    return 0, 0

def get_locomo_dist(ev_list):
    """Tính khoảng cách hội thoại giữa điểm đầu và điểm cuối của bằng chứng"""
    if not ev_list or len(ev_list) < 2:
        return 0
    parsed = [parse_locomo_evidence(e) for e in ev_list]
    # Giả định mỗi session có tối đa 100 lượt để tính index tương đối
    global_indices = [(s * 100) + t for s, t in parsed]
    return max(global_indices) - min(global_indices)

# --- HEURISTICS CHO LONGMEMEVAL (KHẮT KHE HƠN) ---
def is_extremely_hard_lme(item, counts, quotas):
    q_id = item.get("question_id", "")
    q_text = item.get("question", "").lower()
    q_type = item.get("question_type", "")

    # 0. Abstention: ưu tiên lấy đủ để test hallucination control / cycle guards
    if q_id.endswith("_abs"):
        if counts["abstention"] < quotas["abstention"]:
            counts["abstention"] += 1
            return True

    # 0.5 Prospective memory: bắt các tín hiệu intention planning
    prospective_keywords = ["plan", "intend", "going to", "hope", "tomorrow", "next week", "aim"]
    if any(kw in q_text for kw in prospective_keywords):
        if counts["prospective"] < quotas["prospective"]:
            counts["prospective"] += 1
            return True
    
    # 1. Knowledge Update: Giữ toàn bộ (thường khoảng 30-50 câu)
    if q_type == "knowledge-update":
        if counts[q_type] < quotas["knowledge-update"]:
            counts[q_type] += 1
            return True
    
    # 2. Temporal Reasoning: Giữ toàn bộ
    if q_type == "temporal-reasoning":
        if counts[q_type] < quotas["temporal-reasoning"]:
            counts[q_type] += 1
            return True

    # 3. Multi-session: Chỉ giữ nếu bằng chứng nằm ở >= 3 session (Rất khó cho RAG)
    if q_type == "multi-session":
        evidence_sessions = item.get("answer_session_ids", [])
        if len(evidence_sessions) >= 3 and counts[q_type] < quotas["multi-session"]:
            counts[q_type] += 1
            return True
            
    # 4. Preference & Others: Lấy mẫu ngẫu nhiên rất ít (chỉ để test sự tồn tại của mạng Habit)
    if q_type in ["single-session-preference", "single-session-user"]:
        if counts[q_type] < quotas["single-session"]:
            counts[q_type] += 1
            return True

    return False


def flatten_session_text(session):
    if isinstance(session, list):
        return " ".join(turn.get("content", "") for turn in session if isinstance(turn, dict))
    if isinstance(session, dict):
        return session.get("content", "")
    if isinstance(session, str):
        return session
    return ""


def estimate_session_gap(item):
    hay_ids = item.get("haystack_session_ids", [])
    answer_ids = item.get("answer_session_ids", [])
    if not hay_ids or not answer_ids:
        return 0

    indices = [hay_ids.index(ans_id) for ans_id in answer_ids if ans_id in hay_ids]
    if len(indices) >= 2:
        return max(indices) - min(indices)
    if len(indices) == 1:
        # Nếu chỉ có 1 answer session, ưu tiên bằng chứng càng xa cuối timeline càng tốt.
        return max(0, (len(hay_ids) - 1) - indices[0])
    return 0


def estimate_conflict_density(item):
    sessions = item.get("haystack_sessions", [])
    corpus = " ".join(flatten_session_text(sess).lower() for sess in sessions)
    conflict_keywords = [
        "change",
        "changed",
        "update",
        "updated",
        "moved",
        "switch",
        "switched",
        "left",
        "quit",
        "now",
        "used to",
        "no longer",
        "instead",
        "previously",
        "before",
        "after",
    ]
    return sum(corpus.count(kw) for kw in conflict_keywords)


def estimate_entity_overlap(item):
    sessions = item.get("haystack_sessions", [])
    per_session_entities = []
    for sess in sessions:
        text = flatten_session_text(sess)
        entities = set(re.findall(r"\b[A-Z][a-z]{2,}\b", text))
        if entities:
            per_session_entities.append(entities)

    if not per_session_entities:
        return 0

    counter = Counter()
    for ent_set in per_session_entities:
        counter.update(ent_set)

    # Số entity xuất hiện lặp ở >= 2 sessions, đại diện mức chồng chéo thực thể.
    return sum(1 for _, freq in counter.items() if freq >= 2)


def small_subset_score(item):
    q_type = item.get("question_type", "")
    priority = {
        "multi-session": 3,
        "knowledge-update": 2,
        "temporal-reasoning": 1,
    }.get(q_type, 0)

    session_gap = estimate_session_gap(item)
    conflict_density = estimate_conflict_density(item)
    entity_overlap = estimate_entity_overlap(item)

    # Ưu tiên category trước, sau đó mới xét độ phức tạp.
    score = (
        priority * 100
        + min(session_gap, 25) * 3
        + min(conflict_density, 20) * 2
        + min(entity_overlap, 25)
    )
    return score, session_gap, conflict_density, entity_overlap


def build_lme_small_subset(lme_items, target_total=12):
    preferred_counts = {
        "multi-session": 5,
        "knowledge-update": 4,
        "temporal-reasoning": 3,
    }

    scored = []
    for item in lme_items:
        score, gap, conflict, overlap = small_subset_score(item)
        enriched = dict(item)
        enriched["_small_subset_meta"] = {
            "score": score,
            "session_gap": gap,
            "conflict_density": conflict,
            "entity_overlap": overlap,
        }
        scored.append(enriched)

    selected = []
    selected_ids = set()

    # 1) Chọn theo quota ưu tiên MS/KU/TR
    for q_type, need in preferred_counts.items():
        candidates = [x for x in scored if x.get("question_type") == q_type]
        candidates.sort(key=lambda x: x["_small_subset_meta"]["score"], reverse=True)
        for cand in candidates:
            qid = cand.get("question_id")
            if qid in selected_ids:
                continue
            selected.append(cand)
            selected_ids.add(qid)
            if len([s for s in selected if s.get("question_type") == q_type]) >= need:
                break

    # 2) Nếu chưa đủ target thì lấy thêm theo tổng điểm cao nhất
    if len(selected) < target_total:
        remain = [x for x in scored if x.get("question_id") not in selected_ids]
        remain.sort(key=lambda x: x["_small_subset_meta"]["score"], reverse=True)
        for cand in remain:
            selected.append(cand)
            selected_ids.add(cand.get("question_id"))
            if len(selected) >= target_total:
                break

    # Xóa metadata tạm trước khi ghi file
    for item in selected:
        item.pop("_small_subset_meta", None)

    return selected

# --- HEURISTICS CHO LOCOMO ---
def filter_hard_locomo_qa(sample):
    hard_qas = []
    for qa in sample.get("qa", []):
        # FIX: category là int, không dùng .lower()
        cat = qa.get("category", 0)
        evidence = qa.get("evidence", []) 
        
        # 1. Multi-hop: Khoảng cách giữa các bằng chứng > 100 lượt hội thoại
        if len(evidence) >= 2:
            dist = get_locomo_dist(evidence)
            if dist > 100:
                hard_qas.append(qa)
                continue
        
        # 2. Causal/Habit keywords trong câu hỏi (Dành cho mạng Action-Effect)
        q_lower = qa["question"].lower()
        if any(kw in q_lower for kw in ["why", "reason", "habit", "always", "usually", "tend to"]):
            hard_qas.append(qa)
            
    sample["qa"] = hard_qas 
    return sample

def main():
    # Giảm dataset theo tỷ lệ nhưng giữ nguyên phân bố tương đối
    scale = 1 / 3

    def scaled_quota(base):
        return max(1, round(base * scale))

    # 1. Xử lý LongMemEval
    lme_path = Path(r"data\LongMemEval\longmemeval_s_cleaned.json")
    if lme_path.exists():
        with open(lme_path, "r", encoding="utf-8") as f:
            lme_data = json.load(f)
        
        random.seed(42) # Đảm bảo reproducible
        random.shuffle(lme_data)

        quotas = {
            "knowledge-update": scaled_quota(35),
            "temporal-reasoning": scaled_quota(35),
            "multi-session": scaled_quota(35),
            "abstention": scaled_quota(20),
            "prospective": scaled_quota(15),
            "single-session": scaled_quota(15),
        }
        lme_counts = defaultdict(int)
        lme_distilled = [item for item in lme_data if is_extremely_hard_lme(item, lme_counts, quotas)]
        
        with open("data/longmemeval_s_distilled.json", "w", encoding="utf-8") as f:
            json.dump(lme_distilled, f, indent=2, ensure_ascii=False)
        print(f"✅ LongMemEval Distilled: {len(lme_distilled)} samples saved.")
        print(f"   Breakdown: {dict(lme_counts)}")
        print(f"   Quotas (scale={scale:.3f}): {quotas}")

        # 1.1 Tạo tập nhỏ 10-12 conversations, nghiêng mạnh về MS/KU/TR
        lme_small = build_lme_small_subset(lme_distilled, target_total=12)
        small_counts = Counter(item.get("question_type", "unknown") for item in lme_small)
        with open("data/longmemeval_s_distilled_small.json", "w", encoding="utf-8") as f:
            json.dump(lme_small, f, indent=2, ensure_ascii=False)
        print(f"✅ LongMemEval Small: {len(lme_small)} conversations saved.")
        print(f"   Small breakdown: {dict(small_counts)}")

    # 2. Xử lý LoCoMo
    locomo_path = Path(r"data\LoCoMo\locomo10.json")
    if locomo_path.exists():
        with open(locomo_path, "r", encoding="utf-8") as f:
            locomo_data = json.load(f)
        
        random.seed(42)  # Reproducible conversation-level sampling for LoCoMo
        target_locomo_convs = 5
        locomo_distilled = []
        for sample in locomo_data:
            # Copy để không làm hỏng data gốc trong bộ nhớ
            sample_copy = json.loads(json.dumps(sample))
            processed_sample = filter_hard_locomo_qa(sample_copy)
            if len(processed_sample["qa"]) > 0:
                locomo_distilled.append(processed_sample)

        # Giữ nguyên toàn bộ QA của mỗi hội thoại, chỉ giảm số lượng hội thoại
        if len(locomo_distilled) > target_locomo_convs:
            locomo_distilled = random.sample(locomo_distilled, target_locomo_convs)
        
        with open("data/locomo_distilled.json", "w", encoding="utf-8") as f:
            json.dump(locomo_distilled, f, indent=2, ensure_ascii=False)
        
        total_qa = sum(len(s["qa"]) for s in locomo_distilled)
        print(f"✅ LoCoMo Distilled: {len(locomo_distilled)} convs (full), {total_qa} total QAs saved.")

if __name__ == "__main__":
    main()