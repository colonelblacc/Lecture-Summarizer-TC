import streamlit as st
import os
import threading
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from batch_processor import BatchProcessor

# Page Config
st.set_page_config(page_title="Lecture Summarizer (Batch)", page_icon="🎙️")
st.title("🎙️ Robust Lecture Summarizer")

# Constants
RECORDING_FILE = "recording.wav"
FINAL_NOTES_FILE = "final_notes.txt"

# Session State
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'processor' not in st.session_state:
    st.session_state.processor = BatchProcessor()
if 'recording_data' not in st.session_state:
    st.session_state.recording_data = []
if 'processing_active' not in st.session_state:
    st.session_state.processing_active = False

# Sidebar
st.sidebar.header("Settings")

# Microphone Selection
devices = sd.query_devices()
input_devices = [f"{d['index']}: {d['name']}" for d in devices if d['max_input_channels'] > 0]
selected_device_str = st.sidebar.selectbox("Select Microphone", input_devices, index=0)
selected_device_index = int(selected_device_str.split(":")[0])

st.sidebar.header("Status")
status_placeholder = st.sidebar.empty()
progress_bar = st.sidebar.progress(0)
st.sidebar.markdown("---")
st.sidebar.write("Volume Level:")
volume_bar = st.sidebar.progress(0)

def update_status():
    status_placeholder.text(st.session_state.processor.status_message)
    # Simple average for visualization
    total_progress = (st.session_state.processor.transcription_progress + st.session_state.processor.summarization_progress) / 2
    progress_bar.progress(min(total_progress, 1.0))
    
    # Update volume meter if recording - DISABLED due to subprocess isolation
    # (Real-time volume from subprocess requires IPC which is overkill here)
    if st.session_state.recording:
        volume_bar.progress(0.5) # Just show it's active
    else:
        volume_bar.progress(0)

import signal
import subprocess

# Process Management
if 'recorder_pid' not in st.session_state:
    st.session_state.recorder_pid = None

def start_recording_subprocess():
    if st.session_state.recorder_pid is not None:
        return # Already running

    cmd = [sys.executable, "recorder_process.py", str(selected_device_index), RECORDING_FILE]
    
    # Clean up old recording to prevent stale state
    if os.path.exists(RECORDING_FILE):
        try:
            os.remove(RECORDING_FILE)
        except:
            pass
            
    try:
        # Start the process
        proc = subprocess.Popen(cmd)
        st.session_state.recorder_pid = proc.pid
        st.session_state.recording = True
        st.success(f"Recording started (PID: {proc.pid})")
    except Exception as e:
        st.error(f"Failed to start recorder: {e}")

def stop_recording_subprocess():
    pid = st.session_state.recorder_pid
    if pid is None:
        return

    try:
        os.kill(pid, signal.SIGTERM) # Send SIGTERM to allow graceful exit & saving
        
        # Wait a moment for file save
        with st.spinner("Saving audio file..."):
            time.sleep(2) 
            
        st.session_state.recorder_pid = None
        st.session_state.recording = False
        
        if os.path.exists(RECORDING_FILE):
             st.success(f"Saved to {RECORDING_FILE}")
        else:
             st.error("Recording file not found after stop.")

    except ProcessLookupError:
        st.warning("Recorder process was already gone.")
        st.session_state.recorder_pid = None
        st.session_state.recording = False
    except Exception as e:
        st.error(f"Error stopping: {e}")

# UI Layout

# 1. Capture Audio
st.header("1. Capture Audio")

# File Upload Option
uploaded_file = st.file_uploader("Upload an existing audio file (WAV/MP3)", type=["wav", "mp3"])

if uploaded_file is not None:
    # Save the uploaded file to the target path
    with open(RECORDING_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File uploaded! Ready to process.")

st.subheader("OR Record a new one")

col1, col2 = st.columns(2)

# Important: Streamlit re-runs scripts. We need a persistent stream. 
# Robust recording in Streamlit often requires a specific component or a simple "start/stop" that blocks (not ideal) 
# or using a background thread.
# For simplicity in this plan: We will use a Blocking Record for fixed duration OR a toggle that relies on re-runs.
# Re-run based recording is flaky.
# Let's use a meaningful "Record for X seconds" or "Start/Stop" that writes to a buffer.
# Actually, the simplest reliable way in Streamlit without custom components is to use an external recorder or `audio_recorder_streamlit`.
# But we can't install new UI components easily.
# We will trust the user to use the buttons. 
# We'll use a globally defined stream if possible, but Streamlit clears module variables on reload sometimes? No, cache helps.
# Let's try a simple approach: "Start" launches a thread that records until "Stop" sets a flag.

if st.button("🔴 Start Recording", disabled=st.session_state.recording):
    start_recording_subprocess()
    st.rerun()

if st.button("⏹️ Stop Recording", disabled=not st.session_state.recording):
    stop_recording_subprocess()
    st.rerun()

if st.session_state.recording:
    st.error("Recording... (Press Stop to finish)")

# 2. Processing Section
st.header("2. Process Batch")

if os.path.exists(RECORDING_FILE):
    st.info(f"Audio file ready: {RECORDING_FILE}")
    
    if st.button("🚀 Start Batch Processing", disabled=st.session_state.processing_active):
        st.session_state.processing_active = True
        
        # Prepare the processor
        proc = st.session_state.processor
        proc.is_running = True
        st.session_state.processing_active = True
        
        def run_pipeline(processor_instance):
            try:
                success_stt = processor_instance.process_audio_batches(RECORDING_FILE)
                if success_stt:
                    processor_instance.process_summary_batches()
            except Exception as e:
                processor_instance.status_message = f"Error: {e}"
            finally:
                processor_instance.is_running = False

        t = threading.Thread(target=run_pipeline, args=(proc,))
        t.start()
        st.rerun()

# 3. Status & Results
# 3. Status & Results
# Check if processor is running via its internal flag (reliable across threads)
is_running = st.session_state.processor.is_running
if is_running:
    st.warning("Pipeline is running... Please wait.")
    update_status()
    time.sleep(1) # Auto-refresh
    st.rerun()
else:
    update_status()
    if st.session_state.processing_active and not is_running:
         st.session_state.processing_active = False # Sync state when done

st.header("3. Notes")
if os.path.exists(FINAL_NOTES_FILE):
    with open(FINAL_NOTES_FILE, "r", encoding="utf-8") as f:
        st.markdown(f.read())
