import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from nanogui.context import ApplicationContext, get_app_context
from nanogui.server import TCPServer

class GraphWidget(QWidget):
    """Graph widget with label."""
    def __init__(self, label: str) -> None:
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.channel_label = QLabel(label)
        self.channel_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.channel_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", "Analog Value")
        self.plot_widget.setLabel("bottom", "Time (us)")
        layout.addWidget(self.plot_widget)

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color=(255, 0, 0), width=2))

    def update_plot(self, x_data: list[int], y_data: list[int]) -> None:
        """Update the plot with new data."""
        if len(x_data) > 0:
            self.plot_widget.setXRange(min(x_data), max(x_data), padding=0.1)

        self.curve.setData(x=x_data, y=y_data)

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
        self.host_input.setText("127.0.0.1")
        host_layout.addWidget(self.host_label)
        host_layout.addWidget(self.host_input)

        port_layout = QHBoxLayout()
        self.port_label = QLabel("Port: ")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("e.g. 8888")
        self.port_input.setText("8888")
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
        layout = QGridLayout()
        self.setLayout(layout)

        self.channel_a = GraphWidget("Channel A")
        self.channel_b = GraphWidget("Channel B")
        self.channel_c = GraphWidget("Channel C")
        self.channel_d = GraphWidget("Channel D")

        layout.addWidget(self.channel_a, 0, 0)
        layout.addWidget(self.channel_b, 0, 1)
        layout.addWidget(self.channel_c, 1, 0)
        layout.addWidget(self.channel_d, 1, 1)

    def update_channel(self, channel: str, x_data: list[int], y_data: list[int]) -> None:
        """Update a specific channel graph."""
        if channel == "A":
            self.channel_a.update_plot(x_data, y_data)
        elif channel == "B":
            self.channel_b.update_plot(x_data, y_data)
        elif channel == "C":
            self.channel_c.update_plot(x_data, y_data)
        elif channel == "D":
            self.channel_d.update_plot(x_data, y_data)


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

        self.channel_data = {
            "A": {"time": [], "value": []},
            "B": {"time": [], "value": []},
            "C": {"time": [], "value": []},
            "D": {"time": [], "value": []},
        }
        
        self.setFixedSize(1280, 980)
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

        self._server.signals.data_received.connect(self.update_graph)

    def update_graph(self, data: list[int]) -> None:
        """Update graphs with received data."""
        channel_a_data = data[0:16]
        channel_b_data = data[16:32]
        channel_c_data = data[32:48]
        channel_d_data = data[48:64]
        time_data = data[64:80]

        self.channel_data["A"]["value"].extend(channel_a_data)
        self.channel_data["B"]["value"].extend(channel_b_data)
        self.channel_data["C"]["value"].extend(channel_c_data)
        self.channel_data["D"]["value"].extend(channel_d_data)
        self.channel_data["A"]["time"].extend(time_data)
        self.channel_data["B"]["time"].extend(time_data)
        self.channel_data["C"]["time"].extend(time_data)
        self.channel_data["D"]["time"].extend(time_data)

        self._data_panel_widget.update_channel("A", self.channel_data["A"]["time"], self.channel_data["A"]["value"])
        self._data_panel_widget.update_channel("B", self.channel_data["B"]["time"], self.channel_data["B"]["value"])
        self._data_panel_widget.update_channel("C", self.channel_data["C"]["time"], self.channel_data["C"]["value"])
        self._data_panel_widget.update_channel("D", self.channel_data["D"]["time"], self.channel_data["D"]["value"])

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