import time
from typing import Any

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from src.vision.ocr import VisionProvider, TesseractVisionProvider


DEFAULT_OCR_POLL_INTERVAL = 0.5


class WorkflowRunner(QThread):
    step_finished = Signal(int)
    workflow_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, steps: list[dict[str, Any]], vision_provider: VisionProvider | None = None) -> None:
        super().__init__()
        import copy
        self.steps = copy.deepcopy(steps)
        self._mutex = QMutex()
        self._is_running = True
        self.vision_provider = vision_provider if vision_provider is not None else TesseractVisionProvider()

    def stop(self) -> None:
        locker = QMutexLocker(self._mutex)
        self._is_running = False

    def is_running(self) -> bool:
        locker = QMutexLocker(self._mutex)
        return self._is_running

    def run(self) -> None:
        try:
            for index, _step in enumerate(self.steps):
                if not self.is_running():
                    break

                # Emitting finished signal for the step
                self.step_finished.emit(index)

            if self.is_running():
                self.workflow_completed.emit("Success")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def wait_for_ocr(self, target: str, timeout: float) -> None:
        """
        Polls the screen for the target text, sleeping 500ms between checks,
        and raising TimeoutError if the timeout is reached.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_running():
                raise RuntimeError("Workflow runner stopped")

            img = self.vision_provider.capture_screen()
            text = self.vision_provider.extract_text(img)
            if target in text:
                return

            time.sleep(DEFAULT_OCR_POLL_INTERVAL)

        raise TimeoutError(f"Timeout waiting for text '{target}'")

