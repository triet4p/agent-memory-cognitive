import os

appendix_A = r'''\documentclass[../main.tex]{subfiles}
\usepackage{tcolorbox}
\begin{document}

\section{Phụ lục A: Các Prompt Trích xuất Tri thức (Retain Pipeline)}

Phụ lục này trình bày chi tiết các Prompt cốt lõi được sử dụng trong hệ thống CogMem để giao tiếp với Mô hình Ngôn ngữ Lớn (LLM) trong luồng xử lý Retain (Ghi nhớ). Các Prompt này đóng vai trò quyết định trong việc chuyển đổi ngôn ngữ tự nhiên thành đồ thị tri thức có cấu trúc cụ thể.

\subsection{A.1. Prompt Trích xuất Pass 1 (Fact Extraction)}

Được sử dụng ở bước đầu tiên của luồng Retain, cấu trúc này ép LLM phân loại đầu vào thành một trong 6 loại mạng bộ nhớ (World, Experience, Opinion, Habit, Intention, Action-Effect) và ràng buộc đầu ra thành đối tượng JSON hợp lệ. Việc chia rõ 6 loại Node là xương sống của kiến trúc tiếp theo.

\begin{tcolorbox}[title=System Prompt: Pass 1 Fact Extraction, colback=gray!5!white, colframe=black!75!black, text width=\textwidth, nobeforeafter]
\small
\begin{verbatim}
You are a memory extraction assistant. Extract durable facts from 
conversations for long-term storage.

OUTPUT RULE: Respond ONLY with valid JSON — no prose, no markdown 
fences. Format: {"facts": [<fact>, ...]}  or  {"facts": []} if 
nothing to store.

EVERY fact MUST have these REQUIRED fields:
- "fact_type": one of: world | experience | opinion | habit | 
  intention | action_effect
- "what": core statement, under 80 words — must include: WHO did 
  WHAT to/with WHAT OBJECT.
- "entities": ALL named entities — people, places, orgs, tech 
  tools, product names. e.g. ["Alice","Tamiya","Spitfire Mk.V"].

FACT TYPE GUIDE:
1. "world" — objective fact, not time-bound: job, role, skill.
2. "experience" — USER's personal past event at a specific time.
3. "opinion" — belief or preference; add "confidence": 0.0-1.0.
4. "habit" — repeating behavior; triggers: always, usually, every day.
5. "intention" — future plan or goal; add "intention_status": 
   "planning"|"fulfilled"|"abandoned".
6. "action_effect" — causal relationship (A causes B). Add 
   "precondition", "action", "outcome", "devalue_sensitive".
\end{verbatim}
\end{tcolorbox}

\subsection{A.2. Prompt Tinh chỉnh Pass 2 (Persona-Focused Revision)}

Được sử dụng ngay sau Pass 1 để lọc bỏ các thông tin rác sinh ra bởi LLM hallucination và tinh chỉnh góc nhìn của Agent về User (User-centric alignment). Điều này giải quyết các hiện tượng Agent tự đánh giá và lưu trữ ký ức về chính bản thân nó thay vì User.

\begin{tcolorbox}[title=System Prompt: Pass 2 Persona-Focused, colback=gray!5!white, colframe=black!75!black, text width=\textwidth, nobeforeafter]
\small
\begin{verbatim}
You are a memory refinement assistant. Your task is to filter and 
rewrite raw facts to ensure they STRICTLY capture the USER's long-term 
persona, history, and preferences.

OUTPUT RULE: Respond ONLY with valid JSON — no prose, no markdown 
fences. Format: {"facts": [<fact>, ...]} or {"facts": []}.

RULES:
1. DELETE generic conversational filler, AI system prompts, and 
   temporary state updates.
2. DELETE assistant actions (e.g. "Assistant summarized the meeting").
3. REWRITE facts to be User-centric. If it's about the USER doing, 
   liking, or knowing something, kept it. If it's about the Assistant, 
   drop it.
4. ENSURE fact_type is only one of: world | experience | opinion | 
   habit | intention | action_effect.
\end{verbatim}
\end{tcolorbox}

\end{document}
'''

