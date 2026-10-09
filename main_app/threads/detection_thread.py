from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from main_app.utils.logger import Logger
from main_app.utils.image_utils import ImageUtils

class DetectionThread(QThread):
    faces_detected = pyqtSignal(object, list, list)
    raw_frame_detected = pyqtSignal(object)

    def __init__(self, yolo_model, device, frame_queue, detection_queue, config):
        super().__init__()
        self.yolo_model = yolo_model
        self.device = device
        self.frame_queue = frame_queue
        self.detection_queue = detection_queue
        self.config = config
        self.running = False
        self.logger = Logger("logs/app.log", "ERROR")

    def run(self):
        self.running = True
        while self.running:
            try:
                frame = self.frame_queue.get(timeout=1.0)
                
                if not self._is_valid_frame(frame):
                    self.frame_queue.task_done()
                    continue
                
                boxes, landmarks = self._detect_faces(frame)
                if boxes:
                    self._add_to_queue(frame, boxes)
                    self.faces_detected.emit(frame, boxes, landmarks)
                else:
                    qpixmap = ImageUtils.cv2_to_qpixmap(frame)
                    self.raw_frame_detected.emit(qpixmap)
                
                self.frame_queue.task_done()
                
            except:
                pass
    
    def _is_valid_frame(self, frame):
        return frame is not None and frame.size > 0
    
    def _detect_faces(self, frame):
        conf_threshold = self.config["models"]["face_detection"]["detection_confidence"]
        results = self.yolo_model(frame, conf=conf_threshold, verbose=False, imgsz=320)
        boxes = []
        landmarks = []
        for result in results:
            if not self._has_detections(result):
                continue
                
            xyxy = result.boxes.xyxy
            kpts = getattr(result, 'keypoints', None)
            
            if self._has_keypoints(kpts):
                self._process_with_keypoints(xyxy, kpts, boxes, landmarks)
            else:
                self._process_without_keypoints(xyxy, boxes, landmarks)
        
        return boxes, landmarks
    
    def _has_detections(self, result):
        return (getattr(result, 'boxes', None) is not None and 
                result.boxes.xyxy is not None)
    
    def _has_keypoints(self, kpts):
        return (kpts is not None and 
                getattr(kpts, 'xy', None) is not None)
    
    def _process_with_keypoints(self, xyxy, kpts, boxes, landmarks):
        for box, kpt in zip(xyxy, kpts.xy):
            try:
                boxes.append(box.cpu().numpy().astype(int))
                landmarks.append(kpt.cpu().numpy().astype(int))
            except:
                pass
    
    def _process_without_keypoints(self, xyxy, boxes, landmarks):
        for box in xyxy:
            try:
                boxes.append(box.cpu().numpy().astype(int))
                landmarks.append(None)
            except:
                pass
    
    def _add_to_queue(self, frame, boxes):
        if not self.detection_queue.full():
            self.detection_queue.put((frame, boxes))
        else:
            try:
                self.detection_queue.get_nowait()
                self.detection_queue.put((frame, boxes))
            except:
                pass

    def stop(self):
        self.running = False
        self.wait()