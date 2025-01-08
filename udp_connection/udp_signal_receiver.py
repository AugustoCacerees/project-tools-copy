import socket
import threading
from queue import Queue
from video_recorder import VideoRecorder
from mediapipe_processor import MediapipeProcessor


class UDPSignalReceiver:
    def __init__(self, host="localhost", port=9999, port_points=9998):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((host, port))
        self.buffer = Queue(maxsize=50)  # Buffer con tamaño limitado
        self.recorder = None
        self.recording_thread = None
        self.mediapipe_processor = None
        self.processing_thread = None
        self.port_points = port_points

    def listen_for_signals(self):
        try:
            while True:
                data, addr = self.udp_socket.recvfrom(1024)
                signal = data.decode('utf-8')

                if signal.startswith("start"):
                    user_id = signal.split()[1]
                    if self.recorder and self.recorder.recording:
                        continue
                    else:
                        # Iniciar grabación de video
                        self.recorder = VideoRecorder(user_id, self.buffer)
                        self.recording_thread = threading.Thread(target=self.recorder.record)
                        self.recording_thread.start()
                        
                        # Iniciar procesamiento de puntos del cuerpo
                        self.mediapipe_processor = MediapipeProcessor(self.buffer, self.port_points)
                        self.processing_thread = threading.Thread(target=self.mediapipe_processor.process)
                        self.processing_thread.start()

                elif signal == "stop" and self.recorder:
                    # Detener grabación y procesamiento
                    self.recorder.stop_recording()  # Detiene la grabación
                    if self.recording_thread and self.recording_thread.is_alive():
                        self.recording_thread.join()  # Espera a que termine el hilo de grabación
                    print("Recording stopped and saved.")
                    self.mediapipe_processor.stop_processing()
                    if self.processing_thread and self.processing_thread.is_alive():
                        self.processing_thread.join()

                    print("Recording and processing stopped.")
                    self.recorder = None
                    self.mediapipe_processor = None
                    self.recording_thread = None
                    self.processing_thread = None
        finally:
            self.udp_socket.close()

    def start(self):
        listener_thread = threading.Thread(target=self.listen_for_signals)
        listener_thread.start()
