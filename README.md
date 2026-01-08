**Realtime Lecture Transcription & AI Summarization**

This is a simple Python-based project that records classroom lectures using a microphone, converts speech to text in real time, saves the transcription to a file, and then generates an AI-based summary completely offline. The entire system is free to use, does not require any API keys, and works on CPU-only systems.

The project is designed mainly for students to help with lecture note-taking and quick revision.

---

**System Requirements**

* Windows 10 or Windows 11
* A working microphone
* Internet connection only for first-time installation

---

**Python Version**

* Python 3.10 or higher
* Tested on Python 3.10.11 (64-bit)

---

**Libraries and Tools Used**

Python libraries:

* RealtimeSTT – for real-time speech-to-text transcription
* torch – backend required for speech models
* sounddevice – to access microphone input
* subprocess – to run Ollama from Python
* textwrap – to split large text into chunks
* Standard Python libraries such as os and threading

External software:

* Ollama – a free, local AI model runner used for summarization

---

**How to Install Python and pip**

1. Download Python from:
   [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. During installation, make sure to select:
   “Add Python to PATH”

3. Verify Python installation:

   ```
   python --version
   ```

pip usually comes bundled with Python. To check:

```
pip --version
```

If pip is missing:

```
python -m ensurepip --upgrade
```

---

**How to Install Required Libraries**

### Recommended: Use a Virtual Environment
To avoid system conflicts (externally-managed-environment error), use a virtual environment:

```bash
# 1. Create the virtual environment
python3 -m venv venv

# 2. Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 3. Install system dependencies (Required for PyAudio)
# sudo apt install portaudio19-dev

# 4. Install libraries inside the venv
pip install streamlit RealtimeSTT torch sounddevice pydub faster-whisper scipy
```

---

**How to Install Ollama**

1. Download Ollama from:
   [https://ollama.com](https://ollama.com)

2. Install it and restart your PC.

3. Verify installation:

   ```
   ollama --version
   ```

4. Download a lightweight AI model (recommended for CPU systems):

   ```
   ollama pull phi
   ```

This is a one-time setup.

---

**How to Run the Project**

To run the complete workflow (transcription + summarization) using a single command:

```
python run_all.py
```

---

**Workflow Explanation**

1. The microphone listens to the lecture audio.
2. RealtimeSTT converts speech into text in real time.
3. The full transcription is saved to a file called `lecture.txt`.
4. Ollama reads the text locally using a small AI model.
5. A summarized version of the lecture is generated and saved as `summary.txt`.

In short:
Microphone → RealtimeSTT → lecture.txt → Ollama (local AI) → summary.txt

---

**Project Structure**

```
TC_PROJECT1/
├── run_all.py
├── ollama_auto_summary.py
├── lecture.txt
├── summary.txt
├── .gitignore
└── README.md
```

---

**Notes**

* The first run may take longer because models are downloaded.
* Clear speech with small pauses gives the best transcription results.
* The summarization quality depends on how clear the lecture audio is.

---

**License**

This project is intended for educational and personal learning purposes.

---

