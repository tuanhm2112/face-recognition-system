import sys
import torch
import threading
from PyQt5.QtWidgets import QApplication, QMessageBox
from main_app.utils.config_loader import ConfigManager
from main_app.utils.logger import Logger
from main_app.gui.main_window import MainWindow
from main_app.core.model_manager import ModelManager
from main_app.core.thread_manager import ThreadManager
from main_app.services.history_service import HistoryService


class FaceRecognitionApp:
    def __init__(self):
        print("Initializing application...")
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()
        self.device = None
        print("Creating logger...")
        self.logger = Logger(self.config["runtime"]["log_path"], self.config["runtime"]["log_level"])
        print("Initializing history service...")
        self.history_service = HistoryService()
        print("Initializing GUI...")
        self._init_components()
        print("Setting up connections...")
        self._setup_connections()
        self._connect_config_signals()
        print("Application initialized successfully")

    def _check_cuda_safe(self, timeout=3):
        """Check CUDA với timeout để tránh treo"""
        result = [False]
        exception = [None]
        def check():
            try:
                result[0] = torch.cuda.is_available()
            except Exception as e:
                exception[0] = e
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
        thread.join(timeout)
        return result[0] if not exception[0] else False

    def _log_device_info(self):
        if self.device and self._check_cuda_safe():
            try:
                self.logger.log_info(f"GPU: {torch.cuda.get_device_name(0)}")
            except Exception:
                self.logger.log_info("GPU detected")
        else:
            self.logger.log_warning("Using CPU")

    def _init_components(self):
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self.config)
        self.model_manager = None
        self.models = None
        self.recognizer = None
        self.thread_manager = None

    def _setup_connections(self):
        self.main_window.start_button.clicked.connect(self._toggle_camera)
        self.main_window.add_person_button.clicked.connect(self._open_add_person_dialog)
        self.main_window.settings_button.clicked.connect(self._open_settings_dialog)
        self.main_window.history_button.clicked.connect(self._open_history_dialog)

    def _connect_config_signals(self):
        self.config_manager.camera_changed.connect(self._on_camera_changed)
        self.config_manager.model_changed.connect(self._on_model_changed)

    def _ensure_models_loaded(self):
        if self.models is not None and self.recognizer is not None and self.thread_manager is not None:
            return
        try:
            print("Checking CUDA...")
            cuda_available = self._check_cuda_safe()
            self.device = torch.device("cuda" if cuda_available else "cpu")
            print(f"Using device: {self.device}")
            self._log_device_info()
            print("Loading models...")
            self.model_manager = ModelManager(self.config, self.device)
            self.models = self.model_manager.get_models()
            self.recognizer = self.model_manager.get_recognizer()
            print("Creating thread manager...")
            self.thread_manager = ThreadManager(self.config, self.models, self.device, self.recognizer)
            try:
                self.thread_manager.connect_signals(self.main_window, self._display_results)
            except Exception:
                pass
            try:
                if 'recognition' in self.thread_manager.threads:
                    self.thread_manager.threads['recognition'].history_save_requested.connect(self._save_history_slot)
            except Exception:
                pass
            print("Models loaded successfully")
        except Exception as e:
            msg = f"Failed to load models: {e}"
            print(f"ERROR: {msg}")
            self.logger.log_error(msg)
            QMessageBox.critical(self.main_window, "Model Load Error", f"{msg}\nSee logs for details.")
            raise

    def _toggle_camera(self):
        if not self.main_window.is_running:
            self._start_camera()
        else:
            self._stop_camera()

    def _start_camera(self):
        try:
            if self.device is None or self.models is None or self.recognizer is None or self.thread_manager is None:
                self._ensure_models_loaded()
            self.thread_manager.start()
            self.main_window.set_camera_running(True)
        except Exception as e:
            try:
                self.main_window._update_status(f"Error: {str(e)}")
            except Exception:
                pass
            self.logger.log_error(f"_start_camera error: {e}")

    def _stop_camera(self):
        try:
            if self.thread_manager:
                self.thread_manager.stop()
        except Exception as e:
            self.logger.log_error(f"_stop_camera error: {e}")
        finally:
            try:
                self.main_window.set_camera_running(False)
            except Exception:
                pass

    def _open_add_person_dialog(self):
        try:
            if self.models is None:
                self._ensure_models_loaded()
            from main_app.gui.add_person_dialog import AddPersonDialog
            dialog = AddPersonDialog(self.config, self.models, self.device, self.recognizer)
            dialog.person_added.connect(self._on_person_added)
            dialog.person_deleted.connect(self._on_person_deleted)
            dialog.exec_()
        except Exception as e:
            self.logger.log_error(f"_open_add_person_dialog error: {e}")
            QMessageBox.warning(self.main_window, "Open Dialog Failed", f"Could not open Add Person dialog:\n{e}")

    def _open_settings_dialog(self):
        try:
            from main_app.gui.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self.config)
            dialog.settings_applied.connect(self._on_settings_applied)
            dialog.exec_()
        except Exception as e:
            self.logger.log_error(f"_open_settings_dialog error: {e}")
            QMessageBox.warning(self.main_window, "Open Dialog Failed", f"Could not open Settings dialog:\n{e}")

    def _open_history_dialog(self):
        try:
            from main_app.gui.history_dialog import HistoryDialog
            dialog = HistoryDialog(self.main_window)
            dialog.exec_()
        except Exception as e:
            self.logger.log_error(f"_open_history_dialog error: {e}")
            QMessageBox.warning(self.main_window, "Open Dialog Failed", f"Could not open History dialog:\n{e}")

    def _save_history_slot(self, person_name, frame, box):
        try:
            self.history_service.save_history(person_name, frame, box)
        except Exception as e:
            self.logger.log_error(f"_save_history_slot error: {e}")

    def _on_person_added(self, person_id, embeddings):
        try:
            if self.recognizer:
                self.recognizer.reload_database()
            if self.thread_manager:
                self.thread_manager.update_recognizer(self.recognizer)
            self.main_window.status_bar.showMessage(f"Person added: {person_id}", 3000)
        except Exception as e:
            self.logger.log_error(f"_on_person_added error: {e}")
            try:
                self.main_window.status_bar.showMessage(f"Error: {str(e)}", 3000)
            except Exception:
                pass

    def _on_person_deleted(self, person_id):
        try:
            if self.recognizer:
                self.recognizer.reload_database()
            if self.thread_manager:
                self.thread_manager.update_recognizer(self.recognizer)
            self.main_window.status_bar.showMessage(f"Person {person_id} deleted", 3000)
        except Exception as e:
            self.logger.log_error(f"_on_person_deleted error: {e}")
            try:
                self.main_window.status_bar.showMessage(f"Error: {str(e)}", 3000)
            except Exception:
                pass

    def _on_settings_applied(self):
        new_model_config = self.config_manager.get_config().get("models", {})
        if not self._check_if_needs_restart(new_model_config):
            self.logger.log_info("Confidence settings changed - instant apply")
            try:
                self.main_window.status_bar.showMessage("✅ Confidence settings updated instantly ⚡", 3000)
            except Exception:
                pass
            return
        was_running = self.main_window.is_running
        try:
            if was_running:
                self._stop_camera()
                self.logger.log_info("Camera stopped for model reload...")
            self.logger.log_info("Reloading models with new config...")
            self.model_manager = ModelManager(self.config, self.device)
            self.models = self.model_manager.get_models()
            self.recognizer = self.model_manager.get_recognizer()
            self.thread_manager = ThreadManager(self.config, self.models, self.device, self.recognizer)
            try:
                self.thread_manager.connect_signals(self.main_window, self._display_results)
            except Exception:
                pass
            self.logger.log_info("Models reloaded successfully")
            if was_running:
                self._start_camera()
                try:
                    self.main_window.status_bar.showMessage("✅ Models reloaded & camera restarted", 3000)
                except Exception:
                    pass
            else:
                try:
                    self.main_window.status_bar.showMessage("✅ Models reloaded successfully", 3000)
                except Exception:
                    pass
        except Exception as e:
            error_msg = f"Failed to reload models: {str(e)}"
            self.logger.log_error(error_msg)
            QMessageBox.warning(self.main_window, "Model Reload Failed", f"⚠️ {error_msg}\nPlease restart the application.")

    def _check_if_needs_restart(self, new_model_config):
        old_models = self.config.get("models", {})
        critical_changes = [
            self.config.get("runtime", {}).get("device") != new_model_config.get("runtime", {}).get("device")
        ]
        return any(critical_changes)

    def _on_camera_changed(self):
        if self.main_window.is_running:
            self._stop_camera()
            self._start_camera()

    def _on_model_changed(self):
        self._on_settings_applied()

    def _display_results(self, frame, boxes, person_ids):
        try:
            if person_ids:
                self.main_window.show_recognition(person_ids[0])
        except Exception as e:
            self.logger.log_error(f"_display_results error: {e}")

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())


def main():
    app = FaceRecognitionApp()
    app.run()


if __name__ == "__main__":
    main()
