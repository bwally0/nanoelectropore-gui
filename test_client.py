import socket
import threading
import time

class TestClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = False

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            self.running = True
            print(f"Connected to server at {self.host}:{self.port}")
            
            threading.Thread(target=self._listen_for_messages, daemon=True).start()
        except ConnectionRefusedError:
            print(f"Could not connect to server at {self.host}:{self.port}. Is the server running?")
            self.client_socket = None

    def send_message(self, message: str):
        """Send a message to the server."""
        if self.client_socket:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
                print(f"Sent: {message}")
            except BrokenPipeError:
                print("Error: Connection to server is broken.")

    def _listen_for_messages(self):
        while self.running and self.client_socket:
            try:
                response = self.client_socket.recv(1024)
                if response:
                    print(f"Received: {response.decode('utf-8')}")
                else:
                    print("Server closed the connection.")
                    self.close_connection()
            except socket.error as e:
                if self.running:
                    print(f"Error receiving response: {e}")
                break

    def close_connection(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            print("Connection closed.")


if __name__ == "__main__":
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 8888

    client = TestClient(SERVER_HOST, SERVER_PORT)
    client.connect_to_server()

    if client.client_socket:
        client.send_message("Hello, Server!")
        time.sleep(5)
        client.send_message("Hello, Server!")

        time.sleep(5)
        client.close_connection()
