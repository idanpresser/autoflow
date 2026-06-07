import os
import mss
import numpy as np
import pytesseract

# Configure Tesseract fallback paths
_local_path = os.path.join("bin", "tesseract", "tesseract.exe")
_standard_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(_local_path):
    pytesseract.pytesseract.tesseract_cmd = os.path.abspath(_local_path)
elif os.path.exists(_standard_path):
    pytesseract.pytesseract.tesseract_cmd = _standard_path

def capture_screen():
    """
    Captures a screenshot of the primary monitor using high-speed mss
    and returns it as a numpy array.
    """
    with mss.MSS() as sct:
        # sct.monitors[1] is the primary monitor
        # sct.monitors[0] represents the unified screen space of all monitors
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        return np.array(sct_img)

def extract_text(image_np):
    """
    Extracts text from a numpy image array using pytesseract.
    Raises FileNotFoundError with clear instructions if Tesseract is not installed.
    """
    try:
        return pytesseract.image_to_string(image_np)
    except pytesseract.pytesseract.TesseractNotFoundError as e:
        raise FileNotFoundError(
            "Tesseract OCR executable not found. Please install Tesseract OCR "
            "and add it to your PATH, or bundle it under 'bin/tesseract/tesseract.exe'."
        ) from e


