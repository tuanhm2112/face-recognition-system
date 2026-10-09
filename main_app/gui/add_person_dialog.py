"""
Add Person Dialog - Dialog thêm người mới với giao diện hiện đại
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QLabel, QMessageBox, QWidget, QFrame,
                             QComboBox)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

from main_app.utils.style_loader import StyleLoader
from main_app.utils.config_loader import ConfigManager
from main_app.services import FaceCaptureService, FaceEmbeddingService, PersonService
from main_app.widgets import CameraPreviewWidget, ThumbnailListWidget


class AddPersonDialog(QDialog):
    """Dialog thêm người mới vào hệ thống và xóa người hiện có"""
    
    person_added = pyqtSignal(str, list)
    person_deleted = pyqtSignal(str)

    def __init__(self, config, models, device, recognizer):
        super().__init__()
        self.config = config
        self.config_manager = ConfigManager()
        
        # Khởi tạo services
        self.capture_service = FaceCaptureService(models['yolo'])
        self.embedding_service = FaceEmbeddingService(models['arcface'])
        self.person_service = PersonService(recognizer)
        
        # Data storage
        self.captured_data = []  # List of (frame, aligned_face, embedding)
        
        self._init_ui()
        self._apply_theme()
        self._connect_signals()

    def _get_camera_source(self):
        source_type = self.config.get("camera", {}).get("source_type", "local")
        if source_type == "local":
            return self.config.get("camera", {}).get("camera_index", 0)
        return self.config.get("camera", {}).get("stream_url", 0)

    def _init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("Add New Person")
        self.setMinimumSize(1000, 650)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)
        
        # Left: Camera preview
        camera_source = self._get_camera_source()
        self.camera_widget = CameraPreviewWidget(camera_source=camera_source)
        content_layout.addWidget(self.camera_widget, 3)
        
        # Right: Form section
        form_widget = self._create_form_section()
        content_layout.addWidget(form_widget, 2)
        
        main_layout.addLayout(content_layout, 1)

    def _create_header(self):
        """Tạo header với tiêu đề"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("👤 Add New Person")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        subtitle = QLabel("Capture multiple photos for better recognition")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        return header_frame

    def _create_form_section(self):
        """Tạo phần form nhập liệu và xóa người"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Name input section
        name_section = self._create_name_input()
        layout.addLayout(name_section)
        
        # Delete person section
        delete_section = self._create_delete_section()
        layout.addLayout(delete_section)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #404040;")
        layout.addWidget(divider)
        
        # Thumbnails section
        thumbnails_label = QLabel("📸 Captured Photos")
        thumbnails_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(thumbnails_label)
        
        self.thumbnail_list = ThumbnailListWidget()
        layout.addWidget(self.thumbnail_list, 1)
        
        # Status label
        self.status_label = QLabel("No photos captured yet")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-size: 12px; padding: 8px;")
        layout.addWidget(self.status_label)
        
        # Save button
        self.save_button = QPushButton("💾 Save Person")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setMinimumHeight(50)
        self.save_button.setEnabled(False)
        layout.addWidget(self.save_button)
        
        return widget

    def _create_name_input(self):
        """Tạo phần nhập tên"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        name_label = QLabel("Person Name:")
        name_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter full name...")
        self.name_input.setMinimumHeight(40)
        layout.addWidget(self.name_input)
        
        hint_label = QLabel("💡 Tip: Capture 3-5 photos from different angles")
        hint_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(hint_label)
        
        return layout
    
    def _create_delete_section(self):
        """Tạo phần xóa người"""
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        delete_label = QLabel("Delete Existing Person:")
        delete_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(delete_label)
        
        self.person_selector = QComboBox()
        self.person_selector.setMinimumHeight(40)
        self.person_selector.addItem("Select a person...")
        self._populate_person_selector()
        layout.addWidget(self.person_selector)
        
        self.delete_button = QPushButton("🗑️ Delete Person")
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setMinimumHeight(40)
        self.delete_button.setEnabled(False)
        layout.addWidget(self.delete_button)
        
        return layout

    def _populate_person_selector(self):
        """Điền danh sách persons vào QComboBox"""
        self.person_selector.clear()
        self.person_selector.addItem("Select a person...")
        persons = self.person_service.get_all_persons()
        for person_id, person_data in persons.items():
            self.person_selector.addItem(person_data['name'], person_id)
    
    def _connect_signals(self):
        """Kết nối signals"""
        self.camera_widget.frame_captured.connect(self._on_frame_captured)
        self.thumbnail_list.item_removed.connect(self._on_thumbnail_removed)
        self.name_input.textChanged.connect(self._update_ui_state)
        self.save_button.clicked.connect(self._save_person)
        self.person_selector.currentIndexChanged.connect(self._update_ui_state)
        self.delete_button.clicked.connect(self._delete_person)
        self.config_manager.theme_changed.connect(self._on_theme_changed)
    
    def _apply_theme(self, theme_name=None):
        """Áp dụng theme"""
        if theme_name is None:
            theme_name = self.config.get("ui", {}).get("theme", "dark")
        
        stylesheet = StyleLoader.load_theme(theme_name)
        # Thêm style cho dangerButton
        danger_style = """
            QPushButton#dangerButton {
                background-color: #dc3545;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton#dangerButton:hover {
                background-color: #c82333;
            }
            QPushButton#dangerButton:disabled {
                background-color: #6c757d;
                color: #cccccc;
            }
        """
        self.setStyleSheet(stylesheet + danger_style)
    
    def _on_theme_changed(self, theme_name):
        """Callback khi theme thay đổi"""
        self._apply_theme(theme_name)

    def showEvent(self, event):
        """Khi dialog hiển thị, bật camera và cập nhật danh sách persons"""
        super().showEvent(event)
        self._populate_person_selector()
        self.camera_widget.start_camera()

    def closeEvent(self, event):
        """Khi đóng dialog, tắt camera"""
        self.camera_widget.stop_camera()
        super().closeEvent(event)

    def _on_frame_captured(self, frame):
        """Xử lý khi capture frame từ camera"""
        # Validate có khuôn mặt
        has_face, error_msg = self.capture_service.validate_frame_has_face(frame)
        
        if not has_face:
            QMessageBox.warning(self, "Warning", f"⚠ {error_msg}")
            return
        
        # Extract face region
        face_img, bbox = self.capture_service.extract_face_region(frame)
        
        if face_img is None:
            QMessageBox.warning(self, "Warning", "Failed to extract face")
            return
        
        # Process face: align + extract embedding
        aligned_face, embedding = self.embedding_service.process_face_for_embedding(face_img)
        
        if aligned_face is None or embedding is None:
            QMessageBox.warning(self, "Warning", "Failed to process face")
            return
        
        # Lưu data
        self.captured_data.append((frame, aligned_face, embedding))
        
        # Thêm thumbnail
        self.thumbnail_list.add_thumbnail(face_img)
        
        # Update UI
        self._update_ui_state()

    def _on_thumbnail_removed(self, index):
        """Xử lý khi xóa thumbnail"""
        if 0 <= index < len(self.captured_data):
            del self.captured_data[index]
            self._update_ui_state()

    def _update_ui_state(self):
        """Cập nhật trạng thái UI"""
        count = self.thumbnail_list.get_count()
        
        if count == 0:
            self.status_label.setText("No photos captured yet")
            self.status_label.setStyleSheet("color: #888888; font-size: 12px;")
        else:
            self.status_label.setText(f"✓ {count} photo(s) captured")
            self.status_label.setStyleSheet("color: #00aa00; font-size: 12px; font-weight: bold;")
        
        # Validate name
        is_valid_name, _ = self.person_service.validate_person_name(
            self.name_input.text().strip()
        )
        
        self.save_button.setEnabled(count > 0 and is_valid_name)
        
        # Enable delete button if a person is selected
        self.delete_button.setEnabled(self.person_selector.currentIndex() > 0)

    def _save_person(self):
        """Lưu người mới vào database"""
        name = self.name_input.text().strip()
        
        # Validate name
        is_valid, error_msg = self.person_service.validate_person_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Warning", error_msg)
            return
        
        if len(self.captured_data) == 0:
            QMessageBox.warning(self, "Warning", "Please capture at least one photo")
            return
        
        try:
            # Lưu ảnh aligned faces
            frames = [data[0] for data in self.captured_data]
            aligned_faces = [data[1] for data in self.captured_data]
            self.person_service.save_face_images(name, frames, aligned_faces)
            
            # Thêm person với embeddings
            embeddings = [data[2] for data in self.captured_data]
            success, person_id, message = self.person_service.add_person(
                name, frames, embeddings
            )
            
            if success:
                QMessageBox.information(self, "Success", f"✓ {message}")
                self.person_added.emit(person_id, embeddings)
                self._populate_person_selector()  # Cập nhật danh sách sau khi thêm
                self.close()
            else:
                QMessageBox.warning(self, "Error", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
    
    def _delete_person(self):
        """Xóa người được chọn"""
        person_id = self.person_selector.currentData()
        person_name = self.person_selector.currentText()
        
        if not person_id:
            QMessageBox.warning(self, "Warning", "Please select a person to delete")
            return
        
        # Xác nhận xóa
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete '{person_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success, message = self.person_service.delete_person(person_id)
                if success:
                    QMessageBox.information(self, "Success", f"✓ {message}")
                    self.person_deleted.emit(person_id)
                    self._populate_person_selector()
                else:
                    QMessageBox.warning(self, "Error", message)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {str(e)}")