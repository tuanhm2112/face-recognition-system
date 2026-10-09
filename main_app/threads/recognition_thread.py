import time
from PyQt5.QtCore import QThread, pyqtSignal
from collections import defaultdict
from main_app.utils.logger import Logger
from main_app.services.history_service import HistoryService


class RecognitionThread(QThread):
    faces_recognized = pyqtSignal(object, list, list, list)
    history_save_requested = pyqtSignal(str, object, object)
    max_history = 15
    skip_frame = 15
    UNKNOWN_RETRY_INTERVAL = 1.0

    def __init__(self, recognizer, config, recognition_queue):
        super().__init__()
        self.recognizer = recognizer
        self.config = config
        self.recognition_queue = recognition_queue
        self.running = False
        self.logger = Logger("logs/app.log", "ERROR")
        self.history_service = HistoryService()
        self.history = defaultdict(list)
        self.final_ids = {}
        self.frame_count = defaultdict(int)
        self._unknown_finalized_time = {}
        self._was_previously_unknown = set()

    def run(self):
        self.running = True
        while self.running:
            try:
                frame, boxes, embeddings, track_ids = self.recognition_queue.get(timeout=1.0)
                person_ids = self._recognize_faces(frame, boxes, embeddings, track_ids)
                if person_ids:
                    self.faces_recognized.emit(frame, boxes, person_ids, track_ids)
                self.recognition_queue.task_done()
            except:
                pass

    def _recognize_faces(self, frame, boxes, embeddings, track_ids):
        person_ids = []
        current_threshold = self.config["models"]["face_recognition"]["recognition_threshold"]
        now = time.time()

        for i, (embedding, track_id) in enumerate(zip(embeddings, track_ids)):
            try:
                self.frame_count[track_id] += 1

                if self.frame_count[track_id] <= self.skip_frame:
                    person_ids.append(None)
                    continue

                if track_id in self.final_ids:
                    current_final = self.final_ids[track_id]
                    if current_final == "Unknown":
                        finalized_at = self._unknown_finalized_time.get(track_id, 0)
                        if now - finalized_at >= self.UNKNOWN_RETRY_INTERVAL:
                            del self.final_ids[track_id]
                            self.history[track_id].clear()
                            self.frame_count[track_id] = self.skip_frame + 1
                            self._was_previously_unknown.add(track_id)
                        else:
                            person_ids.append("Unknown")
                            continue
                    else:
                        person_ids.append(current_final)
                        continue

                person_name, confidence = self.recognizer.search(embedding, current_threshold)
                self.history[track_id].append((person_name, confidence))
                if len(self.history[track_id]) > self.max_history:
                    self.history[track_id].pop(0)

                if self.frame_count[track_id] >= self.max_history + self.skip_frame:
                    name_count = defaultdict(int)
                    for name, _ in self.history[track_id]:
                        name_count[name] += 1
                    final_name = max(name_count.items(), key=lambda x: x[1])[0]
                    self.final_ids[track_id] = final_name

                    if final_name == "Unknown":
                        self._unknown_finalized_time[track_id] = now
                        if track_id not in self._was_previously_unknown:
                            self.history_save_requested.emit(final_name, frame, boxes[i])
                    else:
                        self.history_save_requested.emit(final_name, frame, boxes[i])
                        self._unknown_finalized_time.pop(track_id, None)
                        self._was_previously_unknown.discard(track_id)
                    person_ids.append(final_name)
                else:
                    person_ids.append(None)

            except Exception as e:
                person_ids.append(None)
                self.history[track_id].append(("Unknown", 0.0))
                if len(self.history[track_id]) > self.max_history:
                    self.history[track_id].pop(0)
                self.logger.log_error(f"Recognition error: {str(e)}")

        active_track_ids = set(track_ids)
        for tid in list(self.history.keys()):
            if tid not in active_track_ids:
                del self.history[tid]
                self.final_ids.pop(tid, None)
                self.frame_count.pop(tid, None)
                self._unknown_finalized_time.pop(tid, None)
                self._was_previously_unknown.discard(tid)

        return person_ids

    def stop(self):
        self.running = False
        self.wait()
