import os
from pathlib import Path
from typing import Protocol, runtime_checkable

import cv2
import mss
import numpy as np
import pytesseract
from mistralai.client import Mistral


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


class MistralVisionProvider(VisionProvider):
    def __init__(self, client: Mistral | None = None) -> None:
        """
        Initializes the Mistral client. Uses MISTRAL_API_KEY from environment if not provided.
        """
        if client is not None:
            self.client = client
        else:
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError(
                    "MISTRAL_API_KEY environment variable is not set. "
                    "Please configure it in your .env file."
                )
            self.client = Mistral(api_key=api_key)

    def capture_screen(self) -> np.ndarray:
        """
        Captures a screenshot of the primary monitor using high-speed mss
        and returns it as a numpy array.
        """
        with mss.MSS() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            return np.array(sct_img)

    def extract_text(self, image_np: np.ndarray) -> str:
        """
        Extracts text from a numpy image array using Mistral OCR API.
        Uploads screenshot to Mistral, processes OCR, and deletes file immediately.
        """
        # Encode numpy array image to PNG bytes
        success, encoded_img = cv2.imencode(".png", image_np)
        if not success:
            raise ValueError("Failed to encode image to PNG format")
        image_bytes = encoded_img.tobytes()

        # Upload screenshot to Mistral with purpose="ocr"
        uploaded_file = self.client.files.upload(
            file={"file_name": "screenshot.png", "content": image_bytes},
            purpose="ocr",
        )

        try:
            # Request OCR processing from Mistral AI
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={"type": "file_id", "file_id": uploaded_file.id},
            )
            # Retrieve text from all pages
            text = "\n".join(page.markdown for page in ocr_response.pages)
            return text
        finally:
            # Ensure cleanup of the uploaded screenshot
            try:
                self.client.files.delete(file_id=uploaded_file.id)
            except Exception as e:
                print(f"Warning: Failed to delete uploaded OCR file {uploaded_file.id}: {e}")


def get_vision_provider() -> VisionProvider:
    """
    Factory function returning the configured VisionProvider based on the OCR_PROVIDER
    environment variable. Defaults to TesseractVisionProvider if not specified.
    """
    provider_type = os.getenv("OCR_PROVIDER", "tesseract").lower().strip()
    if provider_type == "mistral":
        return MistralVisionProvider()
    return TesseractVisionProvider()


def capture_screen() -> np.ndarray:
    """
    Convenience function wrapper for configured vision provider capture_screen.
    """
    return get_vision_provider().capture_screen()


def extract_text(image_np: np.ndarray) -> str:
    """
    Convenience function wrapper for configured vision provider extract_text.
    """
    return get_vision_provider().extract_text(image_np)


