import mss
import numpy as np
import pytesseract

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
    """
    return pytesseract.image_to_string(image_np)

