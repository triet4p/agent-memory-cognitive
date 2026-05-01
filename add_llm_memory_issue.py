import os

filepath = r"f:\ai-ml\agent-memory-cognitive\reports\final_reports\src\Chapter\2_Literature_review.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_section = r'''\subsection{2.1. Thách thức cốt lõi về Bộ nhớ của Mô hình Ngôn ngữ Lớn (LLMs)}

Mặc dù các Mô hình Ngôn ngữ Lớn (LLMs) đạt được nhiều thành tựu vượt bậc trong xử lý ngôn ngữ tự nhiên, chúng vẫn tồn tại những giới hạn bản chất về mặt kiến trúc liên quan đến khả năng duy trì bộ nhớ dài hạn:

\begin{itemize}
    \item \textbf{Giới hạn Cửa sổ Ngữ cảnh (Context Window Bottleneck) và Chi phí (N^2)$}: Cơ chế Self-Attention cốt lõi của kiến trúc Transformer đòi hỏi độ phức tạp tính toán và bộ nhớ tăng theo bình phương độ dài chuỗi đầu vào ((N^2)$). Điều này khiến việc đưa toàn bộ lịch sử hội thoại dài hạn vào prompt (context stuffing) trở nên bất khả thi về mặt tài nguyên phần cứng và làm tăng độ trễ nội tại.
    \item \textbf{Hiện tượng "Trôi dạt ở giữa" (Lost-in-the-Middle Phenomenon)}: Nghiên cứu của Liu et al. (2023) chỉ ra rằng LLMs có xu hướng trích xuất thông tin xuất hiện ở đầu và cuối cửa sổ ngữ cảnh tốt hơn nhiều so với thông tin nằm ở đoạn giữa. Việc nhồi nhét quá nhiều lịch sử hội thoại sẽ làm nhiễu loạn luồng chú ý (attention drift), dẫn đến bỏ sót dữ kiện quan trọng.
    \item \textbf{Quên thảm khốc (Catastrophic Forgetting)}: Phương pháp tinh chỉnh (Fine-tuning) để mô hình học thông tin mới thường dẫn đến việc nó bị ghi đè và đánh mất các kiến thức cơ sở đã học trong quá trình pre-training. Việc tinh chỉnh cũng không tương thích với bối cảnh bộ nhớ người dùng cần được cập nhật liên tục (real-time stream).
    \item \textbf{Ảo giác (Hallucination) do thiếu cơ sở nối kết (Grounding)}: LLM sinh văn bản dựa trên xác suất chuỗi phân phối tuyến tính thay vì suy luận từ hệ thống gốc (knowledge-grounded). Khi không có cấu trúc tri thức neo giữ, hệ thống dễ dàng tạo ra các sự thật giả tạo học được từ trọng số lưu trữ ngầm.
\end{itemize}

Để giải quyết các rào cản này, sự chuyển dịch từ việc phụ thuộc vào \textit{Context Window} sang các hệ thống \textit{Bộ nhớ Dài hạn bên ngoài (External Long-term Memory)} là xu thế bắt buộc. Tuy nhiên, để xây dựng hệ thống tác nhân toàn diện, chúng ta cần vay mượn cơ sở lý thuyết từ Khoa học nhận thức.

\subsection{2.2. Cơ sở Lý thuyết: Khoa học Nhận thức và Đồ thị Tri thức}

\subsubsection{2.2.1'''

# Replace the heading 2.1 to shift everything down by 0.1
content = content.replace(r"\subsection{2.1. Cơ sở Lý thuyết: Khoa học Nhận thức và Đồ thị Tri thức}", new_section)
content = content.replace(r"\subsubsection{2.1.1.", r"\subsubsection{2.2.1.")
content = content.replace(r"\subsubsection{2.1.2.", r"\subsubsection{2.2.2.")
content = content.replace(r"\subsection{2.2. Tiến trình phát triển", r"\subsection{2.3. Tiến trình phát triển")
content = content.replace(r"\subsubsection{2.2.1.", r"\subsubsection{2.3.1.")
content = content.replace(r"\subsubsection{2.2.2.", r"\subsubsection{2.3.2.")
content = content.replace(r"\subsubsection{2.2.3.", r"\subsubsection{2.3.3.")
content = content.replace(r"\subsection{2.3. Điểm chuẩn kiểm", r"\subsection{2.4. Điểm chuẩn kiểm")
content = content.replace(r"\subsubsection{2.3.1.", r"\subsubsection{2.4.1.")
content = content.replace(r"\subsubsection{2.3.2.", r"\subsubsection{2.4.2.")
content = content.replace(r"\subsection{2.4. Hạn chế cốt lõi", r"\subsection{2.5. Hạn chế cốt lõi")


with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated successfully")
