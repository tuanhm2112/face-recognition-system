import logging
import os

class Logger:
    def __init__(self, log_path, log_level):
        self.logger = logging.getLogger("FaceRecognition")
        self.logger.setLevel(getattr(logging, log_level))
        
        # Resolve relative path nếu cần
        if not os.path.isabs(log_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_path = os.path.join(project_root, log_path)
        
        # Tạo thư mục log nếu chưa có
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        handler = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)
    
    def log_warning(self, message):
        self.logger.warning(message)