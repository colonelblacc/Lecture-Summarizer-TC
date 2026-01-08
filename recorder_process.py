import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import sys
import signal
import time

# Global state
recording_active = True
recorded_frames = []

def signal_handler(sig, frame):
    """Handle termination signals to save the file gracefully."""
    global recording_active
    print("Signal received, stopping...")
    recording_active = False

def record_process(device_index, filename, samplerate=44100):
    global recording_active
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Use default samplerate if 0 or None, or request 16000 but accept whatever the device enforces
        # Setting samplerate=None allows sounddevice to pick the device's native rate (e.g. 44100 or 48000)
        # This prevents the "Chipmunk" effect (pitch shift).
        with sd.InputStream(samplerate=None, device=device_index, channels=1, dtype='float32') as stream:
            actual_samplerate = int(stream.samplerate)
            print(f"Recording started at {actual_samplerate}Hz.")
            sys.stdout.flush() 
            
            while recording_active:
                data, overflow = stream.read(4096)
                if overflow:
                    print("Overflow warning", file=sys.stderr)
                recorded_frames.append(data.copy())
    except Exception as e:
        print(f"Error in stream: {e}", file=sys.stderr)
    
    print("Saving file...")
    if recorded_frames:
        full_data = np.concatenate(recorded_frames, axis=0)
        # Convert to 16-bit PCM
        data_int16 = (full_data * 32767).clip(-32768, 32767).astype(np.int16)
        
        # Write with the ACTUAL rate
        wav.write(filename, actual_samplerate, data_int16)
        print(f"Saved {len(data_int16)} samples to {filename} at {actual_samplerate}Hz")
    else:
        print("No data recorded.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python recorder_process.py <device_index> <output_filename>")
        sys.exit(1)
        
    dev_idx = int(sys.argv[1])
    # Handle 'None' or invalid inputs gently if needed, but app should send valid int
    
    out_file = sys.argv[2]
    
    record_process(dev_idx, out_file)
