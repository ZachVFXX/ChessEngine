from engine import Engine, Piece
from pydantic import TypeAdapter


class Room:
    def __init__(self, player1, player2):
        self.players = {"white": player1, "black": player2}
        self.engine = Engine()
        self.current_turn = self.engine.active_color.name.lower()

    def get_opponent(self, player):
        return (
            self.players["white"]
            if self.players["black"] == player
            else self.players["black"]
        )

    def make_move(self, player, from_pos, to_pos):
        if self.players[self.current_turn] != player:
            return False, "Not your turn"

        if self.engine.make_move(from_pos, to_pos):
            return True, None
        else:
            return False, "Invalid move"

    def get_full_board(self):
        ListPieceValidator = TypeAdapter(list[Piece])
        board = ListPieceValidator.validate_python(self.engine.board)
        board = ListPieceValidator.dump_json(board)
        print(board)
        return board
