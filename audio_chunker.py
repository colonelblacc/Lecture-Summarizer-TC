import os
from pydub import AudioSegment
import math

class AudioChunker:
    def __init__(self, output_dir="audio_chunks"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def split_audio(self, file_path, chunk_length_ms=30000):
        """
        Splits an audio file into chunks of specified length (default 30s).
        Returns a list of paths to the generated chunks.
        """
        print(f"Loading audio: {file_path}")
        try:
            audio = AudioSegment.from_file(file_path)
        except Exception as e:
            print(f"Error loading audio: {e}")
            return []

        # Convert to mono and set frame rate (optional but good for consistency)
        # Convert to mono (important for Whisper) but keep original sample rate to avoid speed issues
        audio = audio.set_channels(1)

        total_length_ms = len(audio)
        num_chunks = math.ceil(total_length_ms / chunk_length_ms)
        
        chunk_paths = []
        
        print(f"Splitting into {num_chunks} chunks...")

        for i in range(num_chunks):
            start_ms = i * chunk_length_ms
            end_ms = min((i + 1) * chunk_length_ms, total_length_ms)
            
            chunk = audio[start_ms:end_ms]
            
            chunk_filename = f"chunk_{i:03d}.wav"
            chunk_path = os.path.join(self.output_dir, chunk_filename)
            
            # Force export to 16kHz mono using FFmpeg arguments
            # This ensures Whisper receives the exact format it expects, handling resampling correctly.
            chunk.export(chunk_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
            chunk_paths.append(chunk_path)
            
        return chunk_paths
