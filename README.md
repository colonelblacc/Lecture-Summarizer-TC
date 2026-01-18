# Robust Lecture Summarizer

A local, offline AI-powered lecture summarization tool. It records audio, transcribes it using Whisper, and generates concise notes using local LLMs (via Ollama).

## Features
- **Local Processing**: Values privacy and works offline.
- **Batch Processing**: Handles long recordings by splitting them into chunks.
- **Crash Resilience**: Saves progress after every batch; can resume if interrupted.
- **Interactive UI**: Built with Streamlit for easy recording and management.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.10+** installed.
- **Ollama** installed and running (for summarization).
  - Download: [ollama.com](https://ollama.com)
  - Pull the model: `ollama pull phi` (or any other model you prefer)

### 2. Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/colonelblacc/Lecture-Summarizer-TC.git
    cd Lecture-Summarizer-TC
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    # System dependency for audio (Linux only)
    # sudo apt-get install portaudio19-dev

    pip install -r requirements.txt
    ```

### 3. Running the App

Run the Streamlit application:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`.

---

## 📂 Project Structure

- `app.py`: Main Streamlit application UI.
- `batch_processor.py`: Orchestrates chunking, transcription, and summarization.
- `recorder_process.py`: Handles audio recording in a separate process for stability.
- `transcribe_worker.py`: Helper script for transcribing audio files.
- `audio_chunks/`: Temporary storage for audio processing.
- `transcripts/`: Intermediate transcription files.
- `summaries/`: Intermediate summary files.
- `recording.wav`: Raw audio recording.
- `final_notes.txt`: Final compiled lecture notes.

## 🛠 Troubleshooting

- **Audio Input Error**: Ensure your microphone is accessible and not used by another app.
- **Microphone not found on Linux**: Install PortAudio: `sudo apt-get install portaudio19-dev python3-pyaudio`.
- **Ollama Error**: Make sure Ollama is running in the background (`ollama serve`) and you have pulled the `phi` model.

## License
MIT
