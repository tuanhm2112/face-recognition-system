import cv2
import time
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class ImageUtils:

    _blink_state = True
    _last_blink_time = 0
    _BLINK_INTERVAL = 0.35

    @staticmethod
    def preprocess_image(image):
        image = cv2.convertScaleAbs(image, alpha=1.1, beta=10)
        image = cv2.GaussianBlur(image, (5, 5), 0)
        return image

    @staticmethod
    def _draw_corner_brackets(image, x1, y1, x2, y2, color, thickness=2, corner_length_ratio=0.25):
        w = x2 - x1
        h = y2 - y1
        corner_len = max(int(min(w, h) * corner_length_ratio), 10)

        cv2.line(image, (x1, y1), (x1 + corner_len, y1), color, thickness)
        cv2.line(image, (x1, y1), (x1, y1 + corner_len), color, thickness)

        cv2.line(image, (x2, y1), (x2 - corner_len, y1), color, thickness)
        cv2.line(image, (x2, y1), (x2, y1 + corner_len), color, thickness)

        cv2.line(image, (x1, y2), (x1 + corner_len, y2), color, thickness)
        cv2.line(image, (x1, y2), (x1, y2 - corner_len), color, thickness)

        cv2.line(image, (x2, y2), (x2 - corner_len, y2), color, thickness)
        cv2.line(image, (x2, y2), (x2, y2 - corner_len), color, thickness)

    @staticmethod
    def _update_blink():
        now = time.time()
        if now - ImageUtils._last_blink_time >= ImageUtils._BLINK_INTERVAL:
            ImageUtils._blink_state = not ImageUtils._blink_state
            ImageUtils._last_blink_time = now

    @staticmethod
    def _is_recognized(person_id):
        if not person_id:
            return False
        return person_id.lower() not in ("unknown", "")

    @staticmethod
    def draw_bounding_boxes(image, boxes, person_ids):
        ImageUtils._update_blink()

        for box, person_id in zip(boxes, person_ids):
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])

            if ImageUtils._is_recognized(person_id):
                color = (0, 255, 0)
                ImageUtils._draw_corner_brackets(image, x1, y1, x2, y2, color, thickness=2)
                cv2.putText(image, person_id, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            else:
                if ImageUtils._blink_state:
                    color = (0, 0, 255)
                    ImageUtils._draw_corner_brackets(image, x1, y1, x2, y2, color, thickness=2)

        return image

    @staticmethod
    def draw_bounding_boxes_with_tracking(image, boxes, person_ids, track_ids=None):
        ImageUtils._update_blink()

        for i, (box, person_id) in enumerate(zip(boxes, person_ids)):
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])

            if ImageUtils._is_recognized(person_id):
                color = (0, 255, 0)
                ImageUtils._draw_corner_brackets(image, x1, y1, x2, y2, color, thickness=2)

                label = person_id
                (text_w, text_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )
                cv2.rectangle(
                    image,
                    (x1, y1 - text_h - baseline - 8),
                    (x1 + text_w + 4, y1 - 2),
                    (0, 0, 0),
                    cv2.FILLED,
                )
                cv2.putText(
                    image, label, (x1 + 2, y1 - baseline - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
                )
            else:
                if ImageUtils._blink_state:
                    color = (0, 0, 255)
                    ImageUtils._draw_corner_brackets(image, x1, y1, x2, y2, color, thickness=2)

        return image

    @staticmethod
    def cv2_to_qpixmap(image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, c = image.shape
        qimage = QImage(image.data, w, h, w * c, QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)