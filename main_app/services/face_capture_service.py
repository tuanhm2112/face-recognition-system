"""
Face Capture Service - Xử lý capture và validate khuôn mặt
"""
import cv2

class FaceCaptureService:
  
    
    def __init__(self, yolo_model):

        self.yolo_model = yolo_model
    
    def validate_frame_has_face(self, frame):

        if frame is None or frame.size == 0:
            return False, "Invalid frame"
        results = self.yolo_model(frame, verbose=False)
        if len(results) == 0 or len(results[0].boxes) == 0:
            return False, "No face detected!\nPlease adjust your position."
        return True, ""
    
    def extract_face_region(self, frame):

        results = self.yolo_model(frame, verbose=False)
        if len(results) == 0 or len(results[0].boxes) == 0:
            return None, None
        boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        box = boxes[areas.argmax()]
        x1, y1, x2, y2 = box
        face_img = frame[y1:y2, x1:x2]
        if face_img.size == 0:
            return None, None
        return face_img, box.tolist()
    
    def get_camera_frame(self, camera_index=0):

        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return False, None, "Cannot open camera"
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return False, None, "Cannot read frame from camera"
        
        return True, frame, ""

