# AutoFlow: Phase Alignment & Guardrails

To prevent scope drift, over-engineering, and "AI slop" (unstructured code, redundant functions, or generic designs), this document defines key technical constraints and architectural decisions for each phase. 

Every task implemented must align with the answers documented here.

---

## Phase 1: Core Foundation & UI Builder

### Q1.1: What is the styling approach and layout constraints for the UI?
- **Answer**: Use PySide6 layouts (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`) with explicit styling. No browser-default or generic raw grey boxes. Apply a dark mode theme with Outfit or Inter typography and HSL-based highlights (e.g., sleek blues/teal). The step list must support adding, deleting, and reordering steps smoothly.

### Q1.2: What is the JSON serialization format for profiles?
- **Answer**: Profiles must be stored under `profiles/{profile_name}.json` as an object:
  ```json
  {
    "profile_name": "Restart React Server",
    "hotkey": "ctrl+shift+r",
    "steps": [
      { "type": "focus_window", "target": "Windows Terminal" },
      { "type": "keystroke", "keys": ["ctrl", "c"] },
      { "type": "type_text", "text": "npm run start" },
      { "type": "keystroke", "keys": ["enter"] },
      { "type": "wait_for_text", "text": "Compiled successfully", "timeout_sec": 30 }
    ]
  }
  ```
  Ensure all files serialize/deserialize this schema exactly.

### Q1.3: How should invalid configuration files be handled?
- **Answer**: Do not fail silently or let PySide6 crash. Implement a validator inside `src/utils/config.py` that raises a custom `ValidationError` with descriptive details if JSON fields are missing or malformed. Show a `QMessageBox.warning` in the UI to notify the user.

---

## Phase 2: The Execution Engine (Taskt-inspired)

### Q2.1: How do we prevent UI freezing during long-running automations?
- **Answer**: Run all automation steps inside a dedicated `QThread` subclass (`WorkflowRunner` in `src/engine/runner.py`). The thread consumes tasks from a thread-safe `queue.Queue`. The GUI thread must never run block-based loops or wait loops.

### Q2.2: How does the runner communicate status to the UI?
- **Answer**: Use PySide6 Signals:
  - `step_finished(int)`: Emits the index of the completed step to highlight progress in the GUI list.
  - `workflow_completed(str)`: Emits when execution finishes successfully.
  - `error_occurred(str)`: Emits when a step fails, terminating execution and highlighting the failed step in red.

### Q2.3: What safety mechanisms are required for OS input simulation?
- **Answer**: 
  - Always set `pyautogui.FAILSAFE = True` so users can abort execution by moving the mouse to any corner of the screen.
  - Set default typing intervals (e.g., `pyautogui.write(..., interval=0.05)`) to prevent text buffer overflows in target terminals.

---

## Phase 3: "Smart" Triggers (SikuliX-inspired)

### Q3.1: Why use `mss` instead of `PyAutoGUI` for screen grabbing?
- **Answer**: `mss` is a specialized, multi-platform screen capture library that takes screenshots significantly faster (often sub-10ms) than PyAutoGUI's screenshot engine, reducing CPU overhead during OCR loops.

### Q3.2: How do we handle OCR polling loops safely?
- **Answer**: In the worker thread, the polling loop for `wait_for_text` must check `self._is_running` on each iteration to allow instant aborting. Use a strict 500ms sleep between captures (`time.sleep(0.5)`) to limit CPU spikes, and terminate with `TimeoutError` if `timeout_sec` is reached.

### Q3.3: How do we handle Tesseract OCR path configuration?
- **Answer**: Implement a fallback search inside `src/vision/ocr.py` that first checks for a bundled executable path (e.g., `bin/tesseract/tesseract.exe`), then falls back to standard Windows paths (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`). If still not found, raise a clean `FileNotFoundError` with clear setup instructions.

---

## Phase 4: Global Hotkeys & OS Integration

### Q4.1: How do we listen for global hotkeys without blocking the application?
- **Answer**: Use the `keyboard` module which runs its listener hook on a background thread. When the hotkey matches, trigger a signal/event to safe-start the worker `QThread` on the Qt event loop.

### Q4.2: How should system tray integration work?
- **Answer**: Use `QSystemTrayIcon` with a custom context menu (Restore, Run Profile, Exit). The main window close event must be overridden to minimize the application to the tray rather than terminating it, unless explicitly closed via the tray menu.

---

## Phase 5: Packaging and Distribution

### Q5.1: What should the final deployment bundle contain?
- **Answer**: A single self-contained directory containing the executable, PySide6 DLLs, the embedded Python environment, and the Tesseract-OCR binary directory, packaged via a PyInstaller/Nuitka spec file.

### Q5.2: How do we verify the standalone build is correct?
- **Answer**: Run the compiled executable on a clean virtual machine or container lacking a global Python interpreter and Tesseract installation, verifying that GUI loading, profile saving, execution, and OCR work correctly out-of-the-box.
