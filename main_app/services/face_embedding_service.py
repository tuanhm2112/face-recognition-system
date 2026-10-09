import cv2
import numpy as np


class FaceEmbeddingService:
    def __init__(self, arcface_model):
        self.arcface_model = arcface_model

    def extract_embedding(self, face_image):
        try:
            embedding = self.arcface_model(face_image)
            if np.linalg.norm(embedding) > 0:
                return embedding
            return None
        except:
            return None

    def process_face_for_embedding(self, face_image):
        embedding = self.extract_embedding(face_image)
        if embedding is None:
            return None, None
        aligned = cv2.resize(face_image, (112, 112))
        return aligned, embedding
