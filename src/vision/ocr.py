from pathlib import Path

import mss
import numpy as np
import pytesseract

# Configure Tesseract fallback paths
_local_path = Path("bin") / "tesseract" / "tesseract.exe"
_standard_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

if _local_path.exists():
    pytesseract.pytesseract.tesseract_cmd = str(_local_path.resolve())
elif _standard_path.exists():
    pytesseract.pytesseract.tesseract_cmd = str(_standard_path)


def capture_screen() -> np.ndarray:
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


def extract_text(image_np: np.ndarray) -> str:
    """
    Extracts text from a numpy image array using pytesseract.
    Raises FileNotFoundError with clear instructions if Tesseract is not installed.
    """
    try:
        return str(pytesseract.image_to_string(image_np))
    except pytesseract.pytesseract.TesseractNotFoundError as e:
        raise FileNotFoundError(
            "Tesseract OCR executable not found. Please install Tesseract OCR "
            "and add it to your PATH, or bundle it under 'bin/tesseract/tesseract.exe'."
        ) from e
