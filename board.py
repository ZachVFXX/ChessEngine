from piece import Piece, Color, PieceType

CHAR_TO_COLUMN = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
COLUMN_TO_CHAR = {v: k for k, v in CHAR_TO_COLUMN.items()}


class Board:
    def __init__(self):
        self.board: list[Piece] = self.clear_board()
        self.active_color: Color = Color.WHITE
        self.white_can_castle_queen_side: bool = False
        self.white_can_castle_king_side: bool = False
        self.black_can_castle_queen_side: bool = False
        self.black_can_castle_king_side: bool = False
        self.half_move: int = 0
        self.full_move: int = 1
        self.en_passant_target: str | None = None

    def _move(self, from_: int, to_: int) -> None:
        self.board[to_] = self.board[from_]
        self.board[to_].board_index = to_
        self.board[from_] = Piece(PieceType.EMPTY, from_, Color.EMPTY)

    def _get_index_from_pgn(self, pgn: str) -> int:
        """Get the index for the board array from an pgn format string

        exemple: f7 = 13

        Args:
            pgn (str): A pgn representation of the position

        Returns:
            int: The index for the board array
        """
        column = CHAR_TO_COLUMN[pgn[0]]
        row = int(pgn[1])
        return (8 - row) * 8 + column

    def _get_pgn_from_index(self, index: int) -> str:
        """Get the pgn format string from the board array index

        exemple: 13 = f7

        Args:
            index (int): The index for the board array

        Returns:
            str: The pgn representation of the position
        """
        row = 8 - (index // 8)
        column = COLUMN_TO_CHAR[index % 8]
        return f"{column}{row}"

    def clear_board(self) -> list[Piece]:
        return [Piece(PieceType.EMPTY, i, Color.EMPTY) for i in range(64)]

    def load_fen_notation(
        self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    ) -> None:
        """Load a fen string to the board

        Format: <piece_placement> <active_color> <castling_rights> <en_passant> <halfmove> <fullmove>
        Example: 4k2r/6r1/8/8/8/8/3R4/R3K3 w Qk - 0 1

        Args:
            fen (str): The fen string
        """
        try:
            pieces, active_color, castling, en_passant, halfmove, fullmove = fen.split()
        except ValueError:
            raise ValueError("Invalid FEN string format")

        self.active_color = Color.WHITE if active_color.lower() == "w" else Color.BLACK

        self.en_passant_target = None if en_passant.lower() == "-" else en_passant

        # Reset castling rights
        self.black_can_castle_king_side = False
        self.black_can_castle_queen_side = False
        self.white_can_castle_king_side = False
        self.white_can_castle_queen_side = False

        if castling != "-":
            for c in castling:
                match c:
                    case "Q":
                        self.white_can_castle_queen_side = True
                    case "K":
                        self.white_can_castle_king_side = True
                    case "q":
                        self.black_can_castle_queen_side = True
                    case "k":
                        self.black_can_castle_king_side = True

        self.half_move = int(halfmove)
        self.full_move = int(fullmove)

        # Reset board
        self.board = self.clear_board()

        # Place pieces
        board_index = 0
        for char in pieces:
            if char == "/":
                continue
            elif char.isdigit():
                board_index += int(char)
            else:
                color = Color.WHITE if char.isupper() else Color.BLACK
                piece_type = PieceType(char.lower())
                self.board[board_index] = Piece(piece_type, board_index, color)
                board_index += 1

    def print_current_board(self) -> None:
        show_row = 8
        for row in range(8):
            print(show_row, end=" ")
            show_row -= 1
            for col in range(8):
                piece: Piece = self.board[row * 8 + col]
                if piece.piece_type == PieceType.EMPTY:
                    print(".", end=" ")
                else:
                    print(
                        piece.piece_type.value
                        if piece.color == Color.BLACK
                        else piece.piece_type.value.upper(),
                        end=" ",
                    )
            print()
        print("  a b c d e f g h")
        print("white" if self.active_color == Color.WHITE else "black", "turn")
        print(
            f"White: King side: {self.white_can_castle_king_side}, Queen side: {self.white_can_castle_queen_side}"
        )
        print(
            f"Black: King side: {self.black_can_castle_king_side}, Queen side: {self.black_can_castle_queen_side}"
        )
        print(f"Full move: {self.full_move}")
        print(f"Half move: {self.half_move}")
        print(f"En passant: {self.en_passant_target}")
