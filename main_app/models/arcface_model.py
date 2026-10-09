import cv2
import numpy as np
from insightface.model_zoo import get_model


class ArcFaceModel:
    def __init__(self, weight_path, ctx_id=0):
        self.model = get_model(weight_path)
        self.model.prepare(ctx_id=ctx_id)

    def extract_embedding(self, face_image):
        img = cv2.resize(face_image, (112, 112))
        return self.model.get_feat(img).flatten()

    def __call__(self, face_image):
        return self.extract_embedding(face_image)
