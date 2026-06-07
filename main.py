import glob
import json
import logging
import sys

from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.tray_icon import SystemTrayIcon
from src.utils.hotkeys import register_hotkey, unregister_all

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("autoflow")


def load_profile_hotkeys(window: MainWindow) -> None:
    """
    Scans the profiles/ directory for JSON profile files and registers
    a hotkey for each profile that has a 'hotkey' field.
    """
    import os
    profiles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")
    if not os.path.isdir(profiles_dir):
        logger.info("No profiles/ directory found — skipping profile hotkey loading")
        return

    for filepath in glob.glob(os.path.join(profiles_dir, "*.json")):
        try:
            with open(filepath, encoding="utf-8") as f:
                profile = json.load(f)
            hotkey = profile.get("hotkey")
            profile_name = profile.get("profile_name", filepath)
            if hotkey:
                window.setup_hotkey(hotkey)
                logger.info("Registered hotkey '%s' for profile '%s'", hotkey, profile_name)
        except Exception:
            logger.exception("Failed to load profile from %s", filepath)


def setup_failsafe(window: MainWindow) -> None:
    """
    Registers a fail-safe Escape hotkey that stops all running workflows.
    """
    def on_failsafe() -> None:
        logger.warning("Fail-safe triggered — aborting all running workflows")
        if window.runner is not None:
            window.runner.stop()

    try:
        register_hotkey("escape", on_failsafe)
        logger.info("Fail-safe hotkey (Escape) registered")
    except Exception:
        logger.exception("Failed to register fail-safe hotkey")


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()

    app = QApplication(sys.argv)

    window = MainWindow()

    # System tray icon
    tray = SystemTrayIcon(window)
    tray.show()

    # Register default hotkey to run the workflow
    try:
        window.setup_hotkey("ctrl+shift+r")
    except Exception as e:
        logger.warning("Global hotkey registration failed: %s", e)

    # Load all profile hotkeys from profiles/ directory
    load_profile_hotkeys(window)

    # Register fail-safe hotkey (Escape aborts all workflows)
    setup_failsafe(window)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
