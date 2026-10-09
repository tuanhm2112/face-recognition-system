"""
Camera Preview Widget - Widget hiển thị camera preview hiện đại
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
import cv2
from main_app.utils.image_utils import ImageUtils


class CameraPreviewWidget(QWidget):
    """Widget hiển thị camera preview với nút capture"""
    
    frame_captured = pyqtSignal(object)  # Emit frame khi capture
    
    def __init__(self, camera_source=0, parent=None):
        """
        Khởi tạo widget
        
        Args:
            camera_source: Camera index (int) hoặc RTMP/RTSP URL (str)
            parent: Parent widget
        """
        super().__init__(parent)
        self.camera_source = camera_source
        self.cap = None
        self.current_frame = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        
        self._init_ui()
    
    def _init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Camera label
        self.camera_label = QLabel("📹 Camera Preview")
        self.camera_label.setObjectName("videoLabel")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.camera_label.setMinimumSize(480, 270)  # 16:9 ratio
        layout.addWidget(self.camera_label, 1)
        
        # Capture button
        self.capture_button = QPushButton("📷 Capture Photo")
        self.capture_button.setObjectName("primaryButton")
        self.capture_button.setMinimumHeight(50)
        self.capture_button.setToolTip("Capture current frame")
        self.capture_button.clicked.connect(self._on_capture_clicked)
        layout.addWidget(self.capture_button)
    
    def start_camera(self):
        """
        Khởi động camera từ local index hoặc RTMP/RTSP stream
        
        Returns:
            bool: True nếu thành công
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_source)
            
            if self.cap.isOpened():
                self.timer.start(30)  # ~33 FPS
                
                # Display source info
                source_type = "Local Camera" if isinstance(self.camera_source, int) else "RTMP/RTSP Stream"
                self.camera_label.setText(f"📹 {source_type}\nConnecting...")
                
                return True
            else:
                error_msg = f"❌ Cannot open camera\nSource: {self.camera_source}"
                self.camera_label.setText(error_msg)
                return False
                
        except Exception as e:
            self.camera_label.setText(f"❌ Camera Error\n{str(e)}")
            return False
    
    def stop_camera(self):
        """Dừng camera"""
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.camera_label.setText("📹 Camera Preview\nStopped")
    
    def _update_frame(self):
        """Cập nhật frame từ camera"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame = frame
                self._display_frame(frame)
            else:
                self.camera_label.setText("❌ Failed to read frame")
    
    def _display_frame(self, frame):
        """Hiển thị frame lên label"""
        qpixmap = ImageUtils.cv2_to_qpixmap(frame)
        scaled = qpixmap.scaled(
            self.camera_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled)
    
    def _on_capture_clicked(self):
        """Xử lý khi click nút capture"""
        if self.current_frame is not None:
            self.frame_captured.emit(self.current_frame.copy())
    
    def get_current_frame(self):
        """Lấy frame hiện tại"""
        return self.current_frame.copy() if self.current_frame is not None else None
    
    def set_camera_source(self, source):
        """
        Đổi nguồn camera
        
        Args:
            source: Camera index (int) hoặc RTMP/RTSP URL (str)
        """
        was_running = self.cap is not None and self.cap.isOpened()
        self.stop_camera()
        self.camera_source = source
        if was_running:
            self.start_camera()