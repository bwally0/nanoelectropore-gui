import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtGui import QAction
from nanogui.context import ApplicationContext, get_app_context
from nanogui.server import TCPServer

class MainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext, server: TCPServer) -> None:
        super().__init__()
        self._context = context
        self._server = server
        
        self.setWindowTitle("NanoElectroPore GUI")
        self.setMinimumSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        ### Menu Bar ###
        menu_bar = self.menuBar()

        ### File Menu ###
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self.statusBar().showMessage("Connection status: Disconnected.")


def run():
    app = QApplication(sys.argv)
    context = get_app_context()
    server = TCPServer(context)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())