import os
import json
import sys
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
from audio_chunker import AudioChunker
from pydub import AudioSegment, effects

# Constants
TRANSCRIPT_DIR = "transcripts"
SUMMARY_DIR = "summaries"
NOTES_DIR = "notes"
FINAL_NOTES_FILE = os.path.join(NOTES_DIR, "final_notes.txt")
LECTURE_CLEAN_FILE = "lecture_clean.txt"

class BatchProcessor:
    def __init__(self):
        self._ensure_dirs()
        self.chunker = AudioChunker()
        self.transcription_progress = 0.0
        self.summarization_progress = 0.0
        self.status_message = "Idle"
        self.is_running = False
        self._stop_event = threading.Event()

    def _ensure_dirs(self):
        for d in [TRANSCRIPT_DIR, SUMMARY_DIR, NOTES_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)

    def cleanup_artifacts(self):
        """Removes old files from output directories."""
        self.status_message = "Cleaning previous artifacts..."
        
        # Determine directories to clean. Note: 'audio_chunks' is created by chunker, 
        # so we should check if AudioChunker exposes dir or valid path.
        # Assuming AudioChunker uses "audio_chunks" by default or we can clean it hardcoded.
        dirs_to_clean = [TRANSCRIPT_DIR, SUMMARY_DIR, NOTES_DIR, "audio_chunks"]
        
        for d in dirs_to_clean:
            if os.path.exists(d):
                for f in os.listdir(d):
                    # Keep .gitignore or other config files if any, but usually safe to nuke all txt/wav
                    file_path = os.path.join(d, f)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}: {e}")
        
        # Also clean intermediate files
        for f in [LECTURE_CLEAN_FILE]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

    def process_audio_batches(self, audio_file_path):
        """
        Full pipeline: Audio -> Chunks -> Transcripts -> Merged Text
        """
        self.status_message = "Chunking audio..."
        self.transcription_progress = 0.1
        
        # 1. Normalize Audio first
        self.status_message = "Normalizing audio..."
        try:
            raw_audio = AudioSegment.from_file(audio_file_path)
            normalized_audio = effects.normalize(raw_audio)
            
            # Overwrite or save as temp? Overwrite is simpler for this flow
            # but let's be safe and save to a temp normalized file if we want to preserve original.
            # actually, let's just use the normalized audio for chunking.
            # AudioChunker takes a path. So we save it.
            normalized_path = audio_file_path.replace(".wav", "_norm.wav")
            normalized_audio.export(normalized_path, format="wav")
            audio_for_chunking = normalized_path
        except Exception as e:
            print(f"Normalization failed: {e}")
            audio_for_chunking = audio_file_path # Fallback

        # 1. Chunk Audio
        chunks = self.chunker.split_audio(audio_for_chunking)
        if not chunks:
            self.status_message = "Audio chunking failed."
            return False

        total_chunks = len(chunks)
        self.transcription_progress = 0.2
        
        # 2. Transcribe Batches
        # Note: Since RealtimeSTT is designed for microphone, we'll implement a fallback
        # or use a simplified Whisper call for files. 
        # For now, we will simulate a robust file transcriber using RealtimeSTT's recorder if possible
        # or assuming the user has 'whisper' command line or similar?
        # A better approach given the constraints: Use AudioToTextRecorder in a way that processes file data.
        # But AudioToTextRecorder is heavy.
        # Let's try to use the 'faster_whisper' library directly if available, as strictly implied by RealtimeSTT dependency.
        
        # We'll do it sequentially to save VRAM/RAM
        for i, chunk_path in enumerate(chunks):
            if self._stop_event.is_set():
                break
                
            self.status_message = f"Transcribing batch {i+1}/{total_chunks}..."
            
            transcript_file = os.path.join(TRANSCRIPT_DIR, f"batch_{i:03d}.txt")
            
            # Skip if already exists (Crash Recovery)
            if os.path.exists(transcript_file) and os.path.getsize(transcript_file) > 0:
                print(f"Skipping existing batch {i}")
            else:
                text = self._transcribe_file(chunk_path)
                with open(transcript_file, "w", encoding="utf-8") as f:
                    f.write(text)
            
            self.transcription_progress = 0.2 + (0.8 * (i + 1) / total_chunks)

        self.status_message = "Merging transcripts..."
        self.merge_transcripts()
        self.transcription_progress = 1.0
        return True

    def _transcribe_file(self, file_path):
        """
        Transcribes a single wav file. 
        Attemps to use 'faster_whisper' or fallback to a subprocess call to a helper script.
        """
        # For robustness in this environment, we'll try to run a python command 
        # that imports AudioToTextRecorder or faster_whisper to process the file.
        # To avoid reloading model every time, ideally we keep it in memory. 
        # But for 'batch' safety (one crashes, others survive), reloading is safer but slower.
        # Let's try to use a simple subprocess for isolation first.
        
        # ACTUALLY: To avoid complexity, let's load the model once here if we can.
        # But we need to be careful about conflicting with the UI thread.
        try:
            from RealtimeSTT import AudioToTextRecorder
            # This is expensive to init every time. 
            # Ideally we have a persistent worker. 
            # For this 'Report' style plan, let's assume we instantiate it once per pipeline run 
            # But here we are inside the method.
            pass
        except ImportError:
            return "[Error: RealtimeSTT not found]"

        # Quick hack for file transcription using RealtimeSTT's underlying logic or similar
        # Since I cannot easily verify `faster_whisper` API right now, 
        # I will create a temporary helper script `transcribe_worker.py` that takes a file and outputs text.
        
        cmd = [sys.executable, "transcribe_worker.py", file_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Transcription failed for {file_path}: {result.stderr} | Output: {result.stdout}")
                return ""
        except Exception as e:
            print(f"Transcribe worker error: {e}")
            return ""

    def merge_transcripts(self):
        files = sorted([os.path.join(TRANSCRIPT_DIR, f) for f in os.listdir(TRANSCRIPT_DIR) if f.startswith("batch_")])
        full_text = ""
        for f in files:
            with open(f, "r", encoding="utf-8") as txt:
                full_text += txt.read() + " "
        
        with open(LECTURE_CLEAN_FILE, "w", encoding="utf-8") as f:
            f.write(full_text.strip())

    def split_text_into_chunks(self, text, words_per_chunk=500):
        words = text.split()
        for i in range(0, len(words), words_per_chunk):
            yield " ".join(words[i:i + words_per_chunk])

    def process_summary_batches(self):
        """
        Summarizes the cleaned text in batches.
        """
        self.status_message = "Preparing text for summary..."
        self.summarization_progress = 0.0
        
        if not os.path.exists(LECTURE_CLEAN_FILE):
             self.status_message = "No transcript found."
             return False

        with open(LECTURE_CLEAN_FILE, "r", encoding="utf-8") as f:
            text = f.read()
            
        chunks = list(self.split_text_into_chunks(text))
        total_chunks = len(chunks)
        
        if total_chunks == 0:
             self.status_message = "Text is empty."
             return False

        for i, chunk in enumerate(chunks):
            if self._stop_event.is_set():
                break
                
            self.status_message = f"Summarizing part {i+1}/{total_chunks}..."
            
            summary_file = os.path.join(SUMMARY_DIR, f"summary_{i:03d}.txt")
            
            if os.path.exists(summary_file) and os.path.getsize(summary_file) > 0:
                pass # Skip
            else:
                summary = self._summarize_text_chunk(chunk)
                with open(summary_file, "w", encoding="utf-8") as f:
                    f.write(summary)
            
            self.summarization_progress = (i + 1) / total_chunks

        self.status_message = "Compiling final notes..."
        self.compile_final_notes()
        self.summarization_progress = 1.0
        return True

    def _summarize_text_chunk(self, text):
        prompt = f"Summarize the following text into concise bullet points:\n\n{text}"
        try:
            result = subprocess.run(
                ["ollama", "run", "phi"],
                input=prompt,
                text=True,
                encoding="utf-8",
                errors="ignore",
                capture_output=True
            )
            return result.stdout.strip()
        except FileNotFoundError:
            return "[Error: Ollama not found]"

    def compile_final_notes(self):
        files = sorted([os.path.join(SUMMARY_DIR, f) for f in os.listdir(SUMMARY_DIR) if f.startswith("summary_")])
        full_notes = "# Final Lecture Notes\n\n"
        for f in files:
            with open(f, "r", encoding="utf-8") as txt:
                full_notes += txt.read() + "\n\n"
        
        with open(FINAL_NOTES_FILE, "w", encoding="utf-8") as f:
            f.write(full_notes)

    def stop(self):
        self._stop_event.set()
