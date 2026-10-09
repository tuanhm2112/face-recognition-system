"""
Thread Manager - Quản lý pipeline xử lý face recognition
"""
from queue import Queue
from PyQt5.QtCore import QObject
from main_app.threads.camera_thread import CameraThread
from main_app.threads.detection_thread import DetectionThread
from main_app.threads.tracking_thread import TrackingThread
from main_app.threads.embedding_thread import EmbeddingThread
from main_app.threads.recognition_thread import RecognitionThread
from main_app.threads.display_thread import DisplayHandler

class ThreadManager(QObject):
    """
    Quản lý luồng xử lý: Camera → Detection → Tracking → Embedding → Recognition → Display
    """
    
    # Constants
    QUEUE_SIZE = 3
    
    def __init__(self, config, models, device, recognizer):
        super().__init__()
        self.config = config
        
        # Tạo queues
        self.queues = self._create_queues()
        
        # Tạo threads
        self.threads = self._create_threads(models, device, recognizer)
        
        # Display handler (không phải thread)
        self.display_handler = DisplayHandler()

    def _create_queues(self):
        """Tạo các queues cho pipeline"""
        return {
            'frame': Queue(maxsize=self.QUEUE_SIZE),
            'detection': Queue(maxsize=self.QUEUE_SIZE),
            'embedding': Queue(maxsize=self.QUEUE_SIZE),
            'recognition': Queue(maxsize=self.QUEUE_SIZE)
        }

    def _create_threads(self, models, device, recognizer):
        """Tạo các processing threads"""
        return {
            'camera': CameraThread(
                self.config, 
                self.queues['frame']
            ),
            'detection': DetectionThread(
                models['yolo'], 
                device, 
                self.queues['frame'], 
                self.queues['detection'],
                self.config
            ),
            'tracking': TrackingThread(
                models['yolo'],
                device,
                self.queues['detection'],
                self.queues['embedding'],
                self.config
            ),
            'embedding': EmbeddingThread(
                models['arcface'],
                device,
                self.queues['embedding'],
                self.queues['recognition']
            ),
            'recognition': RecognitionThread(
                recognizer,
                self.config,
                self.queues['recognition']
            )
        }

    def start(self):
        """Khởi động pipeline"""
        for thread in self.threads.values():
            thread.start()

    def stop(self):
        """Dừng pipeline"""
        # Dừng threads (gọi stop() để thoát vòng lặp)
        for thread in self.threads.values():
            thread.stop()
        
        # Chờ threads kết thúc
        for thread in self.threads.values():
            thread.wait(300)  # Timeout 1s để tránh hang

    def connect_signals(self, main_window, on_faces_recognized):
        """Kết nối signals giữa các components"""
        detection_thread = self.threads['detection']
        recognition_thread = self.threads['recognition']
        
        # Detection → Display Handler (cho frame gốc khi không có detection)
        detection_thread.raw_frame_detected.connect(
            self.display_handler.display_raw_frame
        )
        
        # Recognition → Display Handler (cho frame có bounding boxes)
        recognition_thread.faces_recognized.connect(
            self.display_handler.display_results
        )
        
        # Display Handler → Main Window
        self.display_handler.frame_ready.connect(
            main_window.update_video
        )
        
        # Recognition → App callback (chỉ truyền frame, boxes, person_ids)
        recognition_thread.faces_recognized.connect(
            lambda frame, boxes, person_ids, track_ids: on_faces_recognized(frame, boxes, person_ids)
        )

    def update_recognizer(self, new_recognizer):
        """Cập nhật recognizer mới"""
        self.threads['recognition'].recognizer = new_recognizer