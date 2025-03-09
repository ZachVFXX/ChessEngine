from socket import socket, AF_INET, SOCK_STREAM, gethostbyname


class Server:
    def __init__(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((gethostbyname("127.0.0.1"), 12397))
        try:
            self.listen_client()
        except Exception as e:
            print(f"Error when listening to the client: {e}")

    def listen_client(self):
        self.server_socket.listen(5)
        client_connexion, client_address = self.server_socket.accept()
        while True:
            print("Connected with " + client_address[0] + ":" + str(client_address[1]))
            message = client_connexion.recv(1024).decode()
            client_connexion.send(b"Connected to the server")
            print(message)

    def send_to_client(self, message: str):
        client_connexion, client_address = self.server_socket.accept()
        print("Connected with " + client_address[0] + ":" + str(client_address[1]))
        message = client_connexion.recv(1024).decode()
        client_connexion.send(b"Connected to the server")
        print(message)


if __name__ == "__main__":
    server = Server()
    server.send_to_client("COUOU")
