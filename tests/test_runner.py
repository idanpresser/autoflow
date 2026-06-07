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
