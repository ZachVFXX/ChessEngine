import socket
import threading
from piece import Message, Piece, move
from pydantic import TypeAdapter
from protocols import Request, Response


class Client:
    def __init__(self, host="192.168.159.146", port=55555):
        self.nickname = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

        self.closed = False
        self.started = False
        self.opponent_data = None
        self.winner = None

    def start(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def send(self, request: Request, message: str):
        data = Message(type=request, data=message)
        packed_message = Message.pack(data)
        self.server.send(packed_message)

    def receive(self):
        while not self.closed:
            try:
                message = Message.recv_message(self.server)
                if message is None:
                    break
                print(f"Received message: {message}")
                self.handle_response(message)
            except Exception:
                raise
        self.close()

    def close(self):
        self.closed = True
        self.server.close()

    def handle_response(self, response: Message):
        r_type = response.type
        data = response.data

        if r_type == Response.NICKNAME:
            self.send(Request.NICKNAME, self.nickname)
        elif r_type == Response.OPPONENT:
            self.opponent_data = data
            print(f"Opponent: {self.opponent_data}")
        elif r_type == Response.START:
            self.started = True
            print("Game started!")
        elif r_type == Response.DONE_MOVE:
            print(f"Move done: {data}")
        elif r_type == Response.WINNER:
            self.winner = data
            print(f"Winner: {self.winner}")
            self.close()
        elif r_type == Response.OPPONENT_LEFT:
            print("Opponent left the game.")
            self.close()
        elif r_type == Response.BOARD_STATE:
            print("Board state")
            ListPieceValidator = TypeAdapter(list[Piece])
            board = ListPieceValidator.validate_json(data)
            board_state = board
            print(board_state)

    def make_move(self, from_pos: int, to_pos: int):
        move_data = move(from_=from_pos, to_=to_pos)
        self.send(Request.TRY_MOVE, move_data)


if __name__ == "__main__":
    client = Client()
    client.nickname = input("Enter your nickname: ")
    client.start()

    while not client.closed:
        print("xxxxxxxxxxxxxxxx")
        if client.started:
            print("playing")
            from_pos = int(input("Enter the position to move from: "))
            to_pos = int(input("Enter the position to move to: "))
            client.make_move(from_pos, to_pos)
