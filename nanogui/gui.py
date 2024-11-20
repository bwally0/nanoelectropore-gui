import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PySide6.QtGui import QAction
import pyqtgraph as pg
import numpy as np
from nanogui.context import ApplicationContext, get_app_context
from nanogui.server import TCPServer

class ConnectionPanelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 120)
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Connection Panel"))

        ### Host and Port Inputs ###
        host_layout = QHBoxLayout()
        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Enter host (e.g. 127.0.0.1)")
        host_layout.addWidget(self.host_label)
        host_layout.addWidget(self.host_input)

        port_layout = QHBoxLayout()
        self.port_label = QLabel("Port: ")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter port (e.g. 8080)")
        port_layout.addWidget(self.port_label)
        port_layout.addWidget(self.port_input)

        main_layout.addLayout(host_layout)
        main_layout.addLayout(port_layout)

        ### Start and Stop Buttons ###
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

class ControlPanelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Control Panel"))

        ### Signal Selectors ###
        self.signal_selectors = []
        for i in range(8):
            row_layout = QHBoxLayout()

            label = QLabel(f"Signal {i}:")
            row_layout.addWidget(label)

            combo_box = QComboBox()
            combo_box.addItems(["0", "1"])
            combo_box.setCurrentIndex(0)
            self.signal_selectors.append(combo_box)
            row_layout.addWidget(combo_box)

            main_layout.addLayout(row_layout)

        ### Update Button ###
        self.update_button = QPushButton("Update")
        main_layout.addWidget(self.update_button)

        self.setLayout(main_layout)

class DataPanelWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 540)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        ### Plot Widget ###
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", "Conductance (G_o)")
        self.plot_widget.setLabel("bottom", "Time (s)")
        main_layout.addWidget(self.plot_widget)

        self.plot_widget.setYRange(0, 10)
        self.plot_widget.setXRange(0, 20)

        self.plot_test_data()

    def plot_test_data(self):
        x = np.linspace(0, 20, 1000)
        y = 2.5 * np.sin(0.1 * x) + 4.5 + np.random.normal(-0.5, 0.5, size=x.shape)

        self.plot_widget.plot(x, y, pen=(255, 0, 0))


class MainWindow(QMainWindow):
    def __init__(self, context: ApplicationContext, server: TCPServer) -> None:
        super().__init__()
        self._context = context
        self._server = server
        
        self.setFixedSize(940, 600)
        self.setWindowTitle("NanoElectroPore GUI")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        ### Menu Bar ###
        menu_bar = self.menuBar()

        ### File Menu ###
        file_menu = menu_bar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        ### Layouts ###
        main_layout = QHBoxLayout()

        left_panel = QVBoxLayout()
        self._connection_panel_widget = ConnectionPanelWidget()
        left_panel.addWidget(self._connection_panel_widget)
        self._control_panel_widget = ControlPanelWidget()
        left_panel.addWidget(self._control_panel_widget)

        right_panel = QVBoxLayout()
        self._data_panel_widget = DataPanelWidget()
        right_panel.addWidget(self._data_panel_widget)

        central_widget.setLayout(main_layout)
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

        self.statusBar().showMessage(self._context.get_message())
        self._context.message_changed.connect(self.statusBar().showMessage)


def run():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        #connectionPanel, #controlPanel{
            border: 1px solid lightgrey;
        }
    """)
    context = get_app_context()
    server = TCPServer(context)
    window = MainWindow(context, server)
    window.show()
    sys.exit(app.exec())