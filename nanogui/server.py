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
        while self._running and self._client_socket:
            try:
                data = self._client_socket.recv(1024)
                if not data:
                    print("Client disconnected.")
                    self._context.set_message("Client disconnected.")
                    break

                print(f"Received: {data.decode()}")
            except ConnectionResetError:
                print("Client connection reset.")
                self._context.set_message("Client connection reset.")
                break

        self._cleanup_client()

    def _cleanup_client(self) -> None:
        if self._client_socket:
            try:
                self._client_socket.close()
            except OSError:
                pass
        self._client_socket = None
        self._client_address = None
        print("Ready for a new connection.")
        self._context.set_message("Ready for a new connection.")

    def send_control_bits(self) -> None:
        if not self._running:
            print("Server not running.")
            self._context.set_message("Server not running.")
            return
        
        if self._client_socket:
            control_bits = self._context.get_control_bits()
            self._client_socket.send(control_bits.to_bytes(1, byteorder="big"))

            binary_representation = f"0b{control_bits:08b}"
            self._client_socket.send(control_bits.to_bytes(1, byteorder="big"))
            print(f"Sent control bits: {binary_representation}")
            self._context.set_message(f"Sent control bits: {binary_representation}")
        else:
            print("Client not connected.")
            self._context.set_message("Client not connected.")

    def stop_server(self) -> None:
        self._running = False
        if self._client_socket:
            self._client_socket.close()
        if self._server_socket:
            self._server_socket.close()
        print("Server stopped.")
        self._context.set_message("Server stopped.")