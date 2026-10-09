"""
History Service - Quản lý lưu và đọc lịch sử nhận diện
"""
import os
import json
from datetime import datetime
import cv2
from main_app.utils.config_loader import ConfigManager
from main_app.utils.logger import Logger

class HistoryService:
    def __init__(self):
        self.config = ConfigManager().get_config()
        project_root = ConfigManager.get_project_root()
        self.storage_path = self.config["history"]["storage_path"]
        if not os.path.isabs(self.storage_path):
            self.storage_path = os.path.join(project_root, self.storage_path)
        self.db_path = self.config["history"]["db_path"]
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.join(project_root, self.db_path)
        self.logger = Logger("logs/app.log", "ERROR")
        self._ensure_dirs()

    def _ensure_dirs(self):
        os.makedirs(self.storage_path, exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump([], f)

    def save_history(self, person_name, frame, box, timestamp=None):
        try:
            if timestamp is None:
                timestamp = datetime.now()
            date_str = timestamp.strftime("%d_%m_%Y")
            date_dir = os.path.join(self.storage_path, date_str)
            os.makedirs(date_dir, exist_ok=True)

            img_filename = f"{person_name}_{timestamp.strftime('%H-%M-%S')}.jpg"
            img_path = os.path.join(date_dir, img_filename)

            x1, y1, x2, y2 = [int(b) for b in box]
            # expand box 0.3% of width and height
            scale = 0.3
            width = x2 - x1
            height = y2 - y1
            new_x1 = x1 - int(width * scale)
            new_y1 = y1 - int(height * scale)
            new_x2 = x2 + int(width * scale)
            new_y2 = y2 + int(height * scale)
            face_img = frame[new_y1:new_y2, new_x1:new_x2]
            if face_img.size == 0:
                self.logger.log_warning(f"Empty face image for {person_name}")
                return

            cv2.imwrite(img_path, face_img)

            # Sửa định dạng timestamp: thay isoformat() bằng strftime()
            entry = {
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S%z"),  # Ví dụ: 2025-10-04 21:13:00+0700
                "person_name": person_name,
                "img_path": img_path
            }
            with open(self.db_path, 'r+') as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=4)

            self.logger.log_info(f"Saved history for {person_name} at {img_path}")
        except Exception as e:
            self.logger.log_error(f"Save history error: {str(e)}")

    def get_history(self, limit=100):
        try:
            with open(self.db_path, 'r') as f:
                data = json.load(f)
            data.sort(key=lambda x: x["timestamp"], reverse=True)
            return data[:limit]
        except:
            return []