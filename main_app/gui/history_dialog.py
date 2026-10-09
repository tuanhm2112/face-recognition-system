"""
History Dialog - Dark AI-Inspired Theme với Glassmorphism
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QScrollArea, 
                             QWidget, QFrame, QHBoxLayout, QDateEdit, 
                             QTimeEdit, QPushButton, QGraphicsDropShadowEffect, QGridLayout, QSizePolicy)

from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QColor
import datetime
import os
import cv2
from main_app.utils.image_utils import ImageUtils
from main_app.services.history_service import HistoryService
from main_app.utils.style_loader import StyleLoader
from main_app.utils.config_loader import ConfigManager


class HistoryDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_service = HistoryService()
        self.setWindowTitle("Recognition History")
        self.setMinimumSize(900, 850)
        
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowMinMaxButtonsHint | 
            Qt.WindowCloseButtonHint
        )
        
        self._init_ui()
        self._load_history()
        self._apply_theme()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_bar.setFixedHeight(4)
        main_layout.addWidget(top_bar)
        
        content_widget = QWidget()
        content_widget.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)

        header = self._create_header()
        content_layout.addWidget(header)

        search_panel = self._create_search_panel()
        content_layout.addWidget(search_panel)

        results_widget = self._create_results_area()
        content_layout.addWidget(results_widget, 1)
        
        main_layout.addWidget(content_widget, 1)

    def _create_header(self):
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(100)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(0)
        header_layout.setAlignment(Qt.AlignVCenter)

        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        left_layout.setAlignment(Qt.AlignVCenter)

        icon = QLabel("🤖")
        icon_font = QFont()
        icon_font.setPointSize(28)
        icon.setFont(icon_font)
        icon.setObjectName("headerIcon")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(icon)

        text_container = QWidget()
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        text_layout.setAlignment(Qt.AlignVCenter)

        title = QLabel("Recognition History")
        title_font = QFont("Inter", 19, QFont.Bold)
        title.setFont(title_font)
        title.setObjectName("mainTitle")
        text_layout.addWidget(title)

        subtitle = QLabel("AI Recognition Records • Advanced Analytics")
        subtitle_font = QFont("Inter", 9)
        subtitle.setFont(subtitle_font)
        subtitle.setObjectName("subtitle")
        text_layout.addWidget(subtitle)

        left_layout.addWidget(text_container)
        header_layout.addWidget(left_container, 1)

        self.count_badge = QLabel("73 RECORDS")
        self.count_badge.setObjectName("countBadge")
        self.count_badge.setFixedSize(140, 50)
        self.count_badge.setAlignment(Qt.AlignCenter)
        count_font = QFont("Inter", 10, QFont.Bold)
        count_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)
        self.count_badge.setFont(count_font)

        badge_shadow = QGraphicsDropShadowEffect()
        badge_shadow.setBlurRadius(24)
        badge_shadow.setXOffset(0)
        badge_shadow.setYOffset(4)
        badge_shadow.setColor(QColor(59, 130, 246, 100))
        self.count_badge.setGraphicsEffect(badge_shadow)

        header_layout.addWidget(self.count_badge, 0, Qt.AlignVCenter)

        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(40)
        header_shadow.setXOffset(0)
        header_shadow.setYOffset(8)
        header_shadow.setColor(QColor(0, 0, 0, 60))
        header_frame.setGraphicsEffect(header_shadow)

        return header_frame

    def _create_search_panel(self):
        search_frame = QFrame()
        search_frame.setObjectName("searchPanel")
        search_frame.setMinimumHeight(190)
        
        panel_shadow = QGraphicsDropShadowEffect()
        panel_shadow.setBlurRadius(32)
        panel_shadow.setXOffset(0)
        panel_shadow.setYOffset(6)
        panel_shadow.setColor(QColor(0, 0, 0, 40))
        search_frame.setGraphicsEffect(panel_shadow)
        
        panel_layout = QVBoxLayout(search_frame)
        panel_layout.setContentsMargins(30, 25, 30, 25)
        panel_layout.setSpacing(20)
        
        panel_title = QLabel("🔍 Search by Time Range")
        title_font = QFont("Inter", 13, QFont.Bold)
        panel_title.setFont(title_font)
        panel_title.setObjectName("panelTitle")
        panel_layout.addWidget(panel_title)
        
        controls_container = QWidget()
        controls_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        grid_layout = QGridLayout(controls_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)
        
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 0)
        grid_layout.setColumnStretch(3, 2)
        grid_layout.setColumnStretch(4, 1)
        grid_layout.setColumnStretch(5, 2)

        from_label = QLabel("From:")
        from_label_font = QFont("Inter", 10, QFont.Bold)
        from_label.setFont(from_label_font)
        from_label.setObjectName("fieldLabel")
        grid_layout.addWidget(from_label, 0, 0, 1, 2, Qt.AlignLeft)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setMinimumSize(160, 50)
        self.start_date_edit.setMaximumWidth(220)
        self.start_date_edit.setObjectName("dateEdit")
        self.start_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.start_date_edit, 1, 0)

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime(0, 0))
        self.start_time_edit.setButtonSymbols(QTimeEdit.UpDownArrows)
        self.start_time_edit.setMinimumSize(100, 50)
        self.start_time_edit.setMaximumWidth(140)
        self.start_time_edit.setObjectName("timeEdit")
        self.start_time_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.start_time_edit, 1, 1)

        arrow = QLabel("→")
        arrow_font = QFont()
        arrow_font.setPointSize(24)
        arrow.setFont(arrow_font)
        arrow.setObjectName("separator")
        arrow.setAlignment(Qt.AlignCenter)
        arrow.setFixedWidth(50)
        grid_layout.addWidget(arrow, 1, 2, Qt.AlignCenter)

        to_label = QLabel("To:")
        to_label_font = QFont("Inter", 10, QFont.Bold)
        to_label.setFont(to_label_font)
        to_label.setObjectName("fieldLabel")
        grid_layout.addWidget(to_label, 0, 3, 1, 2, Qt.AlignLeft)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setMinimumSize(160, 50)
        self.end_date_edit.setMaximumWidth(220)
        self.end_date_edit.setObjectName("dateEdit")
        self.end_date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.end_date_edit, 1, 3)

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.end_time_edit.setTime(QTime(23, 59))
        self.end_time_edit.setButtonSymbols(QTimeEdit.UpDownArrows)
        self.end_time_edit.setMinimumSize(100, 50)
        self.end_time_edit.setMaximumWidth(140)
        self.end_time_edit.setObjectName("timeEdit")
        self.end_time_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        grid_layout.addWidget(self.end_time_edit, 1, 4)

        search_button = QPushButton("🔍  SEARCH")
        search_button.setObjectName("primaryButton")
        search_button.clicked.connect(self._load_history)
        search_button.setMinimumSize(150, 50)
        search_button.setMaximumWidth(200)
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_font = QFont("Inter", 11, QFont.Bold)
        btn_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        search_button.setFont(btn_font)

        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(24)
        btn_shadow.setXOffset(0)
        btn_shadow.setYOffset(4)
        btn_shadow.setColor(QColor(59, 130, 246, 120))
        search_button.setGraphicsEffect(btn_shadow)

        grid_layout.addWidget(search_button, 1, 5, Qt.AlignVCenter)

        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.addStretch(1)
        center_layout.addWidget(controls_container)
        center_layout.addStretch(1)
        
        panel_layout.addLayout(center_layout)
        panel_layout.addStretch()

        return search_frame

    def _create_results_area(self):
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(20)

        self.results_label = QLabel("Search results")
        results_font = QFont("Inter", 11, QFont.Bold)
        self.results_label.setFont(results_font)
        self.results_label.setObjectName("resultsLabel")
        results_layout.addWidget(self.results_label)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("scrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.container.setObjectName("scrollContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        self.container_layout.setSpacing(15)
        
        self.scroll.setWidget(self.container)
        results_layout.addWidget(self.scroll)

        return results_widget

    def _load_history(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        start_date = self.start_date_edit.date().toPyDate()
        start_time = self.start_time_edit.time().toPyTime()
        end_date = self.end_date_edit.date().toPyDate()
        end_time = self.end_time_edit.time().toPyTime()

        start_datetime = datetime.datetime.combine(start_date, start_time)
        end_datetime = datetime.datetime.combine(end_date, end_time)

        history = self.history_service.get_history()
        filtered_history = [
            entry for entry in history
            if start_datetime <= datetime.datetime.strptime(
                entry["timestamp"], "%Y-%m-%d %H:%M:%S"
            ) <= end_datetime
        ]

        count = len(filtered_history)
        self.results_label.setText(f"📊 Search results: {count} record(s)")
        self.count_badge.setText(f"{count} RECORDS")

        if not filtered_history:
            self._show_no_results()
        else:
            for entry in filtered_history:
                card = self._create_history_card(entry)
                self.container_layout.addWidget(card)

    def _show_no_results(self):
        no_result_frame = QFrame()
        no_result_frame.setObjectName("noResultFrame")
        no_result_layout = QVBoxLayout(no_result_frame)
        no_result_layout.setAlignment(Qt.AlignCenter)
        no_result_layout.setSpacing(15)
        
        icon = QLabel("🔍")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon.setFont(icon_font)
        icon.setAlignment(Qt.AlignCenter)
        no_result_layout.addWidget(icon)
        
        no_result = QLabel("No records found")
        no_result.setAlignment(Qt.AlignCenter)
        no_result_font = QFont("Inter", 14, QFont.Bold)
        no_result.setFont(no_result_font)
        no_result.setObjectName("noResultText")
        no_result_layout.addWidget(no_result)
        
        hint = QLabel("Try adjusting your search time range")
        hint.setAlignment(Qt.AlignCenter)
        hint_font = QFont("Inter", 10)
        hint.setFont(hint_font)
        hint.setObjectName("noResultHint")
        no_result_layout.addWidget(hint)
        
        self.container_layout.addWidget(no_result_frame)

    def _create_history_card(self, entry):
        card = QFrame()
        card.setObjectName("historyCard")
        card.setFixedHeight(180)
        
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(24)
        card_shadow.setXOffset(0)
        card_shadow.setYOffset(4)
        card_shadow.setColor(QColor(0, 0, 0, 50))
        card.setGraphicsEffect(card_shadow)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(25)

        thumbnail = self._create_thumbnail(entry)
        card_layout.addWidget(thumbnail)

        info_widget = self._create_info_section(entry)
        card_layout.addWidget(info_widget, 1)

        return card

    def _create_thumbnail(self, entry):
        img_container = QFrame()
        img_container.setObjectName("thumbnailContainer")
        img_container.setFixedSize(140, 140)
        
        img_layout = QVBoxLayout(img_container)
        img_layout.setContentsMargins(8, 8, 8, 8)
        
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setFixedSize(124, 124)
        img_label.setObjectName("thumbnailLabel")
        
        if os.path.exists(entry["img_path"]):
            frame_cv = cv2.imread(entry["img_path"])
            if frame_cv is not None:
                qpixmap = ImageUtils.cv2_to_qpixmap(frame_cv)
                img_label.setPixmap(
                    qpixmap.scaled(124, 124, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
        else:
            img_label.setText("❌\nImage not\navailable")
            img_label.setStyleSheet("color: #64748b; font-size: 11px;")
        
        img_layout.addWidget(img_label)
        return img_container

    def _create_info_section(self, entry):
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 5, 0, 5)
        info_layout.setSpacing(12)

        name_layout = QHBoxLayout()
        name_layout.setSpacing(10)
        
        person_name = entry['person_name'] if entry['person_name'] != 'Unknown' else 'Unknown Person'
        is_unknown = entry['person_name'] == 'Unknown'
        
        name_label = QLabel(f"{'❓' if is_unknown else '👤'} {person_name}")
        name_font = QFont("Inter", 14, QFont.Bold)
        name_label.setFont(name_font)
        name_label.setObjectName("personName")
        name_layout.addWidget(name_label)
        
        if is_unknown:
            badge = QLabel("UNKNOWN")
            badge.setObjectName("unknownBadge")
            badge_font = QFont("Inter", 8, QFont.Bold)
            badge_font.setLetterSpacing(QFont.AbsoluteSpacing, 1.0)
            badge.setFont(badge_font)
            name_layout.addWidget(badge)
        
        name_layout.addStretch()
        info_layout.addLayout(name_layout)
        
        time_label = QLabel(f"🕒 {entry['timestamp']}")
        time_font = QFont("Inter", 12)
        time_label.setFont(time_font)
        time_label.setObjectName("timeLabel")
        info_layout.addWidget(time_label)
        
        path_label = QLabel(f"📁 {entry['img_path']}")
        path_font = QFont("Inter", 9)
        path_label.setFont(path_font)
        path_label.setObjectName("pathLabel")
        path_label.setWordWrap(True)
        info_layout.addWidget(path_label)
        
        info_layout.addStretch()
        
        return info_widget

    def _apply_theme(self):
        dark_ai_theme = """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0e1a, stop:0.5 #1a1530, stop:1 #0f1419);
            }
            
            #topBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:0.5 #8b5cf6, stop:1 #3b82f6);
            }
            
            #contentArea {
                background: transparent;
            }
            
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.15), 
                    stop:0.5 rgba(139, 92, 246, 0.15), 
                    stop:1 rgba(59, 130, 246, 0.15));
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 20px;
            }
            
            #headerIcon, #mainTitle {
                color: #f8fafc;
            }
            
            #subtitle {
                color: #94a3b8;
            }
            
            #countBadge {
                background: rgba(59, 130, 246, 0.2);
                color: #f8fafc;
                border-radius: 16px;
                border: 1px solid rgba(59, 130, 246, 0.5);
            }
            
            #searchPanel {
                background: rgba(20, 24, 35, 0.7);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 20px;
            }
            
            #panelTitle, #resultsLabel {
                color: #e2e8f0;
            }
            
            #fieldLabel {
                color: #94a3b8;
            }
            
            #separator {
                color: #64748b;
            }
            
            #dateEdit, #timeEdit {
                background: rgba(15, 20, 30, 0.9);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
                padding: 8px 12px;
                color: #e2e8f0;
                font-size: 12px;
                font-weight: 500;
            }
            
            #dateEdit:hover, #timeEdit:hover {
                border-color: rgba(59, 130, 246, 0.5);
                background: rgba(20, 25, 35, 1);
            }
            
            #dateEdit:focus, #timeEdit:focus {
                border-color: #3b82f6;
                background: rgba(20, 25, 35, 1);
            }
            
            #dateEdit::drop-down, #timeEdit::up-button, #timeEdit::down-button {
                background: rgba(59, 130, 246, 0.2);
                border: none;
                border-radius: 6px;
            }
            
            #dateEdit::drop-down:hover, #timeEdit::up-button:hover, #timeEdit::down-button:hover {
                background: rgba(59, 130, 246, 0.4);
            }
            
            #primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3b82f6, stop:1 #8b5cf6);
                color: #ffffff;
                border: none;
                border-radius: 14px;
                font-weight: 600;
            }
            
            #primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60a5fa, stop:1 #a78bfa);
            }
            
            #primaryButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #7c3aed);
            }
            
            #scrollArea {
                background: transparent;
                border: none;
            }
            
            #scrollContainer {
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: rgba(20, 24, 35, 0.5);
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(59, 130, 246, 0.5);
                border-radius: 5px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(59, 130, 246, 0.7);
            }
            
            #historyCard {
                background: rgba(20, 24, 35, 0.7);
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 18px;
            }
            
            #historyCard:hover {
                border-color: rgba(59, 130, 246, 0.5);
                background: rgba(25, 30, 42, 0.8);
            }
            
            #thumbnailContainer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(20, 24, 35, 0.9), 
                    stop:1 rgba(10, 14, 26, 0.9));
                border: 2px solid rgba(59, 130, 246, 0.3);
                border-radius: 14px;
            }
            
            #thumbnailLabel {
                border-radius: 10px;
                background: rgba(10, 14, 26, 0.6);
            }
            
            #personName {
                color: #f8fafc;
            }
            
            #timeLabel {
                color: #94a3b8;
            }
            
            #pathLabel {
                color: #64748b;
            }
            
            #unknownBadge {
                background: rgba(234, 179, 8, 0.2);
                color: #fde047;
                padding: 4px 10px;
                border-radius: 10px;
                border: 1px solid rgba(234, 179, 8, 0.4);
            }
            
            #noResultFrame {
                background: rgba(20, 24, 35, 0.5);
                border: 2px dashed rgba(59, 130, 246, 0.3);
                border-radius: 20px;
                padding: 60px;
            }
            
            #noResultText {
                color: #cbd5e1;
            }
            
            #noResultHint {
                color: #94a3b8;
            }
            
            QCalendarWidget {
                background: rgba(20, 24, 35, 0.95);
                color: #e2e8f0;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 12px;
            }
            
            QCalendarWidget QToolButton {
                color: #e2e8f0;
                background: rgba(59, 130, 246, 0.2);
                border: none;
                border-radius: 6px;
                padding: 5px;
            }
            
            QCalendarWidget QToolButton:hover {
                background: rgba(59, 130, 246, 0.4);
            }
            
            QCalendarWidget QMenu {
                background: rgba(20, 24, 35, 0.95);
                color: #e2e8f0;
                border: 1px solid rgba(59, 130, 246, 0.3);
            }
            
            QCalendarWidget QSpinBox {
                background: rgba(15, 20, 30, 0.9);
                color: #e2e8f0;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 6px;
                padding: 3px;
            }
            
            QCalendarWidget QAbstractItemView {
                background: rgba(10, 14, 26, 0.9);
                color: #e2e8f0;
                selection-background-color: rgba(59, 130, 246, 0.5);
                selection-color: #ffffff;
            }
        """
        
        self.setStyleSheet(dark_ai_theme)