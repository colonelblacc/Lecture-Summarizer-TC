import sounddevice as sd

print("\n--- Audio Devices ---")
print(sd.query_devices())

print("\n--- Default Input Device ---")
try:
    print(sd.query_devices(kind='input'))
except Exception as e:
    print(f"Error getting default input: {e}")
