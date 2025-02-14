import grpc
from concurrent import futures
from google.cloud import speech_v1p1beta1 as speech
import audio_streaming_pb2
import audio_streaming_pb2_grpc

# Google Cloud Speech-klient
client = speech.SpeechClient()

class TranscriptionService(audio_streaming_pb2_grpc.TranscriptionServiceServicer):
    def Transcribe(self, request_iterator, context):
        """
        gRPC-strømming for sanntidstranskripsjon
        """
        print("🔄 Mottar lydstrøm via gRPC...")

        def audio_generator():
            for request in request_iterator:
                yield speech.StreamingRecognizeRequest(audio_content=request.audio_chunk)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="nb-NO",
            alternative_language_codes=["nn-NO", "en-US"],
            enable_automatic_punctuation=True
        )

        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

        # Send til Google Speech API
        responses = client.streaming_recognize(streaming_config, audio_generator())

        # Send transkripsjon tilbake til klienten
        for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                yield audio_streaming_pb2.TranscriptionResponse(text=transcript)

def start_grpc_server():
    """Starter gRPC-serveren."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_streaming_pb2_grpc.add_TranscriptionServiceServicer_to_server(TranscriptionService(), server)
    server.add_insecure_port("[::]:50051")
    print("🚀 gRPC-server kjører på port 50051...")
    server.start()
    server.wait_for_termination()
