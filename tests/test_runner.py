"""
Tests for WorkflowRunner — the core execution engine.
Tests verify step dispatch, signal emission, OCR polling, cancellation,
thread safety, deep copy, and global exception handling.
"""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.engine.runner import WorkflowRunner


def test_workflow_runner_initialization() -> None:
    steps = [{"type": "type_text", "text": "hello"}]
    runner = WorkflowRunner(steps)

    # Check steps are correctly set
    assert runner.steps == steps

    # Check for presence of required signals
    assert hasattr(runner, "step_started")
    assert hasattr(runner, "step_finished")
    assert hasattr(runner, "workflow_completed")
    assert hasattr(runner, "error_occurred")


@patch("src.engine.runner.type_text")
def test_workflow_runner_execution(mock_type_text: MagicMock) -> None:
    """Verify that run() dispatches steps and emits signals in order."""
    steps = [
        {"type": "type_text", "text": "step 0"},
        {"type": "type_text", "text": "step 1"},
        {"type": "type_text", "text": "step 2"},
    ]
    runner = WorkflowRunner(steps)

    finished_indices: list[int] = []
    completed_msg: list[str] = []

    runner.step_finished.connect(finished_indices.append)
    runner.workflow_completed.connect(completed_msg.append)

    # Call run directly to execute synchronously in tests
    runner.run()

    assert finished_indices == [0, 1, 2]
    assert len(completed_msg) == 1
    assert completed_msg[0] == "Success"
    assert mock_type_text.call_count == 3


def test_workflow_runner_wait_for_text_success() -> None:
    from unittest.mock import MagicMock, patch

    mock_provider = MagicMock()
    mock_provider.extract_text.side_effect = ["", "Waiting", "Success"]
    runner = WorkflowRunner([], vision_provider=mock_provider)

    with patch("src.engine.runner.time.sleep") as mock_sleep:
        runner.wait_for_ocr("Success", timeout=5)
        assert mock_provider.extract_text.call_count == 3
        assert mock_sleep.call_count == 2


def test_workflow_runner_wait_for_text_timeout() -> None:
    from unittest.mock import MagicMock, patch

    mock_provider = MagicMock()
    mock_provider.extract_text.return_value = "Failed"
    runner = WorkflowRunner([], vision_provider=mock_provider)

    with patch("src.engine.runner.time.sleep"):
        with pytest.raises(TimeoutError) as exc_info:
            runner.wait_for_ocr("Success", timeout=1)
        assert "Timeout waiting for text" in str(exc_info.value)


def test_workflow_runner_stop() -> None:
    """Verify that a stopped runner emits no signals."""
    steps = [
        {"type": "type_text", "text": "step 0"},
        {"type": "type_text", "text": "step 1"},
    ]
    runner = WorkflowRunner(steps)
    runner._is_running = False

    finished_indices: list[int] = []
    completed_msg: list[str] = []

    runner.step_finished.connect(finished_indices.append)
    runner.workflow_completed.connect(completed_msg.append)

    runner.run()

    assert finished_indices == []
    assert completed_msg == []


def test_workflow_runner_wait_for_ocr_stop() -> None:
    from unittest.mock import MagicMock

    mock_provider = MagicMock()
    runner = WorkflowRunner([], vision_provider=mock_provider)
    runner._is_running = False

    with pytest.raises(RuntimeError) as exc_info:
        runner.wait_for_ocr("Success", timeout=10)
    assert "Workflow runner stopped" in str(exc_info.value)
    mock_provider.capture_screen.assert_not_called()


def test_workflow_runner_vision_injection() -> None:
    import numpy as np

    from src.vision.ocr import VisionProvider

    class MockVisionProvider(VisionProvider):
        def __init__(self) -> None:
            self.capture_count = 0
            self.extract_count = 0

        def capture_screen(self) -> np.ndarray:
            self.capture_count += 1
            return np.zeros((10, 10, 3), dtype=np.uint8)

        def extract_text(self, image_np: np.ndarray) -> str:
            self.extract_count += 1
            if self.extract_count == 3:
                return "Success"
            return ""

    # Test default provider initialization
    runner_default = WorkflowRunner([])
    assert runner_default.vision_provider.__class__.__name__ == "TesseractVisionProvider"

    # Test injected provider initialization
    mock_provider = MockVisionProvider()
    runner = WorkflowRunner([], vision_provider=mock_provider)
    assert runner.vision_provider is mock_provider

    # Test that wait_for_ocr calls injected provider
    with patch("src.engine.runner.time.sleep") as mock_sleep:
        runner.wait_for_ocr("Success", timeout=5)
        assert mock_provider.capture_count == 3
        assert mock_provider.extract_count == 3
        assert mock_sleep.call_count == 2


