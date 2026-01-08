import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np

DURATION = 25# seconds
RATE = 16000  # Hz
OUTPUT = "test_mic.wav"

print(f"Recording for {DURATION} seconds... Speak now!")
try:
    recording = sd.rec(int(DURATION * RATE), samplerate=RATE, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    print("Recording finished.")
    
    # Check if there is actual sound (not just silence)
    max_amp = np.max(np.abs(recording))
    print(f"Peak Amplitude: {max_amp:.4f}")
    if max_amp < 0.01:
        print("WARNING: Recording seems nearly silent.")
    else:
        print("Audio detected!")

    wav.write(OUTPUT, RATE, recording)
    print(f"Saved to {OUTPUT}")
    
except Exception as e:
    print(f"Recording failed: {e}")
