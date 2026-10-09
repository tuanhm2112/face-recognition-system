"""
Display Handler - Xử lý hiển thị kết quả (KHÔNG phải QThread)
"""
from PyQt5.QtCore import QObject, pyqtSignal
from main_app.utils.image_utils import ImageUtils
from main_app.utils.logger import Logger

class DisplayHandler(QObject):

    frame_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.logger = Logger("logs/app.log", "ERROR")

    def display_results(self, frame, boxes, person_ids, track_ids=None):

        try:
            frame_with_boxes = ImageUtils.draw_bounding_boxes_with_tracking(frame, boxes, person_ids, track_ids)
            qpixmap = ImageUtils.cv2_to_qpixmap(frame_with_boxes)
            self.frame_ready.emit(qpixmap)
        except Exception as e:
            self.logger.log_error(f"Display error: {str(e)}")
    
    def display_raw_frame(self, qpixmap):

        try:
            self.frame_ready.emit(qpixmap)
        except Exception as e:
            self.logger.log_error(f"Raw frame display error: {str(e)}")