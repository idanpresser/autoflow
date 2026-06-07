import pytest

from src.engine.runner import WorkflowRunner


def test_workflow_runner_initialization() -> None:
    steps = [{"type": "type_text", "text": "hello"}]
    runner = WorkflowRunner(steps)

    # Check steps are correctly set
    assert runner.steps == steps

    # Check for presence of required signals
    assert hasattr(runner, "step_finished")
    assert hasattr(runner, "workflow_completed")
    assert hasattr(runner, "error_occurred")


def test_workflow_runner_execution() -> None:
    steps = [
        {"type": "dummy", "text": "step 0"},
        {"type": "dummy", "text": "step 1"},
        {"type": "dummy", "text": "step 2"},
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


def test_workflow_runner_wait_for_text_success() -> None:
    from unittest.mock import MagicMock, patch
    mock_provider = MagicMock()
    mock_provider.extract_text.side_effect = ["", "Waiting", "Success"]
    runner = WorkflowRunner([], vision_provider=mock_provider)

    with patch("time.sleep") as mock_sleep:
        runner.wait_for_ocr("Success", timeout=5)
        assert mock_provider.extract_text.call_count == 3
        assert mock_sleep.call_count == 2


def test_workflow_runner_wait_for_text_timeout() -> None:
    from unittest.mock import MagicMock, patch
    mock_provider = MagicMock()
    mock_provider.extract_text.return_value = "Failed"
    runner = WorkflowRunner([], vision_provider=mock_provider)

    with patch("time.sleep"):
        with pytest.raises(TimeoutError) as exc_info:
            runner.wait_for_ocr("Success", timeout=1)
        assert "Timeout waiting for text" in str(exc_info.value)


def test_workflow_runner_stop() -> None:
    steps = [
        {"type": "dummy", "text": "step 0"},
        {"type": "dummy", "text": "step 1"},
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
    from unittest.mock import patch
    with patch("time.sleep") as mock_sleep:
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
    steps = [{"type": "type_text", "text": "hello"}]
    runner = WorkflowRunner(steps)

    # Mutate the original steps list and dictionary
    steps[0]["text"] = "mutated"
    steps.append({"type": "keystroke", "keys": ["enter"]})

    # Assert that the runner's steps list remains unchanged
    assert runner.steps != steps
    assert runner.steps == [{"type": "type_text", "text": "hello"}]



