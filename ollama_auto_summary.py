import subprocess
import textwrap

LECTURE_PATH = r"C:\Users\gaara\AppData\Local\Programs\Python\Python310\TC_PROJECT1\lecture.txt"
SUMMARY_PATH = r"C:\Users\gaara\AppData\Local\Programs\Python\Python310\TC_PROJECT1\summary.txt"

def summarize(text):
    prompt = f"""
Summarize the following classroom lecture into
clear, exam-oriented bullet points:

{text}
"""
    result = subprocess.run(
    ["ollama", "run", "phi"],
    input=prompt,
    text=True,
    encoding="utf-8",     # ✅ FORCE UTF-8
    errors="ignore",      # ✅ IGNORE BAD BYTES
    capture_output=True
)

    
    return result.stdout.strip()

with open(LECTURE_PATH, "r", encoding="utf-8") as f:
    lecture = f.read()

chunks = textwrap.wrap(lecture, 1500)

final_summary = ""
for chunk in chunks:
    final_summary += summarize(chunk) + "\n\n"

with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
    f.write(final_summary)

print("✅ Summary saved to summary.txt")
