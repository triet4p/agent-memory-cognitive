import time
import json
import requests
import re
from pathlib import Path

BASE_URL = "http://localhost:8888/v1/default"
BANK_ID_PREFIX = "hindsight_eval_"
# Ngưỡng an toàn cho mỗi lần gọi API (nên để 10k-12k để tránh overhead hệ thống)
MAX_CHUNK_CHARS = 20000 

def split_text_into_sentences(text):
    """Bẻ văn bản thành các câu dựa trên dấu chấm và khoảng trắng."""
    # Regex bắt các dấu chấm kết thúc câu nhưng tránh bẻ nhầm các từ viết tắt (e.g., Mr., Dr.)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences

def analyze_hindsight_cost(sample_index=0):
    data_path = Path("data/longmemeval_s_distilled_small.json")
    if not data_path.exists(): return

    with open(data_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    
    sample = samples[sample_index]
    q_id = sample.get("question_id") or sample.get("sample_id")
    bank_id = f"{BANK_ID_PREFIX}{q_id.replace('-', '_')}"
    sessions = sample.get("haystack_sessions", [])
    
    print(f"📊 PHÂN TÍCH CHI PHÍ HINDSIGHT (SENTENCE-LEVEL SMART CHUNKING)")
    print(f"🆔 ID: {q_id} | Sessions: {len(sessions)}")
    
    print(f"\n🛠️  Đang khởi tạo Bank: {bank_id}...")
    try: requests.delete(f"{BASE_URL}/banks/{bank_id}", timeout=10)
    except: pass
    requests.put(f"{BASE_URL}/banks/{bank_id}", json={"name": "Cost Analysis", "mission": "Baseline"}, timeout=10)

    session_metrics = []
    start_total = time.time()
    
    print(f"\n--- BẮT ĐẦU XÂY DỰNG GRAPH ---")
    
    for i, session in enumerate(sessions):
        start_step = time.time()
        
        # --- LOGIC CHIA NHỎ THÔNG MINH ---
        final_api_calls = []
        current_payload = ""

        for turn in session:
            role = turn.get('role', 'user').upper()
            content = turn.get('content', '')
            full_turn_text = f"{role}: {content}\n"

            # Nếu nguyên 1 turn nhỏ hơn giới hạn, gom vào payload hiện tại
            if len(current_payload) + len(full_turn_text) < MAX_CHUNK_CHARS:
                current_payload += full_turn_text
            else:
                # Nếu payload hiện tại đã có dữ liệu, chốt nó lại
                if current_payload:
                    final_api_calls.append(current_payload)
                    current_payload = ""

                # Nếu bản thân 1 turn này đã lớn hơn giới hạn -> Phải bẻ theo câu
                if len(full_turn_text) >= MAX_CHUNK_CHARS:
                    sentences = split_text_into_sentences(content)
                    temp_sub_turn = f"{role}: "
                    
                    for sent in sentences:
                        # Nếu thêm 1 câu vào mà vẫn trong giới hạn
                        if len(temp_sub_turn) + len(sent) < MAX_CHUNK_CHARS:
                            temp_sub_turn += sent + " "
                        else:
                            # Chốt mảnh hiện tại và bắt đầu mảnh mới với Role cũ
                            final_api_calls.append(temp_sub_turn.strip())
                            temp_sub_turn = f"{role}: {sent} "
                    
                    if len(temp_sub_turn) > len(f"{role}: "):
                        current_payload = temp_sub_turn # Phần dư của turn dài chuyển sang payload tiếp theo
                else:
                    # Turn này to nhưng chưa tới mức vượt giới hạn 1 mình, bắt đầu payload mới
                    current_payload = full_turn_text

        if current_payload:
            final_api_calls.append(current_payload)

        # --- THỰC THI GỌI API ---
        print(f"🔄 Session {i+1}/{len(sessions)} | API Calls: {len(final_api_calls)}...", end="", flush=True)
        success = True

        for idx, part in enumerate(final_api_calls):
            try:
                print(f"\n   📡 API Call {idx+1}/{len(final_api_calls)}...", end="", flush=True)
                response = requests.post(
                    f"{BASE_URL}/banks/{bank_id}/memories",
                    json={"items": [{"content": part}], "async": False},
                    timeout=5400
                )
                if response.status_code != 200:
                    success = False; break
            except:
                success = False; break
        
        duration = time.time() - start_step
        if success:
            stats = requests.get(f"{BASE_URL}/banks/{bank_id}/stats", timeout=10).json()
            session_metrics.append({"session": i + 1, "duration": duration, "nodes": stats['total_nodes']})
            print(f" ✅ {duration:.1f}s (Nodes: {stats['total_nodes']})")
        else:
            print(f" ❌ Lỗi xử lý")
            
    total_duration = time.time() - start_total
    print(f"\n🏁 TỔNG KẾT: {total_duration/60:.2f} phút")

if __name__ == "__main__":
    analyze_hindsight_cost(10)