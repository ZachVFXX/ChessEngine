import threading
from piece import Message, Color
import socket
from protocols import Response, Request
from rooms import Room


def recv_all(sock, n):
    """Helper function to receive exactly n bytes or return None if EOF is hit."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


class Server:
    def __init__(self, host="", port=55555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.client_names: dict[socket.socket, str] = {}
        self.opponent: dict[socket.socket, socket.socket] = {}
        self.rooms: dict[socket.socket, Room] = {}
        self.waiting_for_pair = None

    def handle_connect(self, client: socket.socket):
        while True:
            self.send(Response.NICKNAME, "", client)
            try:
                message = Message.recv_message(client)
                if message is None:
                    return

                r_type = message.type
                nickname = message.data

                if r_type == Request.NICKNAME:
                    self.client_names[client] = nickname
                else:
                    continue

                if not self.waiting_for_pair:
                    self.waiting_for_pair = client
                    print("Waiting for a room")
                else:
                    self.create_room(client)
                    self.send(Response.START, "", client)
                    self.send_to_opponent(Response.START, "", client)
                break
            except Exception as e:
                print(f"Error in handle_connect: {e}")
                return

    def create_room(self, client: socket.socket):
        print("Creating room.")
        room = Room(client, self.waiting_for_pair)
        self.opponent[client] = self.waiting_for_pair
        self.opponent[self.waiting_for_pair] = client

        self.send(Response.BOARD_STATE, room.get_full_board(), client)
        self.send_to_opponent(Response.BOARD_STATE, room.get_full_board(), client)

        self.send(
            Response.OPPONENT,
            self.get_client_data(client),
            self.waiting_for_pair,
        )
        self.send(
            Response.OPPONENT,
            self.get_client_data(self.waiting_for_pair),
            client,
        )

        self.send(Response.COLOR, Color.WHITE, client)
        self.send(Response.COLOR, Color.BLACK, self.waiting_for_pair)

        self.rooms[client] = room
        self.rooms[self.waiting_for_pair] = room

        print(
            f"room with {self.client_names[client]} and {self.client_names[self.waiting_for_pair]}"
        )

        self.waiting_for_pair = None

    def get_client_data(self, client: socket.socket):
        name = self.client_names[client]
        return name

    def handle(self, client: socket.socket):
        self.handle_connect(client)

        while True:
            try:
                message = Message.recv_message(client)
                if message is None:
                    break
                self.handle_receive(message, client)
            except Exception as e:
                print(f"Error in handle: {e}")
                raise
                break

        self.send_to_opponent(Response.OPPONENT_LEFT, None, client)
        self.disconnect(client)

    def disconnect(self, client: socket.socket):
        opponent = self.opponent.get(client)
        if opponent in self.opponent:
            del self.opponent[opponent]

        if client in self.opponent:
            del self.opponent[client]

        if client in self.client_names:
            del self.client_names[client]

        if opponent in self.client_names:
            del self.client_names[opponent]

        if client in self.rooms:
            del self.rooms[client]

        if opponent in self.rooms:
            del self.rooms[opponent]

        client.close()

    def handle_receive(self, message: Message, client: socket.socket):
        print("handle message", message)
        r_type = message.type
        data = message.data
        room = self.rooms[client]

        if r_type == Request.TRY_MOVE:
            from_pos = data.from_
            to_pos = data.to_
            success, error = room.make_move(client, from_pos, to_pos)
            if success:
                self.send_to_opponent(Response.DONE_MOVE, data, client)
                self.send(Response.DONE_MOVE, data, client)
            else:
                self.send(Response.ERROR, error, client)
        if r_type == Request.GET_LEGAL_MOVES:
            self.send(
                Response.LEGAL_MOVES,
                self.rooms[client].engine.get_legal_moves(data),
                client,
            )

    def send(self, r_type: Response, data: str, client: socket.socket):
        message = Message(type=r_type, data=data)
        packed_message = Message.pack(message)
        client.send(packed_message)

    def send_to_opponent(self, r_type: Response, data: str, client: socket.socket):
        opponent = self.opponent.get(client)
        if not opponent:
            return
        self.send(r_type, data, opponent)

    def listening(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()


if __name__ == "__main__":
    server = Server()
    server.listening()
