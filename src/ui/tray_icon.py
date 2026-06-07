from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QStyle, QSystemTrayIcon, QWidget


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent: QWidget | None = None) -> None:
        # Use standard computer icon as fallback
        icon = (
            parent.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
            if parent
            else QIcon()
        )
        super().__init__(icon, parent)
        self._parent_widget = parent
        self.setToolTip("AutoFlow")

        self.menu = QMenu()

        self.restore_action = self.menu.addAction("Restore")
        self.restore_action.triggered.connect(self.on_restore)

        self.menu.addSeparator()

        self.exit_action = self.menu.addAction("Exit")
        self.exit_action.triggered.connect(self.on_exit)

        self.setContextMenu(self.menu)

    def on_restore(self) -> None:
        if self._parent_widget:
            self._parent_widget.showNormal()
            self._parent_widget.activateWindow()

    def on_exit(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.quit()

    def show_notification(self, title: str, message: str) -> None:
        """Shows a system tray balloon notification."""
        self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)

    def show_running(self, profile_name: str) -> None:
        """Shows a notification that a workflow profile has started running."""
        self.show_notification("AutoFlow", f"Running profile: {profile_name}")

    def show_completed(self, profile_name: str) -> None:
        """Shows a notification that a workflow profile completed successfully."""
        self.show_notification("AutoFlow", f"Profile completed: {profile_name}")

    def show_error(self, profile_name: str, error: str) -> None:
        """Shows an error notification for a workflow profile."""
        self.showMessage(
            "AutoFlow Error",
            f"Profile '{profile_name}' failed: {error}",
            QSystemTrayIcon.MessageIcon.Critical,
            5000,
        )
