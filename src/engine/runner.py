from PySide6.QtCore import QThread, Signal

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
