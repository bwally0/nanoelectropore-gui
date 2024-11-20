import socket
import threading
from nanogui.context import ApplicationContext

class TCPServer:
    def __init__(self, context: ApplicationContext) -> None:
        self._context = context
        self._server_socket = None
        self._client_socket = None
        self._client_address = None
        self._running = False
    
    def start_server(self) -> None:
        host = self._context.get_host()
        port = self._context.get_port()

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind((host, port))
        self._server_socket.listen(1)
        print(f"Server listening on {host}:{port}")
        self._context.set_message(f"Server listening on {host}:{port}")

        self._running = True
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def stop_server(self) -> None:
        self._running = False
        self._running = False
        if self._client_socket:
            self._client_socket.close()
        if self._server_socket:
            self._server_socket.close()
        print("Server stopped.")
        self._context.set_message("Server stopped.")