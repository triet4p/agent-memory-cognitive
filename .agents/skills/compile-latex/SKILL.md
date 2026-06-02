---
name: compile-latex
description: Compile LaTeX code into a PDF document.
---

## Overview
The `compile-latex` skill allows you to compile LaTeX code into a PDF document. You can provide the LaTeX code as input, and the skill will return the compiled PDF file.

## How to Use
To use the `compile-latex` skill, you can use this bash script in `PowerShell`:

```powershell
$ cd F:/ai-ml/agent-memory-cognitive/reports/final_reports/src; & "F:/MikTeX/miktex/bin/x64/pdflatex.exe" -synctex=1 -interaction=nonstopmode main.tex 2>&1
```

Then, read log and check if the compilation was successful. If there are errors, they will be displayed in the log output.

If any error or warning occurs, please fix the LaTeX code and try compiling again until it compiles successfully. Once the compilation is successful, you will find the generated PDF file in the same directory as your LaTeX source file.

