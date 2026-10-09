"""
Settings Dialog - Cài đặt ứng dụng với giao diện hiện đại
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QComboBox, QSlider, QTabWidget, QWidget,
                             QGroupBox, QCheckBox, QMessageBox, QLineEdit, 
                             QRadioButton, QButtonGroup, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from main_app.utils.style_loader import StyleLoader
from main_app.utils.config_loader import ConfigManager


class SettingsDialog(QDialog):
    """Dialog cài đặt với khả năng áp dụng ngay lập tức"""
    
    settings_applied = pyqtSignal()
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.config_manager = ConfigManager()
        self._init_ui()
        self._apply_theme()

    def _init_ui(self):
        """Khởi tạo giao diện"""
        self.setWindowTitle("Settings")
        self.setMinimumSize(600, 550)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_general_tab(), "General")
        tab_widget.addTab(self._create_advanced_tab(), "Advanced")
        main_layout.addWidget(tab_widget, 1)
        
        # Buttons
        buttons_layout = self._create_action_buttons()
        main_layout.addLayout(buttons_layout)

    def _create_header(self):
        """Tạo header"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("⚙ Application Settings")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        subtitle = QLabel("Configure camera, appearance, and recognition settings")
        subtitle.setStyleSheet("color: #888888; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        return header_frame

    def _create_general_tab(self):
        """Tab General - Người dùng cuối"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Camera settings
        camera_group = self._create_camera_group()
        layout.addWidget(camera_group)
        
        # Appearance settings
        appearance_group = self._create_appearance_group()
        layout.addWidget(appearance_group)
        
        layout.addStretch()
        return widget

    def _create_camera_group(self):
        """Tạo group camera settings"""
        group = QGroupBox("📹 Camera Settings")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Camera source type
        source_label = QLabel("Camera Source:")
        source_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(source_label)
        
        # Radio buttons
        self.source_button_group = QButtonGroup()
        
        self.local_camera_radio = QRadioButton("Local Camera (USB/Built-in)")
        self.rtmp_camera_radio = QRadioButton("RTMP/RTSP Stream")
        
        self.source_button_group.addButton(self.local_camera_radio, 0)
        self.source_button_group.addButton(self.rtmp_camera_radio, 1)
        
        current_source = self.config["camera"].get("source_type", "local")
        if current_source == "local":
            self.local_camera_radio.setChecked(True)
        else:
            self.rtmp_camera_radio.setChecked(True)
        
        layout.addWidget(self.local_camera_radio)
        layout.addWidget(self.rtmp_camera_radio)
        
        # Local camera widget
        self.local_camera_widget = self._create_local_camera_widget()
        layout.addWidget(self.local_camera_widget)
        
        # RTMP URL widget
        self.rtmp_url_widget = self._create_rtmp_url_widget()
        layout.addWidget(self.rtmp_url_widget)
        
        # Connect toggle
        self.local_camera_radio.toggled.connect(self._toggle_camera_source)
        self._toggle_camera_source()
        
        # Resolution
        layout.addSpacing(10)
        res_label = QLabel("Resolution:")
        res_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(res_label)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "640x480 (VGA)",
            "1280x720 (HD)",
            "1920x1080 (Full HD)"
        ])
        current_res = self.config["camera"]["resolution"]
        res_map = {str([640, 480]): 0, str([1280, 720]): 1, str([1920, 1080]): 2}
        self.resolution_combo.setCurrentIndex(res_map.get(str(current_res), 0))
        layout.addWidget(self.resolution_combo)
        
        group.setLayout(layout)
        return group

    def _create_local_camera_widget(self):
        """Widget cho local camera"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 5, 0, 5)
        layout.setSpacing(8)
        
        label = QLabel("Select Camera:")
        layout.addWidget(label)
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 0 (Default)", "Camera 1", "Camera 2"])
        current_index = self.config["camera"].get("camera_index", 0)
        self.camera_combo.setCurrentIndex(current_index)
        layout.addWidget(self.camera_combo)
        
        return widget

    def _create_rtmp_url_widget(self):
        """Widget cho RTMP/RTSP URL"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 5, 0, 5)
        layout.setSpacing(8)
        
        label = QLabel("Stream URL:")
        layout.addWidget(label)
        
        self.stream_url_input = QLineEdit()
        self.stream_url_input.setPlaceholderText("rtmp://192.168.1.100/live/stream or rtsp://...")
        # ✅ CHỈNH KÍCH THƯỚC:
        self.stream_url_input.setMinimumHeight(30)   # Chiều cao tối thiểu
        self.stream_url_input.setStyleSheet("""
            QLineEdit {
                font-size: 12px;
                padding: 6px 8px;
                border-radius: 6px;
                border: 1px solid #cccccc;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
                background-color: #f9fcff;
            }
        """)
        current_url = self.config["camera"].get("stream_url", "")
        self.stream_url_input.setText(current_url)
        layout.addWidget(self.stream_url_input)
        
        hint = QLabel("💡 Examples:\n"
                     "  • RTSP: rtsp://192.168.1.100:8554/live")
        hint.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(hint)
        
        return widget

    def _create_appearance_group(self):
        """Tạo group appearance settings"""
        group = QGroupBox("🎨 Appearance")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        current_theme = self.config.get("ui", {}).get("theme", "dark")
        self.theme_combo.setCurrentText(current_theme.capitalize())
        layout.addWidget(self.theme_combo)
        
        group.setLayout(layout)
        return group

    def _create_advanced_tab(self):
        """Tab Advanced - Developer"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Detection settings
        detection_group = self._create_detection_group()
        layout.addWidget(detection_group)
        
        # Recognition settings
        recognition_group = self._create_recognition_group()
        layout.addWidget(recognition_group)
        
        # Processing settings
        processing_group = self._create_processing_group()
        layout.addWidget(processing_group)
        
        layout.addStretch()
        return widget

    def _create_detection_group(self):
        """Tạo group detection settings"""
        group = QGroupBox("🔍 Detection Settings")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        conf_value = self.config['models']['face_detection']['detection_confidence']
        self.det_conf_label = QLabel(f"Detection Confidence: {conf_value:.2f}")
        self.det_conf_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.det_conf_label)
        
        self.det_conf_slider = QSlider(Qt.Horizontal)
        self.det_conf_slider.setMinimum(10)
        self.det_conf_slider.setMaximum(95)
        self.det_conf_slider.setValue(int(conf_value * 100))
        self.det_conf_slider.valueChanged.connect(
            lambda v: self.det_conf_label.setText(f"Detection Confidence: {v/100:.2f}")
        )
        layout.addWidget(self.det_conf_slider)
        
        hint = QLabel("Lower values detect more faces but may include false positives")
        hint.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(hint)
        
        group.setLayout(layout)
        return group

    def _create_recognition_group(self):
        """Tạo group recognition settings"""
        group = QGroupBox("🎯 Recognition Settings")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        threshold_value = self.config['models']['face_recognition']['recognition_threshold']
        self.rec_threshold_label = QLabel(f"Recognition Threshold: {threshold_value:.2f}")
        self.rec_threshold_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.rec_threshold_label)
        
        self.rec_threshold_slider = QSlider(Qt.Horizontal)
        self.rec_threshold_slider.setMinimum(10)
        self.rec_threshold_slider.setMaximum(80)
        self.rec_threshold_slider.setValue(int(threshold_value * 100))
        self.rec_threshold_slider.valueChanged.connect(
            lambda v: self.rec_threshold_label.setText(f"Recognition Threshold: {v/100:.2f}")
        )
        layout.addWidget(self.rec_threshold_slider)
        
        hint = QLabel("Lower values are more strict, higher values are more lenient")
        hint.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(hint)
        
        group.setLayout(layout)
        return group

    def _create_processing_group(self):
        """Tạo group processing settings"""
        group = QGroupBox("⚡ Processing")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        device_label = QLabel("Device:")
        device_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(device_label)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cuda", "cpu"])
        self.device_combo.setCurrentText(self.config["runtime"]["device"])
        layout.addWidget(self.device_combo)
        
        group.setLayout(layout)
        return group

    def _create_action_buttons(self):
        """Tạo các nút action"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)
        
        self.save_button = QPushButton("💾 Save Settings")
        self.save_button.setObjectName("primaryButton")
        self.save_button.setMinimumWidth(150)
        self.save_button.clicked.connect(self._save_settings)
        layout.addWidget(self.save_button)
        
        return layout

    def _toggle_camera_source(self):
        """Toggle hiển thị Local Camera hoặc RTMP URL"""
        is_local = self.local_camera_radio.isChecked()
        self.local_camera_widget.setVisible(is_local)
        self.rtmp_url_widget.setVisible(not is_local)
    
    def _apply_theme(self):
        """Áp dụng theme"""
        theme_name = self.config.get("ui", {}).get("theme", "dark")
        stylesheet = StyleLoader.load_theme(theme_name)
        self.setStyleSheet(stylesheet)

    def _save_settings(self):
        """Lưu cài đặt"""
        try:
            # General settings
            resolution_map = {0: [640, 480], 1: [1280, 720], 2: [1920, 1080]}
            self.config["camera"]["resolution"] = resolution_map[self.resolution_combo.currentIndex()]
            
            # Camera source
            if self.local_camera_radio.isChecked():
                self.config["camera"]["source_type"] = "local"
                self.config["camera"]["camera_index"] = self.camera_combo.currentIndex()
            else:
                self.config["camera"]["source_type"] = "rtmp"
                stream_url = self.stream_url_input.text().strip()
                
                if not stream_url:
                    QMessageBox.warning(self, "Warning", "⚠ Please enter a valid RTMP/RTSP URL")
                    return
                
                if not (stream_url.startswith("rtmp://") or stream_url.startswith("rtsp://")):
                    QMessageBox.warning(self, "Warning", "⚠ URL must start with rtmp:// or rtsp://")
                    return
                
                self.config["camera"]["stream_url"] = stream_url
            
            # UI settings
            if "ui" not in self.config:
                self.config["ui"] = {}
            self.config["ui"]["theme"] = self.theme_combo.currentText().lower()
            
            # Advanced settings
            self.config["models"]["face_detection"]["detection_confidence"] = self.det_conf_slider.value() / 100
            self.config["models"]["face_recognition"]["recognition_threshold"] = self.rec_threshold_slider.value() / 100
            self.config["runtime"]["device"] = self.device_combo.currentText()
            
            # Update config via ConfigManager
            self.config_manager.update_config(self.config, save_to_file=True)
            
            # Emit signal
            self.settings_applied.emit()
            
            QMessageBox.information(self, "Success", "✓ Settings saved successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{str(e)}")