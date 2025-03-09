from socket import socket, AF_INET, SOCK_STREAM, gethostbyname


class Client:
    def __init__(self):
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((gethostbyname("127.0.0.1"), 12397))

        try:
            self._create_connection()
        except Exception as e:
            print(f"Error when connecting to the server: {e}")

    def _create_connection(self):
        self.client_socket.send("Starting connection with the server".encode())
        response = self.client_socket.recv(1024).decode()
        print(response)

    def send(self, message: str):
        self.client_socket.send(message.encode())
        response = self.client_socket.recv(1024).decode()
        print(response)


if __name__ == "__main__":
    client = Client()
    for i in range(10):
        message = input("send: ")
        client.send(message)
