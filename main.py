import sys
from PySide6.QtWidgets import QApplication
from main_window import PostManagerApp 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PostManagerApp()
    window.show()
    sys.exit(app.exec())