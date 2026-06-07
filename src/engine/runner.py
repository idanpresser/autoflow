import time
from PySide6.QtCore import QThread, Signal
from src.vision.ocr import capture_screen, extract_text

class WorkflowRunner(QThread):
    step_finished = Signal(int)
    workflow_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, steps):
        super().__init__()
        self.steps = steps
        self._is_running = True

    def run(self):
        for index, step in enumerate(self.steps):
            if not self._is_running:
                break
            
            # Emitting finished signal for the step
            self.step_finished.emit(index)
            
        if self._is_running:
            self.workflow_completed.emit("Success")

    def wait_for_ocr(self, target, timeout):
        """
        Polls the screen for the target text, sleeping 500ms between checks,
        and raising TimeoutError if the timeout is reached.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self._is_running:
                break
            
            img = capture_screen()
            text = extract_text(img)
            if target in text:
                return
            
            time.sleep(0.5)
            
        raise TimeoutError(f"Timeout waiting for text '{target}'")

