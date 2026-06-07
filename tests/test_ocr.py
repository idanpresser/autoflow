import numpy as np
from src.vision.ocr import capture_screen

def test_capture_screen():
    img = capture_screen()
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] in (3, 4)

def test_extract_text():
    from unittest.mock import patch
    mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
    with patch("pytesseract.image_to_string", return_value="READY") as mock_ocr:
        from src.vision.ocr import extract_text
        text = extract_text(mock_img)
        assert text == "READY"
        mock_ocr.assert_called_once_with(mock_img)

def test_tesseract_fallback_path():
    import os
    import importlib
    import src.vision.ocr as ocr
    import pytesseract
    from unittest.mock import patch
    
    original_cmd = pytesseract.pytesseract.tesseract_cmd
    
    try:
        def side_effect(path):
            normalized = os.path.normpath(path)
            return normalized.endswith(os.path.normpath("bin/tesseract/tesseract.exe"))
            
        with patch("os.path.exists", side_effect=side_effect):
            importlib.reload(ocr)
            assert os.path.normpath("bin/tesseract/tesseract.exe") in os.path.normpath(pytesseract.pytesseract.tesseract_cmd)
    finally:
        pytesseract.pytesseract.tesseract_cmd = original_cmd


