import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from main_app.utils.logger import Logger
import cv2


class EmbeddingThread(QThread):
    embeddings_ready = pyqtSignal(object, list, list)

    def __init__(self, arcface_model, device, embedding_queue, recognition_queue):
        super().__init__()
        self.arcface_model = arcface_model
        self.embedding_queue = embedding_queue
        self.recognition_queue = recognition_queue
        self.running = False
        self.logger = Logger("logs/app.log", "ERROR")

    def run(self):
        self.running = True
        while self.running:
            try:
                frame, tracked_boxes, track_ids = self.embedding_queue.get(timeout=1.0)
                embeddings = self._extract_embeddings(frame, tracked_boxes)
                if embeddings and len(embeddings) == len(tracked_boxes):
                    self._add_to_queue(frame, tracked_boxes, embeddings, track_ids)
                self.embedding_queue.task_done()
            except:
                pass

    def _extract_embeddings(self, frame, boxes):
        embeddings = []
        for box in boxes:
            embedding = self._extract_single_embedding(frame, box)
            if embedding is not None:
                embeddings.append(embedding)
        return embeddings

    def _extract_single_embedding(self, frame, box):
        try:
            x1, y1, x2, y2 = [int(b) for b in box]
            face = frame[y1:y2, x1:x2]
            if face.size == 0:
                return None
            embedding = self.arcface_model(face)
            if np.linalg.norm(embedding) > 0:
                return embedding
            return None
        except:
            return None

    def _add_to_queue(self, frame, tracked_boxes, embeddings, track_ids):
        if not self.recognition_queue.full():
            self.recognition_queue.put((frame, tracked_boxes, embeddings, track_ids))
        else:
            try:
                self.recognition_queue.get_nowait()
                self.recognition_queue.put((frame, tracked_boxes, embeddings, track_ids))
            except:
                pass

    def stop(self):
        self.running = False
        self.wait()