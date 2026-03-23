import time
import json
import requests
from pathlib import Path

# Cấu hình API - Trỏ trực tiếp vào Docker Hindsight đang chạy trên Windows
BASE_URL = "http://localhost:8888/v1/default"
BANK_ID_PREFIX = "cost_eval_"

def analyze_hindsight_cost(sample_index=0):
    # 1. Load dữ liệu từ tập distilled (đảm bảo đúng đường dẫn file của bạn)
    data_path = Path("data/longmemeval_s_distilled.json")
    if not data_path.exists():
        print(f"❌ Không tìm thấy file: {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    
    # Lấy sample để test
    sample = samples[sample_index]
    
    # Lấy ID chính xác (LongMemEval dùng 'question_id')
    q_id = sample.get("question_id") or sample.get("sample_id")
    bank_id = f"{BANK_ID_PREFIX}{q_id.replace('-', '_')}"
    
    # Lấy danh sách sessions
    sessions = sample.get("haystack_sessions", [])
    
    print(f"📊 PHÂN TÍCH CHI PHÍ HINDSIGHT")
    print(f"🆔 ID: {q_id}")
    print(f"📝 Số lượng sessions cần xử lý: {len(sessions)}")
    print(f"❓ Question: {sample.get('question')}")
    
    # 2. Reset Bank để đảm bảo kết quả đo lường không bị lẫn
    print(f"\n🛠️  Đang khởi tạo Bank: {bank_id}...")
    try:
        requests.delete(f"{BASE_URL}/banks/{bank_id}", timeout=10) # Thêm timeout
    except requests.exceptions.RequestException as e:
        print(f"   (Không thể xóa bank cũ, có thể chưa tồn tại: {e})")

    requests.put(f"{BASE_URL}/banks/{bank_id}", json={
        "name": "Cost Analysis",
        "mission": "Evaluating baseline Hindsight overhead"
    }, timeout=10)

    # 3. Quy trình Retain (Xây dựng Graph)
    session_metrics = []
    start_total = time.time()
    
    print(f"\n--- BẮT ĐẦU XÂY DỰNG GRAPH ---")
    
    for i, session in enumerate(sessions):
        # LongMemEval session là list các dict {'role':..., 'content':...}
        transcript = ""
        for turn in session:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            transcript += f"{role.upper()}: {content}\n"
        
        print(f"🔄 Đang xử lý Session {i+1}/{len(sessions)} ({len(transcript)} ký tự)...", end="", flush=True)
        
        start_step = time.time()
        
        # GỌI API RETAIN ĐÃ SỬA URL CHÍNH XÁC
        try:
            response = requests.post(
                f"{BASE_URL}/banks/{bank_id}/memories", # URL CHÍNH XÁC
                json={
                    "items": [{"content": transcript}], 
                    "async": False
                },
                timeout=1800 # Chờ tối đa 10 phút cho mỗi session
            )
            
            duration = time.time() - start_step
            
            if response.status_code == 200:
                # Lấy stats hiện tại của Bank
                stats = requests.get(f"{BASE_URL}/banks/{bank_id}/stats", timeout=10).json()
                
                metric = {
                    "session": i + 1,
                    "duration": duration,
                    "nodes": stats['total_nodes'],
                    "links": stats['total_links']
                }
                session_metrics.append(metric)
                print(f" ✅ {duration:.1f}s (Nodes: {stats['total_nodes']})")
            else:
                print(f" ❌ Lỗi {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f" ❌ Request error: {e}")
        except json.JSONDecodeError:
            print(f" ❌ JSON Decode Error: Không thể parse phản hồi từ server.")
            
    total_duration = time.time() - start_total

    # 4. In báo cáo tổng kết
    print("\n" + "="*60)
    print(f"🏁 TỔNG KẾT CHI PHÍ XÂY DỰNG GRAPH")
    print("="*60)
    print(f"⏱️  Tổng thời gian: {total_duration/60:.2f} phút")
    print(f"📞 Số lần gọi LLM (Extraction): {len(sessions)}")
    
    try:
        final_stats = requests.get(f"{BASE_URL}/banks/{bank_id}/stats", timeout=10).json()
        json.dump(final_stats, open(f"final_stats_{bank_id}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\n🕸️  Thông số Graph cuối cùng:")
        print(f"   - Tổng số Nodes (Facts): {final_stats['total_nodes']}")
        print(f"   - Tổng số Links: {final_stats['total_links']}")
        print(f"   - Phân bổ mạng lưới: {json.dumps(final_stats['nodes_by_fact_type'], indent=2)}")
        
        avg_time = sum(m['duration'] for m in session_metrics) / len(session_metrics) if session_metrics else 0
        print(f"\n📈 Hiệu năng trung bình: {avg_time:.2f} giây/session")
    except Exception as e:
        print(f"❌ Không thể lấy final stats: {e}")

    print("="*60)

if __name__ == "__main__":
    analyze_hindsight_cost(12) # Chạy cho sample đầu tiên