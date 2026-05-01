import os

filepath = r"f:\ai-ml\agent-memory-cognitive\reports\final_reports\src\Chapter\3_Methodology.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_overview = r'''\section{3. Phương pháp đề xuất}

\subsection{3.1. Tổng quan Kiến trúc Hệ thống CogMem (Cognitive Memory)}

Để giải quyết triệt để các hạn chế của những hệ thống bộ nhớ hiện tại (như sự mất mát thông tin do nén, sự kém hiệu quả trong truy xuất đa bước và sự thiếu hụt cấu trúc nhận thức cốt lõi), nghiên cứu này đề xuất \textbf{CogMem} — một kiến trúc khép kín lấy cảm hứng từ cấu trúc giải phẫu thần kinh của não bộ (Cognitively-Grounded Architecture).

Kiến trúc tổng thể của CogMem được thiết kế với ba luồng xử lý chính (Pipelines), hoạt động tuần tự và tương tác trực tiếp với không gian Đồ thị Tri thức Dị thể (Heterogeneous Knowledge Graph):

\begin{enumerate}
    \item \textbf{Luồng Ghi nhớ (Retain Pipeline)}: Tiếp nhận luồng dữ liệu thô (raw dialogue/trajectory) từ người dùng. Quá trình chia làm hai pha chính: (1) Trích xuất thông tin (Fact Extraction) thành các loại Node đặc thù dựa trên LLM, đảm bảo việc đính kèm tệp văn bản nguyên bản (Lossless Metadata); (2) Xây dựng liên kết (Link Creation) để định hình mạng lưới nhân quả và các chuỗi cấu trúc thời gian.
    \item \textbf{Luồng Truy hồi (Recall Pipeline)}: Xử lý các câu hỏi hoặc ngữ cảnh truy vấn thông qua việc kích hoạt cơ chế \textit{Định tuyến ý định (Adaptive Query Routing)}. Pipeline này thực thi thuật toán Lan truyền Kích hoạt theo tổng (SUM Spreading Activation) trên đồ thị kết hợp với 3 cơ chế bảo vệ chu trình (Cycle Guards) nhằm thu tập nhiều luồng bằng chứng từ nhiều node bổ trợ.
    \item \textbf{Luồng Phản tư và Sinh văn bản (Reflect \& Synthesis Pipeline)}: Tổng hợp các Node được truy xuất thành công (top-K nodes) kết hợp với văn bản nguyên bản (raw snippets) để đưa vào Context Window, giúp LLM tổng hợp câu trả lời cuối cùng không bị ảo giác (Knowledge-grounded generation).
\end{enumerate}

Bốn đóng góp cốt lõi của phương pháp sẽ được ánh xạ vào các khâu xử lý trên và được trình bày chi tiết trong các tiểu mục tiếp theo.

\subsection{3.2. Đóng góp 1: Đồ thị Bộ nhớ Kế thừa Nhận thức (Cognitively-Grounded Memory Graph)}

\subsubsection{3.2.1. Nền tảng tâm lý}'''

content = content.replace(r'''\section{3. Phương pháp đề xuất}

\subsection{3.1. Đóng góp 1: Cognitively-Grounded Memory Graph (6 Networks + 7 Edge Types)}

\subsubsection{3.1.1. Nền tảng tâm lý}''', new_overview)

# Shift subsequent subsections
content = content.replace(r"\subsubsection{3.1.2.", r"\subsubsection{3.2.2.")
content = content.replace(r"\subsubsection{3.1.3.", r"\subsubsection{3.2.3.")
content = content.replace(r"\subsubsection{3.1.4.", r"\subsubsection{3.2.4.")

content = content.replace(r"\subsection{3.2. Đóng góp 2:", r"\subsection{3.3. Đóng góp 2:")
content = content.replace(r"\subsubsection{3.2.1.", r"\subsubsection{3.3.1.")
content = content.replace(r"\subsubsection{3.2.2.", r"\subsubsection{3.3.2.")

content = content.replace(r"\subsection{3.3. Đóng góp 3:", r"\subsection{3.4. Đóng góp 3:")
content = content.replace(r"\subsubsection{3.3.1.", r"\subsubsection{3.4.1.")
content = content.replace(r"\subsubsection{3.3.2.", r"\subsubsection{3.4.2.")
content = content.replace(r"\subsubsection{3.3.3.", r"\subsubsection{3.4.3.")

content = content.replace(r"\subsection{3.4. Đóng góp 4:", r"\subsection{3.5. Đóng góp 4:")
content = content.replace(r"\subsubsection{3.4.1.", r"\subsubsection{3.5.1.")
content = content.replace(r"\subsubsection{3.4.2.", r"\subsubsection{3.5.2.")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated chapter 3 successfully")
