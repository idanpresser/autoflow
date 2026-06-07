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
