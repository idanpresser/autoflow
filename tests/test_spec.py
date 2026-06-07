from pathlib import Path


def test_spec_file() -> None:
    spec_path = Path("autoflow.spec")
    assert spec_path.exists(), "autoflow.spec file does not exist"

    with spec_path.open(encoding="utf-8") as f:
        content = f.read()

    assert "console=False" in content, "spec file does not disable the console window"
    assert "main.py" in content, "spec file does not target main.py"
