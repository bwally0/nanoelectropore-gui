import socket
import struct
import threading
from PySide6.QtCore import QObject, Signal
from nanogui.context import ApplicationContext

class ServerSignals(QObject):
    data_received = Signal(list)

class TCPServer:
    """TCP server for sending control bits to a client.
    
    params:
        context (ApplicationContext): The application context.
    """
    def __init__(self, context: ApplicationContext) -> None:
        self._context = context
        self._server_socket = None
        self._client_socket = None
        self._client_address = None
        self._running = False
        self.signals = ServerSignals()
    
    def start_server(self) -> None:
        """Start server given host and port from context."""
        host = self._context.get_host()
        port = self._context.get_port()

        if not host or not port:
            print("Please set the host and port.")
            self._context.set_message("Please set the host and port.")
            return

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((host, port))
        self._server_socket.listen(1)
        print(f"Server listening on {host}:{port}")
        self._context.set_message(f"Server listening on {host}:{port}")

        self._running = True
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def _accept_connections(self) -> None:
        """Accept incoming connections."""
        while self._running:
            try:
                if not self._client_socket:
                    print("Waiting for connection...")
                    self._context.set_message("Waiting for connection...")

                self._client_socket, self._client_address = self._server_socket.accept()
                print(f"Connection from {self._client_address}")
                self._context.set_message(f"Connection from {self._client_address}")
                threading.Thread(target=self._handle_client, daemon=True).start()
            except OSError as e:
                if self._running:
                    print(str(e))
                    self._context.set_message(str(e))
                break


    def _handle_client(self) -> None:
        """Handle client connection and incoming messages."""
        while self._running and self._client_socket:
            try:
                data = self._client_socket.recv(160)
                if not data:
                    print("Client disconnected.")
                    self._context.set_message("Client disconnected.")
                    break

                i16_list = list(struct.unpack('>80h', data))
                # print(f"Received integers: {i16_list}")
                self.signals.data_received.emit(i16_list)
            except ConnectionAbortedError:
                print("Connection aborted by host.")
                self._context.set_message("Connection aborted by server.")
                break
            except ConnectionResetError:
                print("Client connection reset.")
                self._context.set_message("Client connection reset.")
                break
            except struct.error as e:
                print(f"Error decoding data: {e}")

        self._cleanup_client()

    def _cleanup_client(self) -> None:
        """Cleanup after client disconnects."""
        if self._client_socket:
            try:
                self._client_socket.close()
            except OSError:
                pass

        self.signals.data_received.emit([])
        self._client_socket = None
        self._client_address = None
        print("Ready for a new connection.")
        self._context.set_message("Ready for a new connection.")

    def send_control_bits(self) -> None:
        """Send control bits to client."""
        if not self._running:
            print("Server not running.")
            self._context.set_message("Server not running.")
            return
        
        if self._client_socket:
            control_bits = self._context.get_control_bits()
            self._client_socket.send(control_bits.to_bytes(1, byteorder="big"))

            binary_representation = f"0b{control_bits:08b}"
            print(f"Sent control bits: {binary_representation}")
            self._context.set_message(f"Sent control bits: {binary_representation}")
        else:
            print("Client not connected.")
            self._context.set_message("Client not connected.")

    def stop_server(self) -> None:
        """Stop the server."""
        self._running = False
        self.signals.data_received.emit([])
        if self._client_socket:
            self._client_socket.close()
        if self._server_socket:
            self._server_socket.close()
        print("Server stopped.")
        self._context.set_message("Server stopped.")