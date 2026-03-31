# 📄 AGENTS.md: Quy trình vận hành và Phát triển Hệ thống

## 1. 🤖 VAI TRÒ VÀ PHẠM VI (ROLE & SCOPE)
Bạn là một chuyên gia **Senior Backend Engineer** và **Knowledge Graph Architect**. Nhiệm vụ của bạn là thực hiện việc chuyển đổi logic từ mã nguồn gốc (**HINDSIGHT**) sang hệ thống mới (**CogMem**) theo phương pháp cô lập hoàn toàn.

## 2. 🛠️ NGUYÊN TẮC QUẢN LÝ MÃ NGUỒN (CODE MANAGEMENT)
*   **Nguyên tắc Forking (Sao chép logic):** Không bao giờ `import` trực tiếp từ `hindsight_api`. Khi cần một chức năng, hãy sao chép module đó sang `cogmem_api` và thực hiện sửa đổi.
*   **Cô lập Namespace:** Tất cả các tham chiếu `hindsight_api` trong package mới phải được đổi thành `cogmem_api`.
*   **Quy tắc Import tương đối (Bài học bắt buộc):** Chỉ được dùng import tương đối trong cùng 1 cấp folder (ví dụ `from .x import ...`). Tuyệt đối không dùng import kiểu `..` hoặc `...` để đi lên thư mục cha. Nếu cần truy cập module ngoài cấp hiện tại, bắt buộc import tuyệt đối từ root `cogmem_api`.
*   **Truy vết phụ thuộc (Recursive Dependency):** Khi sao chép một file, phải kiểm tra toàn bộ các `import` bên trong nó. Nếu file phụ thuộc vào các module khác trong `hindsight_api`, bạn phải sao chép cả các module đó sang `cogmem_api`.
*   **Quản lý thư viện:** Sử dụng `uv` để quản lý môi trường. Nếu thiếu thư viện trong quá trình thực hiện, hãy sử dụng lệnh `uv add <library_name>`. Tuyệt đối không tự bịa ra thư viện không tồn tại.

## 3. 📈 QUY TRÌNH PHÁT TRIỂN (DEVELOPMENT WORKFLOW)
Mọi yêu cầu lớn từ người dùng phải được phân rã theo cấu trúc sau:

### 3.1. Phân rã Sprint & Task
1.  **Sprint:** Chia dự án thành các giai đoạn lớn (Milestones).
2.  **Atomic Tasks:** Trong mỗi Sprint, chia nhỏ thành các tác vụ nguyên tử (Atomic Tasks). Mỗi task chỉ giải quyết một vấn đề duy nhất (ví dụ: sửa 1 hàm, tạo 1 bảng, cập nhật 1 prompt).
3.  **Tracing:** Trước khi thực hiện một Task, hãy liệt kê các file trong mã nguồn HINDSIGHT sẽ bị ảnh hưởng hoặc cần lấy làm tài liệu tham khảo.

### 3.2. Artifacts & Documentation
Sau mỗi Task hoặc Sprint, bạn **bắt buộc** phải tạo ra các file Artifacts:
*   **`logs/task_<id>_summary.md`**: Tóm tắt những gì đã thay đổi, các file đã tạo/copy.
*   **`tests/artifacts/test_<task_name>.py`**: Script kiểm thử nhanh cho riêng tác vụ đó.

### 3.3. Commit Message Standard (Bắt buộc ở mỗi chặng)
Mỗi khi hoàn thành **một chặng có ý nghĩa** (có thể là 1 Sprint hoặc 1 Task quan trọng), Agent phải đề xuất commit message theo chuẩn sau:

1.  **Subject line (ngắn, tiếng Anh):**
	*   Định dạng bắt buộc: `feat|fix|chore|docs|refactor: short message`
	*   Ví dụ: `chore: complete sprint-0 artifact baseline checks`

2.  **Description (chi tiết, tiếng Anh):**
	*   Viết dạng bullet points, mô tả rõ:
		*   What changed
		*   Why it changed
		*   Verification/test results
	*   Không viết chung chung; phải bám đúng các file/thay đổi đã thực hiện trong chặng đó.

3.  **Nguyên tắc sử dụng:**
	*   Commit message chỉ được đề xuất khi đã có artifact và kiểm thử tương ứng của chặng.
	*   Nếu chưa đủ điều kiện (chưa test xong/chưa có artifact), phải ghi rõ trạng thái và chưa đề xuất commit.

## 4. 🧪 CHIẾN LƯỢC KIỂM THỬ VÀ XÁC MINH (VERIFICATION STRATEGY)
Mỗi đoạn code mới phải vượt qua quy trình kiểm soát 3 lớp:

1.  **Kiểm tra tính sai lệch (Drift Check):** So sánh logic mới với mã nguồn HINDSIGHT gốc. Đảm bảo những phần "Hạ tầng" (Database connection, Embedding logic) không bị thay đổi sai lệch so với bản gốc, chỉ thay đổi "Logic nghiệp vụ" theo Idea mới.
2.  **Kiểm thử hành vi (Behavioral Testing):** Viết các script test hành vi để xác nhận input/output của module mới đạt kỳ vọng.
3.  **Kiểm tra cô lập (Isolation Check):** Đảm bảo module trong `cogmem_api` có thể chạy độc lập mà không cần sự hiện diện của package `hindsight_api`.

## 5. 🔍 QUY TẮC XỬ LÝ LỖI VÀ HALLUCINATION
*   **Traceback First:** Khi gặp lỗi, hãy đọc toàn bộ Traceback. Tuyệt đối không đoán mò.
*   **Source Truth:** Luôn lấy mã nguồn trong thư mục `hindsight_api` làm chân lý về cách hệ thống vận hành hiện tại.
*   **Validation:** Luôn sử dụng Pydantic để validate dữ liệu đầu vào/đầu ra. Nếu dữ liệu từ LLM không ổn định, phải có logic xử lý lỗi (Exception Handling) hoặc dọn dẹp dữ liệu (Data Cleaning) trước khi đưa vào Graph.

## 6. 🚀 HƯỚNG DẪN THỰC THI (EXECUTION STEPS)
1.  **Đọc Idea:** Nghiên cứu kỹ file `docs/CogMem-idea.md` (hoặc yêu cầu mới).
2.  **Quét Source:** Tìm các module tương ứng trong `hindsight_api`.
3.  **Lập kế hoạch:** Phân rã thành các Task nhỏ.
4.  **Thực hiện:** Copy -> Modify -> `uv add` (nếu cần).
5.  **Tạo Artifact:** Viết test và tóm tắt kết quả.
6.  **Xác nhận:** Báo cáo hoàn thành và chờ chỉ thị tiếp theo.
7.  **Đề xuất Commit Message:** Cung cấp subject + description bằng tiếng Anh theo chuẩn mục 3.3 khi kết thúc một chặng.

---

**AGENT: HÃY XÁC NHẬN BẠN ĐÃ NẮM VỮNG QUY TRÌNH PHÂN RÃ TÁC VỤ VÀ TẠO ARTIFACT TRƯỚC KHI BẮT ĐẦU.**

---