import numpy as np
from src.vision.ocr import capture_screen

def test_capture_screen():
    img = capture_screen()
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] in (3, 4)
