from PySide6.QtCore import QThread, Signal

class WorkflowRunner(QThread):
    step_finished = Signal(int)
    workflow_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, steps):
        super().__init__()
        self.steps = steps
        self._is_running = True
