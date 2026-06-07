"""
WorkflowRunner — the core execution engine for AutoFlow.
Runs workflow steps on a background QThread, dispatching each step
to the appropriate action handler while emitting signals for UI updates.
"""

import logging
import time
from typing import Any

from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

from src.engine.actions import (
    copy_and_match,
    focus_window,
    run_command,
    send_keystroke,
    type_text,
    wait_delay,
)
from src.vision.image_match import wait_for_image
from src.vision.ocr import VisionProvider, get_vision_provider

logger = logging.getLogger(__name__)

DEFAULT_OCR_POLL_INTERVAL = 0.5


class WorkflowRunner(QThread):
    step_started = Signal(int)
    step_finished = Signal(int)
    workflow_completed = Signal(str)
    error_occurred = Signal(str)

    def __init__(
        self,
        steps: list[dict[str, Any]],
        vision_provider: VisionProvider | None = None,
    ) -> None:
        super().__init__()
        import copy

        self.steps = copy.deepcopy(steps)
        self._mutex = QMutex()
        self._is_running = True
        self.vision_provider = (
            vision_provider
            if vision_provider is not None
            else get_vision_provider()
        )

    def stop(self) -> None:
        with QMutexLocker(self._mutex):
            self._is_running = False

    def is_running(self) -> bool:
        with QMutexLocker(self._mutex):
            return self._is_running

    def run(self) -> None:
        try:
            for index, step in enumerate(self.steps):
                if not self.is_running():
                    logger.info("Workflow cancelled at step %d", index)
                    break

                self.step_started.emit(index)
                logger.info(
                    "Executing step %d/%d: %s",
                    index + 1,
                    len(self.steps),
                    step.get("type", "unknown"),
                )

                self._execute_step(step)

                self.step_finished.emit(index)

            if self.is_running():
                self.workflow_completed.emit("Success")
        except Exception as e:
            logger.exception("Workflow error at step: %s", e)
            self.error_occurred.emit(str(e))

    def _execute_step(self, step: dict[str, Any]) -> None:
        """
        Dispatches a single step to the appropriate action handler
        based on the step's 'type' field.
        """
        step_type = step.get("type", "")

        if step_type == "type_text":
            text = step.get("text", "")
            if not text:
                raise ValueError("type_text step missing 'text' field")
            type_text(text)

        elif step_type == "keystroke":
            keys = step.get("keys", [])
            if not keys:
                raise ValueError("keystroke step missing 'keys' field")
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split("+") if k.strip()]
            send_keystroke(keys)

        elif step_type == "focus_window":
            target = step.get("target", "")
            if not target:
                raise ValueError("focus_window step missing 'target' field")
            focus_window(target)

        elif step_type == "wait":
            seconds = step.get("seconds", step.get("duration", 1.0))
            wait_delay(float(seconds))

        elif step_type == "wait_for_text":
            target_text = step.get("text", "")
            timeout = step.get("timeout_sec", 30)
            if not target_text:
                raise ValueError("wait_for_text step missing 'text' field")
            self.wait_for_ocr(target_text, float(timeout))

        elif step_type == "wait_for_image":
            image_path = step.get("image_path", "")
            timeout = step.get("timeout_sec", 30)
            confidence = step.get("confidence", 0.8)
            if not image_path:
                raise ValueError("wait_for_image step missing 'image_path' field")
            wait_for_image(
                image_path,
                timeout=float(timeout),
                confidence=float(confidence),
                is_running_check=self.is_running,
            )

        elif step_type == "copy_parse":
            pattern = step.get("pattern", "")
            if not pattern:
                raise ValueError("copy_parse step missing 'pattern' field")
            result = copy_and_match(pattern)
            logger.info("copy_parse result: %s", result)

        elif step_type == "run_command":
            command = step.get("command", "")
            timeout = step.get("timeout_sec", 60)
            if not command:
                raise ValueError("run_command step missing 'command' field")
            output = run_command(command, timeout=float(timeout))
            logger.info("run_command output: %s", output[:200] if output else "(empty)")

        else:
            raise ValueError(f"Unknown step type: '{step_type}'")

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
