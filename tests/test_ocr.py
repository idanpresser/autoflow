import numpy as np

from src.vision.ocr import capture_screen


def test_capture_screen() -> None:
    img = capture_screen()
    assert img is not None
    assert isinstance(img, np.ndarray)
    assert len(img.shape) == 3
    assert img.shape[2] in (3, 4)


def test_extract_text() -> None:
    from unittest.mock import patch

    mock_img = np.zeros((100, 100, 3), dtype=np.uint8)
    with patch("pytesseract.image_to_string", return_value="READY") as mock_ocr:
        from src.vision.ocr import extract_text

        text = extract_text(mock_img)
        assert text == "READY"
        mock_ocr.assert_called_once_with(mock_img)


def test_tesseract_fallback_path() -> None:
    import importlib
    import os
    from unittest.mock import patch

    import pytesseract

    import src.vision.ocr as ocr

    original_cmd = pytesseract.pytesseract.tesseract_cmd

    try:

        def side_effect(self_path: object) -> bool:
            normalized = os.path.normpath(str(self_path))
            return normalized.endswith(os.path.normpath("bin/tesseract/tesseract.exe"))

        with patch("pathlib.Path.exists", autospec=True, side_effect=side_effect):
            importlib.reload(ocr)
            assert os.path.normpath("bin/tesseract/tesseract.exe") in os.path.normpath(
                pytesseract.pytesseract.tesseract_cmd
            )
    finally:
        pytesseract.pytesseract.tesseract_cmd = original_cmd


def test_vision_provider_protocol() -> None:
    from src.vision.ocr import (
        MistralVisionProvider,
        TesseractVisionProvider,
        VisionProvider,
    )

    assert issubclass(TesseractVisionProvider, VisionProvider)
    assert issubclass(MistralVisionProvider, VisionProvider)

    t_provider = TesseractVisionProvider()
    assert hasattr(t_provider, "capture_screen")
    assert hasattr(t_provider, "extract_text")

    # For protocol checking with dummy API key
    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"MISTRAL_API_KEY": "dummy_key"}):
        m_provider = MistralVisionProvider()
        assert hasattr(m_provider, "capture_screen")
        assert hasattr(m_provider, "extract_text")


def test_get_vision_provider() -> None:
    import os
    from unittest.mock import patch

    from src.vision.ocr import (
        MistralVisionProvider,
        TesseractVisionProvider,
        get_vision_provider,
    )

    # Test 'mistral' selection
    with patch.dict(os.environ, {"OCR_PROVIDER": "mistral", "MISTRAL_API_KEY": "dummy_key"}):
        provider = get_vision_provider()
        assert isinstance(provider, MistralVisionProvider)

    # Test 'tesseract' selection
    with patch.dict(os.environ, {"OCR_PROVIDER": "tesseract"}):
        provider = get_vision_provider()
        assert isinstance(provider, TesseractVisionProvider)

    # Test default fallback when not set
    with patch.dict(os.environ, {}):
        if "OCR_PROVIDER" in os.environ:
            del os.environ["OCR_PROVIDER"]
        provider = get_vision_provider()
        assert isinstance(provider, TesseractVisionProvider)


def test_mistral_vision_provider_extract_text() -> None:
    import numpy as np
    from unittest.mock import MagicMock

    from src.vision.ocr import MistralVisionProvider

    mock_client = MagicMock()
    mock_uploaded_file = MagicMock()
    mock_uploaded_file.id = "file_123"
    mock_client.files.upload.return_value = mock_uploaded_file

    mock_page = MagicMock()
    mock_page.markdown = "Hello Mistral OCR"
    mock_ocr_response = MagicMock()
    mock_ocr_response.pages = [mock_page]
    mock_client.ocr.process.return_value = mock_ocr_response

    provider = MistralVisionProvider(client=mock_client)
    mock_img = np.zeros((100, 100, 3), dtype=np.uint8)

    extracted_text = provider.extract_text(mock_img)

    assert extracted_text == "Hello Mistral OCR"
    mock_client.files.upload.assert_called_once()
    mock_client.ocr.process.assert_called_once_with(
        model="mistral-ocr-latest",
        document={"type": "file_id", "file_id": "file_123"},
    )
    mock_client.files.delete.assert_called_once_with(file_id="file_123")


def test_mistral_vision_provider_missing_key() -> None:
    import os

    import pytest
    from unittest.mock import patch

    from src.vision.ocr import MistralVisionProvider

    with patch.dict(os.environ, {}):
        if "MISTRAL_API_KEY" in os.environ:
            del os.environ["MISTRAL_API_KEY"]
        with pytest.raises(ValueError, match="MISTRAL_API_KEY environment variable is not set"):
            MistralVisionProvider()


