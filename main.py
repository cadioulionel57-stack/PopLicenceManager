import sys
import traceback

from PySide6.QtWidgets import QApplication

try:
    print("1")
    from database.init_database import initialiser

    print("2")
    from ui.main_window import MainWindow

    print("3")
    initialiser()

    print("4")
    app = QApplication(sys.argv)

    print("5")
    window = MainWindow()

    print("6")
    window.show()

    print("7")
    sys.exit(app.exec())

except Exception:
    traceback.print_exc()