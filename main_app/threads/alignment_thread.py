"""
Alignment Thread - Căn chỉnh khuôn mặt
"""
from PyQt5.QtCore import QThread
from main_app.utils.logger import Logger
from main_app.utils.face_aligner import FaceAligner

class AlignmentThread(QThread):
    def __init__(self, alignment_model, device, detection_queue, embedding_queue):
        super().__init__()
        self.alignment_model = alignment_model
        self.device = device
        self.detection_queue = detection_queue
        self.embedding_queue = embedding_queue
        self.running = False
        self.logger = Logger("logs/app.log", "ERROR")
        self.face_aligner = FaceAligner()

    def run(self):
        self.running = True
        while self.running:
            try:
                frame, boxes = self.detection_queue.get(timeout=1.0)
                aligned_faces = []
                
                for box in boxes:
                    try:
                        x1, y1, x2, y2 = [int(b) for b in box]
                        face_img = frame[y1:y2, x1:x2]
                        
                        if face_img.size == 0:
                            continue
                        
                        landmarks = self.alignment_model.get_landmarks(face_img)
                        
                        if landmarks is not None and len(landmarks) > 0:
                            aligned_face = self.face_aligner.align_face(face_img, landmarks[0], image_size=(112, 112))
                            aligned_faces.append(aligned_face)
                        else:
                            aligned_faces.append(face_img)
                            
                    except Exception as e:
                        self.logger.log_error(f"Alignment error: {str(e)}")
                        continue
                
                if aligned_faces and len(aligned_faces) == len(boxes):
                    self.embedding_queue.put((frame, boxes, aligned_faces))
                    
                self.detection_queue.task_done()
                
            except:
                pass

    def stop(self):
        self.running = False
        self.wait()