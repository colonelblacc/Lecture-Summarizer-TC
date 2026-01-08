import sys
import os

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster_whisper not found. Please install it.")
    sys.exit(1)

def transcribe(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    # Load model (optimized for CPU int8)
    try:
        model = WhisperModel("small", device="cpu", compute_type="int8")
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

        # Force English. 
        # DISABLED VAD filter because it was cutting off parts of the audio in short clips.
        segments, info = model.transcribe(
            file_path, 
            beam_size=10, 
            language="en"
        )
        
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
            
        print(full_text.strip())
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe_worker.py <audio_file>")
        sys.exit(1)
        
    audio_file = sys.argv[1]
    transcribe(audio_file)
