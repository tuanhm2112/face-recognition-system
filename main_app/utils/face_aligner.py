"""
Face Aligner - Căn chỉnh khuôn mặt sử dụng landmarks (chuẩn FaceNet)
"""
import cv2
import numpy as np
from skimage import transform as trans

class FaceAligner:
    """Căn chỉnh khuôn mặt về kích thước chuẩn cho FaceNet"""
    
    @staticmethod
    def align_face(img, landmarks, image_size=(160, 160)):
        """
        Căn chỉnh khuôn mặt dựa trên landmarks

        Args:
            img: Ảnh khuôn mặt
            landmarks: 68 landmarks từ face_alignment
            image_size: Kích thước đầu ra (FaceNet = 160x160)

        Returns:
            Ảnh đã căn chỉnh
        """
        # Lấy 5 điểm chính: mắt trái, mắt phải, mũi, miệng trái, miệng phải
        left_eye = landmarks[36:42].mean(axis=0)
        right_eye = landmarks[42:48].mean(axis=0)
        nose = landmarks[30]
        left_mouth = landmarks[48]
        right_mouth = landmarks[54]
        
        src = np.array([left_eye, right_eye, nose, left_mouth, right_mouth], dtype=np.float32)

        # Điểm đích chuẩn cho FaceNet (160x160)
        dst = np.array([
            [54.706573, 80.03762],
            [105.045425, 79.677345],
            [80.03656, 107.01887],
            [59.356216, 134.5497],
            [100.50284, 134.02554]
        ], dtype=np.float32)

        # Scale nếu thay đổi kích thước khác (ví dụ 128x128)
        dst = dst * (image_size[0] / 160.0)
        
        # Tính affine transform
        tform = trans.SimilarityTransform()
        tform.estimate(src, dst)
        M = tform.params[0:2, :]

        # Warp ảnh
        aligned = cv2.warpAffine(img, M, image_size, borderValue=0.0)
        return aligned
