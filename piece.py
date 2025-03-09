from enum import Enum


class Color(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2


class PieceType(str, Enum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"
    EMPTY = "0"


class Piece:
    def __init__(self, piece_type: PieceType, board_index: int, color: Color):
        self.piece_type = piece_type
        self.board_index = board_index
        self.color = color

    def __repr__(self) -> str:
        return f"{self.color.name} {self.piece_type.name}"
