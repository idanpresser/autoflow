"""
Tests for image_match.py — OpenCV template matching module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.vision.image_match import (
    DEFAULT_CONFIDENCE,
    find_on_screen,
    wait_for_image,
)


def test_find_on_screen_template_not_found() -> None:
    """Verify FileNotFoundError when template image doesn't exist."""
    with pytest.raises(FileNotFoundError, match="Template image not found"):
        find_on_screen("nonexistent_template.png")


@patch("src.vision.image_match.cv2.imread")
def test_find_on_screen_invalid_image(mock_imread: MagicMock, tmp_path: Path) -> None:
    """Verify ValueError when template image can't be loaded."""
    template = tmp_path / "bad_template.png"
    template.touch()
    mock_imread.return_value = None

    with pytest.raises(ValueError, match="Failed to load template image"):
        find_on_screen(str(template))


@patch("src.vision.image_match.capture_screen_bgr")
@patch("src.vision.image_match.cv2.imread")
@patch("src.vision.image_match.cv2.matchTemplate")
@patch("src.vision.image_match.cv2.minMaxLoc")
def test_find_on_screen_match_found(
    mock_minmax: MagicMock,
    mock_match: MagicMock,
    mock_imread: MagicMock,
    mock_capture: MagicMock,
    tmp_path: Path,
) -> None:
    """Verify successful match returns center coordinates."""
    template = tmp_path / "template.png"
    template.touch()

    # Template is 20x10
    mock_imread.return_value = np.zeros((10, 20, 3), dtype=np.uint8)
    # Screen is 1920x1080
    mock_capture.return_value = np.zeros((1080, 1920, 3), dtype=np.uint8)
    mock_match.return_value = np.zeros((1070, 1900), dtype=np.float32)
    # Match found at (100, 200) with confidence 0.95
    mock_minmax.return_value = (0.0, 0.95, (0, 0), (100, 200))

    result = find_on_screen(str(template), confidence=0.8)

    assert result is not None
    # Center = (100 + 20//2, 200 + 10//2) = (110, 205)
    assert result == (110, 205)


@patch("src.vision.image_match.capture_screen_bgr")
@patch("src.vision.image_match.cv2.imread")
@patch("src.vision.image_match.cv2.matchTemplate")
@patch("src.vision.image_match.cv2.minMaxLoc")
def test_find_on_screen_no_match(
    mock_minmax: MagicMock,
    mock_match: MagicMock,
    mock_imread: MagicMock,
    mock_capture: MagicMock,
    tmp_path: Path,
) -> None:
    """Verify None returned when confidence is below threshold."""
    template = tmp_path / "template.png"
    template.touch()

    mock_imread.return_value = np.zeros((10, 20, 3), dtype=np.uint8)
    mock_capture.return_value = np.zeros((1080, 1920, 3), dtype=np.uint8)
    mock_match.return_value = np.zeros((1070, 1900), dtype=np.float32)
    # Low confidence match
    mock_minmax.return_value = (0.0, 0.3, (0, 0), (100, 200))

    result = find_on_screen(str(template), confidence=0.8)
    assert result is None


@patch("src.vision.image_match.find_on_screen")
@patch("src.vision.image_match.time.sleep")
def test_wait_for_image_success(
    mock_sleep: MagicMock,
    mock_find: MagicMock,
) -> None:
    """Verify wait_for_image returns when image is found."""
    mock_find.side_effect = [None, None, (500, 300)]

    result = wait_for_image("template.png", timeout=10, interval=0.5)

    assert result == (500, 300)
    assert mock_find.call_count == 3
    assert mock_sleep.call_count == 2


@patch("src.vision.image_match.find_on_screen")
@patch("src.vision.image_match.time.sleep")
def test_wait_for_image_timeout(
    mock_sleep: MagicMock,
    mock_find: MagicMock,
) -> None:
    """Verify TimeoutError when image is never found."""
    mock_find.return_value = None

    with pytest.raises(TimeoutError, match="not found on screen"):
        wait_for_image("template.png", timeout=1, interval=0.5)


@patch("src.vision.image_match.find_on_screen")
def test_wait_for_image_cancelled(mock_find: MagicMock) -> None:
    """Verify RuntimeError when workflow is cancelled during wait."""
    mock_find.return_value = None

    with pytest.raises(RuntimeError, match="Workflow runner stopped"):
        wait_for_image(
            "template.png",
            timeout=10,
            is_running_check=lambda: False,
        )


def test_default_confidence_value() -> None:
    assert DEFAULT_CONFIDENCE == 0.8
