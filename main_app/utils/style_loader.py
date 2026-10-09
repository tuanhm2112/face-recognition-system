"""
Style Loader - Quản lý theme cho UI
"""
import os


class StyleLoader:
    """Loader cho QSS themes với caching"""
    
    _cache = {}  # Cache để tránh đọc file nhiều lần
    
    @staticmethod
    def load_theme(theme_name="dark"):
        """
        Load QSS theme từ file với caching
        
        Args:
            theme_name: Tên theme ("dark" hoặc "light")
            
        Returns:
            str: Nội dung QSS
        """
        # Check cache
        if theme_name in StyleLoader._cache:
            return StyleLoader._cache[theme_name]
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        theme_path = os.path.join(project_root, "resources", "styles", theme_file)
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
                # Cache kết quả
                StyleLoader._cache[theme_name] = stylesheet
                return stylesheet
        except FileNotFoundError:
            print(f"Warning: Theme file '{theme_path}' not found")
            return ""
        except Exception as e:
            print(f"Error loading theme: {e}")
            return ""
    
    @staticmethod
    def get_available_themes():
        """Lấy danh sách themes có sẵn"""
        return ["dark", "light"]
    
    @staticmethod
    def clear_cache():
        """Xóa cache (dùng khi cần reload themes)"""
        StyleLoader._cache.clear()
    
    @staticmethod
    def preload_themes():
        """Preload tất cả themes vào cache"""
        for theme in StyleLoader.get_available_themes():
            StyleLoader.load_theme(theme)