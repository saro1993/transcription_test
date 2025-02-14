import grpc
from concurrent import futures
import audio_streaming_pb2_grpc
from services.transcription_service import TranscriptionService

def start_grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_streaming_pb2_grpc.add_TranscriptionServiceServicer_to_server(
        TranscriptionService(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC-server kjører på port 50051")
    server.wait_for_termination()
