from PyQt5.QtCore import QThread, pyqtSignal
import numpy as np
from main_app.utils.logger import Logger

class TrackingThread(QThread):
    tracks_ready = pyqtSignal(object, list, list, list)

    def __init__(self, yolo_model, device, detection_queue, embedding_queue, config):
        super().__init__()
        self.yolo_model = yolo_model
        self.device = device
        self.detection_queue = detection_queue
        self.embedding_queue = embedding_queue
        self.config = config
        self.running = False
        self.logger = Logger("logs/app.log", "ERROR")

    def run(self):
        self.running = True
        while self.running:
            try:
                frame, boxes = self.detection_queue.get(timeout=1.0)
                tracked_boxes, track_ids = self._track_faces(frame)
                
                if tracked_boxes:
                    self._add_to_queue(frame, tracked_boxes, track_ids)
                    self.tracks_ready.emit(frame, tracked_boxes, track_ids, [])
                
                self.detection_queue.task_done()
                
            except:
                pass

    def _track_faces(self, frame):
        conf_threshold = self.config["models"]["face_detection"]["detection_confidence"]
        tracking_config = self.config["models"]["face_tracking"]
        
        results = self.yolo_model.track(
            frame, 
            conf=conf_threshold, 
            verbose=False, 
            imgsz=tracking_config.get("imgsz", 320),
            persist=tracking_config.get("persist", True),
            tracker=tracking_config.get("tracker", "bytetrack.yaml"),
            classes=[0]
        )
        
        boxes = []
        track_ids = []
        
        for result in results:
            if not self._has_detections(result):
                continue
            
            xyxy = result.boxes.xyxy
            tids = result.boxes.id
            
            for box, tid in zip(xyxy, tids):
                try:
                    boxes.append(box.cpu().numpy().astype(int))
                    track_ids.append(int(tid.cpu().numpy()))
                except:
                    pass
        
        return boxes, track_ids
    
    def _has_detections(self, result):
        return (getattr(result, 'boxes', None) is not None and 
                result.boxes.xyxy is not None and 
                result.boxes.id is not None)
    
    def _add_to_queue(self, frame, tracked_boxes, track_ids):
        if not self.embedding_queue.full():
            self.embedding_queue.put((frame, tracked_boxes, track_ids))
        else:
            try:
                self.embedding_queue.get_nowait()
                self.embedding_queue.put((frame, tracked_boxes, track_ids))
            except:
                pass

    def stop(self):
        self.running = False
        self.wait()