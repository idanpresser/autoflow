from pathlib import Path
from typing import Protocol, runtime_checkable

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


@runtime_checkable
class VisionProvider(Protocol):
    def capture_screen(self) -> np.ndarray:
        """
        Captures a screenshot of the primary monitor and returns it as a numpy array.
        """
        ...

    def extract_text(self, image_np: np.ndarray) -> str:
        """
        Extracts text from a numpy image array.
        """
        ...


class TesseractVisionProvider(VisionProvider):
    def capture_screen(self) -> np.ndarray:
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

    def extract_text(self, image_np: np.ndarray) -> str:
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


# Default instance for convenience and backward compatibility
_default_provider = TesseractVisionProvider()


def capture_screen() -> np.ndarray:
    """
    Convenience function wrapper for default vision provider capture_screen.
    """
    return _default_provider.capture_screen()


def extract_text(image_np: np.ndarray) -> str:
    """
    Convenience function wrapper for default vision provider extract_text.
    """
    return _default_provider.extract_text(image_np)

