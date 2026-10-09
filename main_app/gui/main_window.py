"""
Main Window - Modern AI-themed UI với glassmorphism và professional design
"""
from PyQt5.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QStatusBar, QSizePolicy, 
                             QFrame, QGraphicsDropShadowEffect, QGridLayout,
                             QGraphicsBlurEffect)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor
from main_app.utils.style_loader import StyleLoader
from main_app.utils.config_loader import ConfigManager


class MainWindow(QMainWindow):
    """Cửa sổ chính của ứng dụng Face Recognition - Modern AI Design"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.config_manager = ConfigManager()
        self.is_running = False
        self._init_ui()
        self._apply_theme()
        self._connect_signals()

    def _init_ui(self):
        """Khởi tạo giao diện hiện đại"""
        self.setWindowTitle("AI Face Recognition System")
        self.setMinimumSize(1000, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Animated gradient bar
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(32, 32, 32, 32)
        content_layout.setSpacing(24)
        
        # Header với glassmorphism
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Video Container với modern shadow
        video_container = self._create_video_container()
        content_layout.addWidget(video_container, 1)
        
        # Control Buttons với hover effects
        buttons_layout = self._create_control_buttons()
        content_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(content_widget, 1)
        
        # Modern status bar
        self._setup_status_bar()

    def _create_top_bar(self):
        """Thanh gradient AI-themed"""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(3)
        return top_bar

    def _create_header(self):
        """Header với glassmorphism effect"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(140)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(32, 24, 32, 24)
        header_layout.setSpacing(24)
        
        # Left: Icon + Text
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(16)
        
        # AI Icon với gradient background
        icon_container = QFrame()
        icon_container.setObjectName("iconContainer")
        icon_container.setFixedSize(72, 72)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel("🤖")
        icon_label.setObjectName("headerIcon")
        icon_font = QFont()
        icon_font.setPointSize(32)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        left_layout.addWidget(icon_container)
        
        # Title + Subtitle
        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)
        
        title = QLabel("AI Face Recognition")
        title_font = QFont("Inter", 24, QFont.Bold)
        title.setFont(title_font)
        title.setObjectName("mainTitle")
        text_layout.addWidget(title)
        
        subtitle = QLabel("Powered by Deep Learning  •  Manh_duy")
        subtitle_font = QFont("Inter", 11)
        subtitle.setFont(subtitle_font)
        subtitle.setObjectName("subtitle")
        text_layout.addWidget(subtitle)
        
        left_layout.addWidget(text_container)
        left_layout.addStretch()
        
        header_layout.addWidget(left_container, 1)
        
        # Right: Status Card với badge style
        status_card = QFrame()
        status_card.setObjectName("statusCard")
        status_card.setFixedSize(160, 56)
        
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(10)
        
        # Animated status indicator
        self.status_indicator = QFrame()
        self.status_indicator.setObjectName("statusIndicator")
        self.status_indicator.setFixedSize(10, 10)
        status_layout.addWidget(self.status_indicator)
        
        # Status text
        status_text_layout = QVBoxLayout()
        status_text_layout.setSpacing(0)
        status_text_layout.setContentsMargins(0, 0, 0, 0)
        
        self.header_status = QLabel("OFFLINE")
        status_font = QFont("Inter", 10, QFont.Bold)
        self.header_status.setFont(status_font)
        self.header_status.setObjectName("statusText")
        status_text_layout.addWidget(self.header_status)
        
        self.status_subtext = QLabel("Ready")
        subtext_font = QFont("Inter", 8)
        self.status_subtext.setFont(subtext_font)
        self.status_subtext.setObjectName("statusSubtext")
        status_text_layout.addWidget(self.status_subtext)
        
        status_layout.addLayout(status_text_layout)
        status_layout.addStretch()
        
        header_layout.addWidget(status_card)
        
        return header_frame

    def _create_video_container(self):
        """Video Container với modern shadow và border"""
        outer_container = QFrame()
        outer_container.setObjectName("videoOuterContainer")
        outer_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Inner container
        container = QFrame()
        container.setObjectName("videoContainer")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        
        # Video label
        self.video_label = QLabel("🎥 Camera Preview\n\nPress 'Start Detection' to begin")
        self.video_label.setObjectName("videoLabel")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.video_label.setMinimumSize(720, 405)
        
        video_font = QFont("Inter", 13)
        self.video_label.setFont(video_font)
        
        container_layout.addWidget(self.video_label)
        
        # Modern shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 35))
        outer_container.setGraphicsEffect(shadow)
        
        outer_layout.addWidget(container)
        
        return outer_container

    def _create_control_buttons(self):
        """Control Buttons với modern design"""
        buttons_container = QWidget()
        buttons_container.setMaximumHeight(68)
        
        container_layout = QHBoxLayout(buttons_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        button_height = 52
        primary_width = 200
        secondary_width = 150
        
        # Primary Action Button
        self.start_button = QPushButton("▶  Start Detection")
        self.start_button.setObjectName("primaryButton")
        self.start_button.setFixedSize(primary_width, button_height)
        self.start_button.setCursor(Qt.PointingHandCursor)
        btn_font = QFont("Inter", 11, QFont.Bold)
        self.start_button.setFont(btn_font)
        
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(24)
        btn_shadow.setXOffset(0)
        btn_shadow.setYOffset(6)
        btn_shadow.setColor(QColor(59, 130, 246, 60))
        self.start_button.setGraphicsEffect(btn_shadow)
        
        buttons_layout.addWidget(self.start_button)
        
        # Secondary Buttons
        secondary_buttons = [
            ("➕  Add Person", "add_person_button"),
            ("📊  History", "history_button"),
            ("⚙  Settings", "settings_button")
        ]
        
        for text, attr_name in secondary_buttons:
            btn = QPushButton(text)
            btn.setObjectName("secondaryButton")
            btn.setFixedSize(secondary_width, button_height)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(btn_font)
            buttons_layout.addWidget(btn)
            setattr(self, attr_name, btn)
        
        container_layout.addStretch()
        container_layout.addLayout(buttons_layout)
        container_layout.addStretch()
        
        layout = QVBoxLayout()
        layout.addWidget(buttons_container)
        
        return layout

    def _setup_status_bar(self):
        """Modern status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.setContentsMargins(24, 8, 24, 8)
        
        self.status_message = QLabel("●  System Ready")
        status_font = QFont("Inter", 9)
        self.status_message.setFont(status_font)
        self.status_bar.addWidget(self.status_message)
        
        self.status_bar.addWidget(QLabel(""), 1)
        
        self.recognition_label = QLabel("")
        self.recognition_label.setFont(status_font)
        self.status_bar.addPermanentWidget(self.recognition_label)

    def _connect_signals(self):
        """Kết nối signals"""
        self.config_manager.theme_changed.connect(self._on_theme_changed)

    def _apply_theme(self, theme_name=None):
        """Modern AI-themed styling"""
        if theme_name is None:
            theme_name = self.config.get("ui", {}).get("theme", "light")
        
        modern_theme = """
            /* Main Window - Neural Network Inspired Background */
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f172a, stop:0.3 #1e293b, stop:0.7 #0f172a, stop:1 #020617);
            }
            
            /* Animated Top Bar */
            #topBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:0.25 #8b5cf6, 
                    stop:0.5 #ec4899, stop:0.75 #8b5cf6, stop:1 #3b82f6);
            }
            
            #contentArea {
                background: transparent;
            }
            
            /* Header - Glassmorphism Card */
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(59, 130, 246, 0.08), stop:1 rgba(139, 92, 246, 0.08));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
            
            /* Icon Container */
            #iconContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            
            #headerIcon, #mainTitle {
                color: #f8fafc;
            }
            
            #subtitle {
                color: #94a3b8;
                letter-spacing: 0.3px;
            }
            
            /* Status Card - Badge Style */
            #statusCard {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }
            
            #statusIndicator {
                background: #ef4444;
                border-radius: 5px;
                border: 2px solid rgba(239, 68, 68, 0.3);
            }
            
            #statusText {
                color: #e2e8f0;
                letter-spacing: 1px;
            }
            
            #statusSubtext {
                color: #64748b;
            }
            
            /* Video Container - Modern Card */
            #videoOuterContainer {
                background: transparent;
            }
            
            #videoContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 41, 59, 0.95), stop:1 rgba(15, 23, 42, 0.95));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 24px;
            }
            
            #videoLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border-radius: 20px;
                color: #64748b;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            /* Primary Button - AI Gradient */
            #primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            
            #primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #7c3aed);
            }
            
            #primaryButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1d4ed8, stop:1 #6d28d9);
            }
            
            /* Secondary Buttons - Glass Effect */
            #secondaryButton {
                background: rgba(30, 41, 59, 0.8);
                color: #e2e8f0;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                font-weight: 600;
            }
            
            #secondaryButton:hover {
                background: rgba(51, 65, 85, 0.9);
                border: 1px solid rgba(59, 130, 246, 0.5);
                color: #60a5fa;
            }
            
            #secondaryButton:pressed {
                background: rgba(30, 41, 59, 0.95);
                border: 1px solid rgba(59, 130, 246, 0.7);
            }
            
            /* Status Bar - Modern Footer */
            QStatusBar {
                background: rgba(15, 23, 42, 0.95);
                color: #94a3b8;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }
            
            QStatusBar QLabel {
                color: #cbd5e1;
            }
        """
        
        self.setStyleSheet(modern_theme)
        self.config = self.config_manager.get_config()

    def _on_theme_changed(self, theme_name):
        """Callback khi theme thay đổi"""
        self._apply_theme(theme_name)
        self.status_message.setText(f"●  Theme: {theme_name.upper()}")

    def update_video(self, qpixmap):
        """Cập nhật video preview"""
        if qpixmap:
            scaled_pixmap = qpixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)
            self.video_label.setAlignment(Qt.AlignCenter)
        else:
            self.video_label.clear()
            self.video_label.setText("⚠️  Camera Error\n\nPlease check your camera connection")
            self._update_status("●  Camera Error", "")

    def _update_status(self, message, recognition_info=""):
        """Cập nhật status bar"""
        self.status_message.setText(message)
        self.recognition_label.setText(recognition_info)

    def set_camera_running(self, running):
        """Cập nhật trạng thái camera với animations"""
        self.is_running = running
        
        if running:
            self.start_button.setText("⏹  Stop Detection")
            
            stop_shadow = QGraphicsDropShadowEffect()
            stop_shadow.setBlurRadius(24)
            stop_shadow.setXOffset(0)
            stop_shadow.setYOffset(6)
            stop_shadow.setColor(QColor(239, 68, 68, 60))
            self.start_button.setGraphicsEffect(stop_shadow)
            
            self.start_button.setStyleSheet("""
                #primaryButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ef4444, stop:1 #dc2626);
                }
                #primaryButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #f87171, stop:1 #ef4444);
                }
                #primaryButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #b91c1c, stop:1 #991b1b);
                }
            """)
            
            self._update_status("●  AI Detection Active", "")
            self.status_indicator.setStyleSheet("""
                background: #10b981;
                border: 2px solid rgba(16, 185, 129, 0.3);
            """)
            self.header_status.setText("ONLINE")
            self.status_subtext.setText("Monitoring")
        else:
            self.start_button.setText("▶  Start Detection")
            
            start_shadow = QGraphicsDropShadowEffect()
            start_shadow.setBlurRadius(24)
            start_shadow.setXOffset(0)
            start_shadow.setYOffset(6)
            start_shadow.setColor(QColor(59, 130, 246, 60))
            self.start_button.setGraphicsEffect(start_shadow)
            
            self.start_button.setStyleSheet("")
            self._update_status("●  System Ready", "")
            self.status_indicator.setStyleSheet("""
                background: #ef4444;
                border: 2px solid rgba(239, 68, 68, 0.3);
            """)
            self.header_status.setText("OFFLINE")
            self.status_subtext.setText("Ready")

    def show_recognition(self, person_name):
        if person_name and person_name != "Unknown":
            self._update_status(
                "●  AI Detection Active", 
                f"✓  Identified: {person_name}"
            )
        elif person_name == "Unknown":
            self._update_status(
                "●  AI Detection Active", 
                "⚠  Unknown Person"
            )
        else:
            self._update_status("●  AI Detection Active", "")