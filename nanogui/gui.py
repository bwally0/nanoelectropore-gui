import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PySide6.QtGui import QAction
import pyqtgraph as pg
import numpy as np
from nanogui.context import ApplicationContext, get_app_context
from nanogui.server import TCPServer

class ConnectionPanelWidget(QWidget):
    """Widget for setting up the connection to the server."""
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(300, 120)
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Connection Panel"))

        ### Host and Port Inputs ###
        host_layout = QHBoxLayout()
        self.host_label = QLabel("Host:")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g. 127.0.0.1")
        host_layout.addWidget(self.host_label)
        host_layout.addWidget(self.host_input)

        port_layout = QHBoxLayout()
        self.port_label = QLabel("Port: ")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("e.g. 8888")
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
    """Widget for setting the control bits."""
    def __init__(self, update_callback) -> None:
        super().__init__()
        self.setFixedSize(300, 300)
        self.update_callback = update_callback

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
        self.update_button.clicked.connect(self._on_update_clicked)
        main_layout.addWidget(self.update_button)

        self.setLayout(main_layout)
    
    def get_control_bits(self) -> list[int]:
        """Get the control bits from the signal selectors.
        
        returns:
            list[int]: List of control bits.
        """
        return [int(combo_box.currentText()) for combo_box in self.signal_selectors][::-1]
    
    def _on_update_clicked(self) -> None:
        """Update the control bits and call the update callback."""
        control_bits = self.get_control_bits()
        if self.update_callback:
            self.update_callback(control_bits)

class DataPanelWidget(QWidget):
    """Widget for displaying data."""
    def __init__(self) -> None:
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

    def plot_test_data(self) -> None:
        """Plot some test data on the plot widget."""
        x = np.linspace(0, 20, 1000)
        y = 2.5 * np.sin(0.1 * x) + 4.5 + np.random.normal(-0.5, 0.5, size=x.shape)

        self.plot_widget.plot(x, y, pen=(255, 0, 0))


class MainWindow(QMainWindow):
    """Main application window.
    
    params:
        context (ApplicationContext): Application context.
        server (TCPServer): TCPServer instance.
    """
    def __init__(self, context: ApplicationContext, server: TCPServer) -> None:
        super().__init__()
        self._context = context
        self._server = server
        
        self.setFixedSize(940, 600)
        self.setWindowTitle("Quantum-NanoElectroPore Controller GUI")

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

        self._control_panel_widget = ControlPanelWidget(self.update_control_bits)
        left_panel.addWidget(self._control_panel_widget)

        right_panel = QVBoxLayout()
        self._data_panel_widget = DataPanelWidget()
        right_panel.addWidget(self._data_panel_widget)

        central_widget.setLayout(main_layout)
        main_layout.addLayout(left_panel)
        main_layout.addLayout(right_panel)

        ### Message Handling ###
        self.statusBar().showMessage(self._context.get_message())
        self._context.message_changed.connect(self.statusBar().showMessage)

        ### Connect Buttons ###
        self._connection_panel_widget.start_button.clicked.connect(self.start_server)
        self._connection_panel_widget.stop_button.clicked.connect(self.stop_server)

    def start_server(self) -> None:
        """Start the server with the host and port specified in the connection panel."""
        host = self._connection_panel_widget.host_input.text()
        port = int(self._connection_panel_widget.port_input.text())

        if not host or not port:
            self._context.set_message("Please set the host and port.")
            return
        
        try:
            self._context.set_host(host)
            self._context.set_port(port)
            self._server.start_server()

            self._connection_panel_widget.start_button.setEnabled(False)
            self._connection_panel_widget.stop_button.setEnabled(True)
        except ValueError:
            self._context.set_message("Invalid port number.")
        except Exception as e:
            print(str(e))
            self._context.set_message(str(e))

    def stop_server(self) -> None:
        """Stop the server."""
        self._server.stop_server()
        self._connection_panel_widget.start_button.setEnabled(True)
        self._connection_panel_widget.stop_button.setEnabled(False)

    def update_control_bits(self, control_bits: list[int]):
        """Update the control bits in context and send to client.
        
        params:
            control_bits: List of control bits.
        """
        try:
            self._context.set_control_bits(control_bits)
            self._server.send_control_bits()
        except Exception as e:
            print(str(e))
            self._context.set_message(str(e))

def run() -> None:
    """Run the application."""
    app = QApplication(sys.argv)
    context = get_app_context()
    server = TCPServer(context)
    window = MainWindow(context, server)
    window.show()
    sys.exit(app.exec())