def test_workflow_runner_thread_safe_stop() -> None:
    runner = WorkflowRunner([])
    assert runner.is_running() is True

    runner.stop()
    assert runner.is_running() is False

    # Check that run() breaks immediately if stopped
    finished_indices: list[int] = []
    runner.step_finished.connect(finished_indices.append)
    runner.run()
    assert finished_indices == []


def test_workflow_runner_steps_deep_copy() -> None:
    steps: list[dict[str, Any]] = [{"type": "type_text", "text": "hello"}]
    runner = WorkflowRunner(steps)

    # Mutate the original steps list and dictionary
    steps[0]["text"] = "mutated"
    steps.append({"type": "keystroke", "keys": ["enter"]})

    # Assert that the runner's steps list remains unchanged
    assert runner.steps != steps
    assert runner.steps == [{"type": "type_text", "text": "hello"}]


def test_workflow_runner_global_exception_handling() -> None:
    class FailingSteps:
        def __init__(self) -> None:
            pass

        def __iter__(self) -> Any:
            raise RuntimeError("Iteration failed")

    # Pass the failing steps but bypass the deepcopy inside __init__ using mock
    with patch("copy.deepcopy", return_value=FailingSteps()):
        runner = WorkflowRunner([])

    errors: list[str] = []
    completed: list[str] = []

    runner.error_occurred.connect(errors.append)
    runner.workflow_completed.connect(completed.append)

    runner.run()

    assert len(errors) == 1
    assert "Iteration failed" in errors[0]
    assert len(completed) == 0


@patch("src.engine.runner.type_text")
@patch("src.engine.runner.send_keystroke")
@patch("src.engine.runner.focus_window")
def test_workflow_runner_dispatches_all_basic_types(
    mock_focus: MagicMock,
    mock_keystroke: MagicMock,
    mock_type: MagicMock,
) -> None:
    """Verify that the runner dispatches type_text, keystroke, and focus_window correctly."""
    steps = [
        {"type": "type_text", "text": "hello"},
        {"type": "keystroke", "keys": ["ctrl", "c"]},
        {"type": "focus_window", "target": "My App"},
    ]
    runner = WorkflowRunner(steps)

    finished: list[int] = []
    runner.step_finished.connect(finished.append)
    runner.run()

    assert finished == [0, 1, 2]
    mock_type.assert_called_once_with("hello")
    mock_keystroke.assert_called_once_with(["ctrl", "c"])
    mock_focus.assert_called_once_with("My App")


@patch("src.engine.runner.wait_delay")
def test_workflow_runner_dispatches_wait(mock_wait: MagicMock) -> None:
    steps = [{"type": "wait", "seconds": 2.5}]
    runner = WorkflowRunner(steps)
    runner.run()
    mock_wait.assert_called_once_with(2.5)


@patch("src.engine.runner.run_command")
def test_workflow_runner_dispatches_run_command(mock_cmd: MagicMock) -> None:
    mock_cmd.return_value = "output"
    steps = [{"type": "run_command", "command": "echo hello", "timeout_sec": 10}]
    runner = WorkflowRunner(steps)
    runner.run()
    mock_cmd.assert_called_once_with("echo hello", timeout=10.0)


@patch("src.engine.runner.copy_and_match")
def test_workflow_runner_dispatches_copy_parse(mock_copy: MagicMock) -> None:
    mock_copy.return_value = "matched"
    steps = [{"type": "copy_parse", "pattern": r"\d+"}]
    runner = WorkflowRunner(steps)
    runner.run()
    mock_copy.assert_called_once_with(r"\d+")


def test_workflow_runner_unknown_step_type() -> None:
    """Verify that unknown step types emit error_occurred."""
    steps = [{"type": "nonexistent_action"}]
    runner = WorkflowRunner(steps)

    errors: list[str] = []
    runner.error_occurred.connect(errors.append)
    runner.run()

    assert len(errors) == 1
    assert "Unknown step type" in errors[0]


def test_workflow_runner_missing_required_field() -> None:
    """Verify that missing required fields in steps emit error_occurred."""
    steps = [{"type": "type_text"}]  # Missing 'text' field
    runner = WorkflowRunner(steps)

    errors: list[str] = []
    runner.error_occurred.connect(errors.append)
    runner.run()

    assert len(errors) == 1
    assert "text" in errors[0].lower()
