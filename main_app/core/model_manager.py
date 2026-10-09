import os
from main_app.utils.model_loader import ModelLoader
from main_app.utils.simple_recognizer import SimpleFaceRecognizer
from main_app.utils.logger import Logger


class ModelManager:
    def __init__(self, config, device):
        self.config = config
        self.device = device
        self.models = {}
        self.recognizer = None
        self._load_models()

    def _load_models(self):
        model_loader = ModelLoader(self.config, self.device)
        self.models = {
            'yolo': model_loader.load_yolo(),
            'arcface': model_loader.load_arcface()
        }
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, "resources", "data")
        logger = Logger(self.config["runtime"]["log_path"], self.config["runtime"]["log_level"])
        self.recognizer = SimpleFaceRecognizer(data_dir, logger)

    def get_models(self):
        return self.models

    def get_recognizer(self):
        return self.recognizer