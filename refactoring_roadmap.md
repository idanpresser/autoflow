# Autoflow Refactoring Roadmap

This document outlines the detailed development phases and tasks required to address codebase architecture issues, magic literals, and thread safety concerns in AutoFlow.

---

# Phase 1: Decoupling and Dependency Injection

- Task 1: Define a `VisionProvider` Protocol in `ocr.py` and refactor screen capture and text extraction to implement it. Prerequisite: None. TDD: Test in `test_ocr.py` using a mock vision provider that avoids grabbing the actual screen or launching tesseract.
- Task 2: Refactor `runner.py` to inject `VisionProvider` into the `WorkflowRunner` constructor. Prerequisite: Phase 1 Task 1. TDD: Update `test_runner.py` to instantiate `WorkflowRunner` with a mock provider and verify OCR polling operates cleanly without patching imports.
- Task 3: Refactor `main_window.py` to accept hotkey registration and runner instantiation as injected dependencies. Prerequisite: Phase 1 Task 2. TDD: Update `test_main_window.py` to pass mock callbacks to check the registration flow.

# Phase 2: Magic Strings and Numbers Extraction

- Task 1: Create a `StepType` Enum in `config.py` and replace all hardcoded step strings in `runner.py` and `main_window.py` with it. Prerequisite: None. TDD: Verify validation in `test_config.py` handles the new Enum serialization correctly.
- Task 2: Extract hardcoded interval numbers in `actions.py` (typing delay) and `runner.py` (polling interval) and colors in `main_window.py` into named constants. Prerequisite: None. TDD: Verify constants are referenced correctly in `test_actions.py`.

# Phase 3: Concurrency and Thread Safety

- Task 1: Protect `self._is_running` flag in `runner.py` using a thread-safe primitive like `QMutex` or a python `threading.Event`. Prerequisite: None. TDD: Test in `test_runner.py` that stop requests cancel active polling loops safely.
- Task 2: Make `main_window.py` pass a deep copy of the steps to `runner.py` to prevent concurrent list mutations. Prerequisite: None. TDD: Test in `test_main_window.py` that updating the step list widget does not mutate steps inside the active runner.
- Task 3: Add a global try-except safety block to `runner.py`'s worker thread loop to catch exceptions and emit `error_occurred`. Prerequisite: None. TDD: Test in `test_runner.py` that thread failures correctly bubble up via signal instead of crashing.
