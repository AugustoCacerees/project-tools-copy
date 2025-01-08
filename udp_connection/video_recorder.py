import cv2
import time

class VideoRecorder:
    def __init__(self, user_id, buffer, frame_size=(640, 480), fps=30):
        self.buffer = buffer
        self.recording = False
        self.user_id = user_id
        self.frame_size = frame_size
        self.fps = fps
        self.video_name = f"{user_id}_{int(time.time())}.avi"
        self.out = None

    def start_recording(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.video_name, fourcc, self.fps, self.frame_size)
        self.recording = True

    def record(self):
        self.start_recording()
        cap = cv2.VideoCapture(0)
        while self.recording:
            ret, frame = cap.read()
            if ret:
                self.buffer.put(frame)  # Agregar el frame al buffer
                self.out.write(frame)
            else:
                print("Failed to capture frame.")
                break
        cap.release()
        self.stop_recording()

    def stop_recording(self):
        self.recording = False
        if self.out is not None:
            self.out.release()
        print(f"Video saved as {self.video_name}")
