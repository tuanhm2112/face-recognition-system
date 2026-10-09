from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from main_app.utils.image_utils import ImageUtils

class CameraThread(QThread):
    frame_captured = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    WAIT_TIMEOUT_MS = 200

    def __init__(self, config, frame_queue):
        super().__init__()
        self.config = config
        self.frame_queue = frame_queue
        self.running = False
        self.cap = None

    def run(self):
        self.running = True
        try:
            self._open_stream()
            if not self.cap or not self.cap.isOpened():
                self.error_occurred.emit("Cannot open camera source.")
                return
            self._capture_loop()
        except Exception as e:
            self.error_occurred.emit(f"Camera error: {str(e)}")
        finally:
            self._release_camera()

    def _open_stream(self):
        self._release_camera()
        source_type = self.config["camera"].get("source_type", "local")
        src = self.config["camera"].get("stream_url", "") if source_type != "local" else self.config["camera"].get("camera_index", 0)
        if source_type == "local":
            self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            width, height = self.config["camera"]["resolution"]
            fps = self.config["camera"]["fps"]
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
        else:
            self.cap = cv2.VideoCapture(src, cv2.CAP_FFMPEG)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)
            self.cap.set(cv2.CAP_PROP_FPS, 30)

    def _capture_loop(self):
        sleep_ms = self._calculate_sleep_time()
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            self._add_to_queue(frame)
            self.msleep(sleep_ms)

    def _calculate_sleep_time(self):
        fps = self.config["camera"]["fps"]
        return 1000 // fps if fps > 0 else 33

    def _add_to_queue(self, frame):
        if not self.frame_queue.full():
            self.frame_queue.put(frame)
        else:
            try:
                self.frame_queue.get_nowait()
                self.frame_queue.put(frame)
            except:
                pass

    def _release_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def stop(self):
        self.running = False
        self.wait(self.WAIT_TIMEOUT_MS)
