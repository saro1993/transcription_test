import grpc
from concurrent import futures
import audio_streaming_pb2
import audio_streaming_pb2_grpc

class TranscriptionService(audio_streaming_pb2_grpc.TranscriptionServiceServicer):
    def Transcribe(self, request_iterator, context):
        for audio_request in request_iterator:
            audio_chunk = audio_request.audio_chunk
            # Prosesser lyd_chunk her (f.eks. send til en talegjenkjenningstjeneste)
            transcribed_text = "Transkribert tekst"  # Dette bør være resultatet av prosesseringen
            yield audio_streaming_pb2.TranscriptionResponse(text=transcribed_text)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_streaming_pb2_grpc.add_TranscriptionServiceServicer_to_server(TranscriptionService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
