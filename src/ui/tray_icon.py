from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QIcon

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        # Use standard computer icon as fallback
        icon = parent.style().standardIcon(QStyle.SP_ComputerIcon) if parent else QIcon()
        super().__init__(icon, parent)
        self.parent = parent
        self.setToolTip("AutoFlow")
        
        self.menu = QMenu()
        
        self.restore_action = self.menu.addAction("Restore")
        self.restore_action.triggered.connect(self.on_restore)
        
        self.menu.addSeparator()
        
        self.exit_action = self.menu.addAction("Exit")
        self.exit_action.triggered.connect(self.on_exit)
        
        self.setContextMenu(self.menu)
        
    def on_restore(self):
        if self.parent:
            self.parent.showNormal()
            self.parent.activateWindow()
            
    def on_exit(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
