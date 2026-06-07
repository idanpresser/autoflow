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

