"""
Thumbnail List Widget - Widget quản lý danh sách thumbnails hiện đại
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from main_app.utils.image_utils import ImageUtils


class ThumbnailListWidget(QWidget):
    """Widget quản lý và hiển thị danh sách thumbnails"""
    
    item_removed = pyqtSignal(int)  # Emit index khi xóa item
    
    def __init__(self, parent=None):
        """Khởi tạo widget"""
        super().__init__(parent)
        self.thumbnails = []
        self._init_ui()
    
    def _init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(10)
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(self.container_widget)
        layout.addWidget(scroll)
    
    def add_thumbnail(self, frame):
        """
        Thêm thumbnail
        
        Args:
            frame: Frame ảnh cần thêm
        """
        self.thumbnails.append(frame)
        
        # Tạo thumbnail frame
        thumb_frame = QFrame()
        thumb_frame.setObjectName("thumbnailFrame")
        thumb_layout = QHBoxLayout(thumb_frame)
        thumb_layout.setContentsMargins(10, 10, 10, 10)
        thumb_layout.setSpacing(12)
        
        # Thumbnail image
        thumb_label = QLabel()
        thumb_label.setFixedSize(100, 75)
        thumb_label.setScaledContents(False)
        thumb_label.setAlignment(Qt.AlignCenter)
        thumb_label.setStyleSheet("""
            QLabel {
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: #1a1a1a;
            }
        """)
        
        qpixmap = ImageUtils.cv2_to_qpixmap(frame)
        thumb_label.setPixmap(
            qpixmap.scaled(100, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        thumb_layout.addWidget(thumb_label)
        
        # Info section
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)
        
        index = len(self.thumbnails)
        photo_label = QLabel(f"Photo #{index}")
        photo_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        info_layout.addWidget(photo_label)
        
        size_label = QLabel(f"{frame.shape[1]}x{frame.shape[0]} px")
        size_label.setStyleSheet("color: #888888; font-size: 11px;")
        info_layout.addWidget(size_label)
        
        info_layout.addStretch()
        thumb_layout.addWidget(info_widget, 1)
        
        # Delete button
        del_button = QPushButton("🗑")
        del_button.setFixedSize(35, 35)
        del_button.setToolTip("Remove this photo")
        del_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """)
        
        current_index = index - 1
        del_button.clicked.connect(lambda: self._on_delete_clicked(thumb_frame, current_index))
        thumb_layout.addWidget(del_button)
        
        self.container_layout.addWidget(thumb_frame)
    
    def _on_delete_clicked(self, frame_widget, index):
        """Xử lý khi click nút xóa"""
        if 0 <= index < len(self.thumbnails):
            # Xóa khỏi list
            del self.thumbnails[index]
            
            # Xóa widget
            self.container_layout.removeWidget(frame_widget)
            frame_widget.deleteLater()
            
            # Emit signal
            self.item_removed.emit(index)
            
            # Update lại số thứ tự
            self._update_indices()
    
    def _update_indices(self):
        """Cập nhật lại số thứ tự thumbnails"""
        for i in range(self.container_layout.count()):
            item = self.container_layout.itemAt(i)
            if item and item.widget():
                frame = item.widget()
                # Tìm info widget (widget thứ 2 trong layout)
                layout = frame.layout()
                if layout and layout.count() >= 2:
                    info_widget = layout.itemAt(1).widget()
                    if info_widget:
                        info_layout = info_widget.layout()
                        if info_layout and info_layout.count() >= 1:
                            photo_label = info_layout.itemAt(0).widget()
                            if isinstance(photo_label, QLabel):
                                photo_label.setText(f"Photo #{i + 1}")
    
    def get_all_frames(self):
        """Lấy tất cả frames"""
        return self.thumbnails.copy()
    
    def get_count(self):
        """Lấy số lượng thumbnails"""
        return len(self.thumbnails)
    
    def clear(self):
        """Xóa tất cả thumbnails"""
        self.thumbnails.clear()
        
        # Xóa tất cả widgets
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()