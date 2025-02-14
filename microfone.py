import pyaudio
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

frames = [np.frombuffer(stream.read(CHUNK), dtype=np.int16) for _ in range(int(RATE / CHUNK * 5))]

stream.stop_stream()
stream.close()
p.terminate()

if "__name__" == "__main__":
    print(frames)
    stream.start_stream()

