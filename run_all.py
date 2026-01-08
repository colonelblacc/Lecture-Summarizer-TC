print("Starting...")


import subprocess
import os
from RealtimeSTT import AudioToTextRecorder


BASE_DIR = r"C:\Users\gaara\AppData\Local\Programs\Python\Python310\TC_PROJECT1"
LECTURE_FILE = os.path.join(BASE_DIR, "lecture.txt")

def record_lecture():
    print("🎤 Recording lecture...")
    print("Press ENTER to stop.\n")

    recorder = AudioToTextRecorder(
        device="cpu",
        model="small",
        compute_type="int8",
        input_device_index=1,
        spinner=True
    )

    recorder.start()
    input()
    recorder.stop()

    text = recorder.text()

    with open(LECTURE_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ Lecture saved.\n")

def summarize_lecture():
    print("🧠 Generating summary using Ollama...\n")
    subprocess.run(
        ["python", "ollama_auto_summary.py"],
        cwd=BASE_DIR
    )
    print("✅ Summary generated.\n")

if __name__ == "__main__":
    record_lecture()
    summarize_lecture()
    print("🎉 All done! Check lecture.txt and summary.txt")