appendix_B = r'''\documentclass[../main.tex]{subfiles}
\usepackage{tcolorbox}
\begin{document}

\section{Phụ lục B: Các Prompt Dành cho Đánh giá (Evaluation \& Reflection)}

Phụ lục này cung cấp các Prompt liên quan đến quá trình tổng hợp thông tin sinh câu trả lời (Reflection pipeline) và các Prompt đánh giá tự động (LLM-as-a-Judge) dùng cho tập test LongMemEval-S và LoCoMo.

\subsection{B.1. Prompt Tổng hợp Câu trả lời (Reflection \& Generation)}

Prompt này nhận đầu vào là các khối bằng chứng (Evidence/Raw Snippets) truy xuất được từ Đồ thị CogMem và ép LLM trả lời nghiêm ngặt dựa trên dữ liệu đồ thị có thật để chống lại hiện tượng ảo giác (hallucination) thường thấy.

\begin{tcolorbox}[title=System Prompt: Answer Generation, colback=gray!5!white, colframe=black!75!black, text width=\textwidth, nobeforeafter]
\small
\begin{verbatim}
You are an AI assistant designed to answer the user's latest query 
using ONLY the provided long-term memory evidence.

EVIDENCE RULES:
1. Base your answer COMPLETELY on the text listed under [EVIDENCE].
2. If the [EVIDENCE] contradicts your internal knowledge, you MUST 
   trust the [EVIDENCE].
3. DO NOT state "Based on the evidence..." or 
   "The text provided says...". Respond directly.
4. If the evidence does not contain the answer, say exactly: 
   "I do not have enough specific memory to answer this question."

<--- BEGIN EVIDENCE --->
{evidence}
<--- END EVIDENCE --->
\end{verbatim}
\end{tcolorbox}

\subsection{B.2. Prompt Chấm điểm Tự động (LLM-as-a-Judge)}

Được dùng trong tập script benchmark để tự động tính điểm từ .0$ đến .0$. Prompt này có quy tắc ưu tiên không phạt lỗi ngoại lệ lệch 1 đơn vị ngày/tháng với các câu hỏi chuỗi thời gian (temporal reasoning).

\begin{tcolorbox}[title=System Prompt: LLM Judge (Temporal Focus), colback=gray!5!white, colframe=black!75!black, text width=\textwidth, nobeforeafter]
\small
\begin{verbatim}
You are an evaluation judge for a memory system.
I will give you a question, a correct answer, and a model response.

Score rubric (0.0-1.0):
- 1.0: correct and complete.
- 0.7-0.9: correct but slightly rephrased or minor detail missing.
- 0.3-0.6: partially correct — right topic but missing key facts, 
  wrong count, or hedged answer.
- 0.0-0.2: wrong, fabricated, or completely missing the answer.

SPECIAL RULE FOR TEMPORAL QUESTIONS:
Do NOT penalize off-by-one errors for counts of days, weeks, 
or months (e.g., answering "18 days" when the label is "19 days" 
is still scored 1.0).

OUTPUT FORMAT:
Respond ONLY with a JSON object.
{"score": <float between 0.0 and 1.0>, "reason": "<string>"}
\end{verbatim}
\end{tcolorbox}

\end{document}
'''

dirs = [
    r"f:\ai-ml\agent-memory-cognitive\reports\final_reports\src\Chapter",
    r"f:\ai-ml\agent-memory-cognitive\final_reports\src\Chapter"
]

for d in dirs:
    a_path = os.path.join(d, "Appendix_A.tex")
    b_path = os.path.join(d, "Appendix_B.tex")
    
    if os.path.exists(d):
        with open(a_path, "w", encoding="utf-8") as f:
            f.write(appendix_A)
        with open(b_path, "w", encoding="utf-8") as f:
            f.write(appendix_B)
        print(f"Updated Appendices in {d}")
    else:
        print(f"Directory {d} does not exist.")

