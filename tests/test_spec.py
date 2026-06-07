import os

def test_spec_file():
    spec_path = "autoflow.spec"
    assert os.path.exists(spec_path), "autoflow.spec file does not exist"
    
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "console=False" in content, "spec file does not disable the console window"
    assert "main.py" in content, "spec file does not target main.py"
