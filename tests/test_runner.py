import pytest
from src.engine.runner import WorkflowRunner

def test_workflow_runner_initialization():
    steps = [{"type": "type_text", "text": "hello"}]
    runner = WorkflowRunner(steps)
    
    # Check steps are correctly set
    assert runner.steps == steps
    
    # Check for presence of required signals
    assert hasattr(runner, "step_finished")
    assert hasattr(runner, "workflow_completed")
    assert hasattr(runner, "error_occurred")

def test_workflow_runner_execution():
    steps = [
        {"type": "dummy", "text": "step 0"},
        {"type": "dummy", "text": "step 1"},
        {"type": "dummy", "text": "step 2"},
    ]
    runner = WorkflowRunner(steps)
    
    finished_indices = []
    completed_msg = []
    
    runner.step_finished.connect(finished_indices.append)
    runner.workflow_completed.connect(completed_msg.append)
    
    # Call run directly to execute synchronously in tests
    runner.run()
    
    assert finished_indices == [0, 1, 2]
    assert len(completed_msg) == 1
    assert completed_msg[0] == "Success"

def test_workflow_runner_wait_for_text_success():
    runner = WorkflowRunner([])
    from unittest.mock import patch
    with patch("src.engine.runner.capture_screen") as mock_capture:
        with patch("src.engine.runner.extract_text", side_effect=["", "Waiting", "Success"]) as mock_extract:
            with patch("time.sleep") as mock_sleep:
                runner.wait_for_ocr("Success", timeout=5)
                assert mock_extract.call_count == 3
                assert mock_sleep.call_count == 2

def test_workflow_runner_wait_for_text_timeout():
    runner = WorkflowRunner([])
    from unittest.mock import patch
    with patch("src.engine.runner.capture_screen") as mock_capture:
        with patch("src.engine.runner.extract_text", return_value="Failed"):
            with patch("time.sleep") as mock_sleep:
                with pytest.raises(TimeoutError) as exc_info:
                    runner.wait_for_ocr("Success", timeout=1)
                assert "Timeout waiting for text" in str(exc_info.value)



