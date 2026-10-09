import os
import threading
from ultralytics import YOLO
from main_app.models import ArcFaceModel
from main_app.utils.logger import Logger


class ModelLoader:
    def __init__(self, config, device):
        self.config = config
        self.device = device
        self.logger = Logger(config["runtime"]["log_path"], config["runtime"]["log_level"])

    def _load_with_timeout(self, load_func, timeout=60, model_name="model"):
        result = [None]
        exception = [None]
        def load():
            try:
                result[0] = load_func()
            except Exception as e:
                exception[0] = e
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            raise TimeoutError(f"{model_name} loading timeout after {timeout}s")
        if exception[0]:
            raise exception[0]
        return result[0]

    def load_yolo(self):
        weight_path = self.config["models"]["face_detection"]["weight_path"]
        if not os.path.isabs(weight_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            weight_path = os.path.join(project_root, weight_path)
        if not os.path.isfile(weight_path):
            raise FileNotFoundError(f"YOLO weight not found: {weight_path}")
        print("Loading YOLO...")
        return self._load_with_timeout(lambda: YOLO(weight_path), timeout=30, model_name="YOLO")

    def load_arcface(self):
        weight_path = self.config["models"]["face_recognition"]["weight_path"]
        if not os.path.isabs(weight_path):
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            weight_path = os.path.join(project_root, weight_path)
        if not os.path.isfile(weight_path):
            raise FileNotFoundError(f"ArcFace weight not found: {weight_path}")
        ctx_id = 0 if 'cuda' in str(self.device) else -1
        print("Loading ArcFace...")
        return self._load_with_timeout(
            lambda: ArcFaceModel(weight_path, ctx_id=ctx_id),
            timeout=60,
            model_name="ArcFace"
        )