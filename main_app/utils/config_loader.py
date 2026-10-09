"""
Config Manager - Quản lý cấu hình động với signals
"""
import yaml
import os
from PyQt5.QtCore import QObject, pyqtSignal

class ConfigManager(QObject):
    """
    Singleton ConfigManager với khả năng emit signals khi config thay đổi
    """
    
    # Signals để thông báo config thay đổi
    config_changed = pyqtSignal(dict)  # Toàn bộ config mới
    theme_changed = pyqtSignal(str)    # Theme mới (dark/light)
    camera_changed = pyqtSignal(dict)  # Camera config mới
    model_changed = pyqtSignal(dict)   # Model config mới
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Khởi tạo ConfigManager"""
        if self._initialized:
            return
        
        super().__init__()
        self._config = None
        self._config_path = None
        self._initialized = True
        self.load_config()
    
    @staticmethod
    def get_project_root():
        """Lấy thư mục gốc của project"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        return project_root
    
    def load_config(self):
        """Load config từ file YAML"""
        project_root = self.get_project_root()
        self._config_path = os.path.join(project_root, "resources", "config", "config.yaml")
        
        if not os.path.exists(self._config_path):
            raise FileNotFoundError(f"Config file not found: {self._config_path}")
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
            if self._config is None:
                self._config = {}
        except Exception as e:
            print(f"Warning: Failed to load config: {e}, using defaults")
            self._config = {}
        
        return self._config
    
    def get_config(self):
        """Lấy config hiện tại (trong memory)"""
        return self._config
    
    def update_config(self, new_config, save_to_file=True):
        """
        Cập nhật config và emit signals
        
        Args:
            new_config: Dict config mới
            save_to_file: Có lưu vào file không (default: True)
        """
        old_config = self._config.copy()
        self._config = new_config
        
        # Lưu vào file nếu cần
        if save_to_file:
            self._save_to_file()
        
        # Emit signals cho các thay đổi cụ thể
        self._emit_specific_signals(old_config, new_config)
        
        # Emit signal tổng quát
        self.config_changed.emit(new_config)
    
    def _save_to_file(self):
        """Lưu config vào file YAML"""
        with open(self._config_path, 'w', encoding='utf-8') as file:
            yaml.safe_dump(self._config, file, default_flow_style=False)
    
    def _emit_specific_signals(self, old_config, new_config):
        """Emit signals cụ thể cho từng loại thay đổi"""
        # Theme changed
        old_theme = old_config.get("ui", {}).get("theme", "dark")
        new_theme = new_config.get("ui", {}).get("theme", "dark")
        if old_theme != new_theme:
            self.theme_changed.emit(new_theme)
        
        # Camera changed
        if old_config.get("camera") != new_config.get("camera"):
            self.camera_changed.emit(new_config["camera"])
        
        # Model changed
        if old_config.get("models") != new_config.get("models"):
            self.model_changed.emit(new_config["models"])
    
    def get(self, key, default=None):
        """Get config value by key"""
        return self._config.get(key, default)
    
    def __getitem__(self, key):
        """Hỗ trợ truy cập bằng config["key"]"""
        return self._config[key]


# Legacy support - để không phá code cũ
class ConfigLoader:
    """Legacy ConfigLoader for backward compatibility"""
    
    @staticmethod
    def get_project_root():
        return ConfigManager.get_project_root()
    
    def load_config(self):
        return ConfigManager().get_config()