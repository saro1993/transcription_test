import grpc
import audio_pb2
import audio_pb2_grpc
import pyaudio

def generate_audio_chunks():
    chunk_size = 1024
    audio_format = pyaudio.paInt16
    channels = 1
    rate = 16000

    p = pyaudio.PyAudio()
    stream = p.open(format=audio_format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    try:
        while True:
            data = stream.read(chunk_size)
            yield audio_pb2.AudioRequest(audio_chunk=data)
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()
        p.terminate()

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = audio_pb2_grpc.TranscriptionServiceStub(channel)
    responses = stub.Transcribe(generate_audio_chunks())
    for response in responses:
        print(f"Transkripsjon: {response.text}")

if __name__ == '__main__':
    run()
