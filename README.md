# AutoFlow

AutoFlow is an intelligent desktop automation application built with **Python and PySide6**. It bridges the gap between simple, coordinate-based macro recorders and heavy, bloated enterprise RPA tools. By combining a visual workflow builder with "smart" state-aware triggers (such as OCR, image detection, and clipboard parsing), AutoFlow enables developers and power users to automate repetitive tasks reliably.

---

## Key Features

- **Visual Workflow Builder:** Drag-and-drop or list-based UI to construct automation steps (type text, press keys, focus windows, wait for conditions).
- **Smart Triggers:** React dynamically to screen state using OCR (via Tesseract) or image template matching (via OpenCV).
- **Global Hotkeys:** Trigger profiles instantly from anywhere in the OS (using the `keyboard` module).
- **System Tray Integration:** Runs quietly in the Windows system tray with minimal RAM usage.
- **Asynchronous Execution:** Prevents UI freezing by running automation queues in a dedicated background worker thread (`QThread`).

---

## Technical Stack

- **Language:** Python 3.12+ (embedded in the project under `.embedded_python/`)
- **GUI Framework:** `PySide6` (Qt for Python)
- **Computer Vision / OCR:** `pytesseract` + `opencv-python` + `mss` (for rapid screen capturing)
- **Input Simulation:** `PyAutoGUI` + `pyperclip` (clipboard state)
- **Global Hotkeys:** `keyboard`

---

## Getting Started

### Prerequisites

AutoFlow runs using a local embedded Python distribution to ensure a self-contained runtime.

### Setup & Installation

1. The project includes a pre-configured embedded Python interpreter in `.embedded_python/` and a virtual environment in `.venv/`.
2. To activate the virtual environment and work with the codebase:
   - On Windows PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - On Windows CMD:
     ```cmd
     .venv\Scripts\activate.bat
     ```

3. To install project dependencies:
   ```powershell
   # Use the local uv installer within the virtual environment
   uv pip install -r requirements.txt
   ```

---

## Project Structure

```text
AutoFlow/
│
├── main.py                  # Entry point, initializes PySide6 app
├── profiles/                # Saved workflow .json configurations
├── src/
│   ├── ui/                  # PySide6 Views (Main window, Tray icon)
│   ├── engine/              # Automation runners and action wrappers
│   ├── vision/              # OCR (Tesseract) and Image template matching
│   └── utils/               # Config serializer, hotkey listener
```
