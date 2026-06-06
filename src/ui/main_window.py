from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutoFlow")
        self.resize(800, 600)
        
        # Central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        
        # Step list widget
        self.step_list = QListWidget(central_widget)
        self.step_list.setObjectName("step_list")
        
        layout.addWidget(self.step_list)
        self.setCentralWidget(central_widget)
