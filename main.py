import sys
from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main() -> None:
    # Load environment variables from .env file
    load_dotenv()

    app = QApplication(sys.argv)

    window = MainWindow()

    # Register default hotkey to run the workflow
    try:
        window.setup_hotkey("ctrl+shift+r")
    except Exception as e:
        print(f"Warning: Global hotkey registration failed: {e}")

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
