import json
import re
import random
from pathlib import Path
from collections import defaultdict

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