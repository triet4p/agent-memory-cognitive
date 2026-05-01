import os
import re

def fix_latex_file(filepath):
    if not os.path.exists(filepath):
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace unicode characters
    content = content.replace("★", "$\\star$")
    content = content.replace("≥", "$\\geq$")
    content = content.replace("θ", "$\\theta$")
    content = content.replace("≈", "$\\approx$")

    # The error "File ended while scanning use of \@xdblarg" often comes from unmatched braces in \caption or \textbf or \section
    # The error "Missing } inserted. \end{center}"
    # Let's write a regex to replace unescaped underscores outside of math/verbatim
    # Actually, it's easier to just replace specific words:
    words = [
        "raw_snippet", "narrative_fact", "network_type", "action_effect", 
        "linked_experience", "fulfilled_at", "devalue_sensitive", "observation_count",
        "O(N^2)"
    ]
    for w in words:
        if w == "O(N^2)":
            content = content.replace("O(N^2)", "(N^2)$")
            # careful not to double wrap
            content = content.replace("30O(N^2)30", "(N^2)$")
        else:
            w_esc = w.replace("_", r"\_")
            # Replace the word if it doesn't already have a backslash
            # A simple way is to replace all occurrences, then fix double backslashes
            content = content.replace(w, w_esc)
            content = content.replace("\\" + w_esc, w_esc) # in case it was already escaped

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Fixed {filepath}")

chapters_dir = r"f:\ai-ml\agent-memory-cognitive\reports\final_reports\src\Chapter"
for filename in os.listdir(chapters_dir):
    if filename.endswith(".tex"):
        fix_latex_file(os.path.join(chapters_dir, filename))

