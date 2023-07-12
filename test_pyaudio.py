from typing import Deque
import pyaudio
import numpy as np
import wave
import time
from collections import deque

# Audio format parameters
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
SEC = int(RATE / CHUNK)


SAVE_INT = 4
WAVE_OUTPUT_FILENAME = "test_wav"

# Duration of audio to keep between saves
KEEP_DURATION = 0.2  # in seconds

# Create a buffer to hold audio data
buffer: Deque[bytes] = deque(maxlen=int((RATE*SAVE_INT) + (RATE*KEEP_DURATION)))
print(buffer.maxlen)

i = 1

# Define the callback function that PyAudio will use
def callback(in_data, frame_count, time_info, status):
    # Append bytes to buffer
    buffer.extend(np.frombuffer(in_data, np.int16))
    # buffer.extend([bytes(d) for d in in_data])
    print(len(buffer))

    # If buffer has more than RECORD_SECONDS of audio, write to file
    if len(buffer) / RATE > SAVE_INT:
        # Extract the first RECORD_SECONDS of audio and write it to file
        audio_to_save = [buffer.popleft() for _ in range(int(RATE * SAVE_INT))]
        global i
        write_to_file(audio_to_save, WAVE_OUTPUT_FILENAME+f"{i}.wav")
        i+=1

    # Always return something, even if we're not yet ready to output
    return (None, pyaudio.paContinue)

# Write buffer to file
def write_to_file(buffer, filename):
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(p.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    # waveFile.writeframes(b''.join(buffer))
    waveFile.writeframes(b''.join(buffer))
    waveFile.close()

# Create PyAudio object
p = pyaudio.PyAudio()

# Open stream using callback
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                # frames_per_buffer=CHUNK,
                stream_callback=callback)

# stream.start_stream()

# Keep the stream active for a specified amount of time
# for _ in range(1):
time.sleep(SAVE_INT)

# Stop the stream after the time has elapsed
stream.stop_stream()
stream.close()

# Terminate the PyAudio object
p.terminate()

