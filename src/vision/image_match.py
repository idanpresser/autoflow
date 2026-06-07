"""
Image matching module for AutoFlow.
Provides template matching capabilities inspired by SikuliX,
using OpenCV's matchTemplate for fast, accurate image detection.
"""

import logging
import time
from collections.abc import Callable
from pathlib import Path

import cv2
import mss
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE = 0.8
DEFAULT_POLL_INTERVAL = 0.5


def capture_screen_bgr() -> np.ndarray:
    """
    Captures a screenshot of the primary monitor and returns it as a BGR numpy array
    (the format OpenCV expects for template matching).
    """
    with mss.MSS() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        # mss returns BGRA, convert to BGR for OpenCV
        img = np.array(sct_img)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def find_on_screen(
    template_path: str | Path,
    confidence: float = DEFAULT_CONFIDENCE,
    screen_image: np.ndarray | None = None,
) -> tuple[int, int] | None:
    """
    Searches the screen for the given template image.

    Args:
        template_path: Path to the template PNG image to search for.
        confidence: Minimum match confidence threshold (0.0 to 1.0).
        screen_image: Optional pre-captured screen image (BGR). If None, captures a new screenshot.

    Returns:
        (x, y) center coordinates of the best match if confidence >= threshold, else None.

    Raises:
        FileNotFoundError: If the template image file does not exist.
        ValueError: If the template image cannot be loaded.
    """
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template image not found: {template_path}")

    template = cv2.imread(str(template_path), cv2.IMREAD_COLOR)
    if template is None:
        raise ValueError(f"Failed to load template image: {template_path}")

    if screen_image is None:
        screen_image = capture_screen_bgr()

    # Ensure template is not larger than the screen
    if (
        template.shape[0] > screen_image.shape[0]
        or template.shape[1] > screen_image.shape[1]
    ):
        logger.warning(
            "Template (%dx%d) is larger than screen (%dx%d)",
            template.shape[1],
            template.shape[0],
            screen_image.shape[1],
            screen_image.shape[0],
        )
        return None

    # Perform template matching using normalized cross-correlation
    result = cv2.matchTemplate(screen_image, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    logger.debug(
        "Template match confidence: %.3f (threshold: %.3f)", max_val, confidence
    )

    if max_val >= confidence:
        # max_loc is (x, y) of the top-left corner of the match
        # Return the center of the matched region
        h, w = template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return (center_x, center_y)

    return None


def wait_for_image(
    template_path: str | Path,
    timeout: float = 30.0,
    interval: float = DEFAULT_POLL_INTERVAL,
    confidence: float = DEFAULT_CONFIDENCE,
    is_running_check: Callable[[], bool] | None = None,
) -> tuple[int, int]:
    """
    Polls the screen for the template image until found or timeout is reached.

    Args:
        template_path: Path to the template PNG image to search for.
        timeout: Maximum seconds to wait before raising TimeoutError.
        interval: Seconds between each screen check.
        confidence: Minimum match confidence threshold.
        is_running_check: Optional callable that returns False if the workflow was cancelled.

    Returns:
        (x, y) center coordinates of the found image.

    Raises:
        TimeoutError: If the image is not found within the timeout period.
        RuntimeError: If is_running_check returns False (workflow cancelled).
    """
    logger.info(
        "Waiting for image '%s' (timeout: %.1fs, confidence: %.2f)",
        template_path,
        timeout,
        confidence,
    )

    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_running_check is not None and not is_running_check():
            raise RuntimeError("Workflow runner stopped")

        location = find_on_screen(template_path, confidence=confidence)
        if location is not None:
            logger.info("Image found at (%d, %d)", location[0], location[1])
            return location

        time.sleep(interval)

    raise TimeoutError(
        f"Image '{template_path}' not found on screen within {timeout}s"
    )
