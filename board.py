from enum import StrEnum, Enum

class Color(Enum):
    NONE = 0
    WHITE = 1
    BLACK = 2

class PieceType(StrEnum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"
    VOID = "0"

class Piece:
    def __init__(self, piece_type: PieceType = PieceType.VOID, color: Color = Color.NONE):
        self.color = color
        self.piece_type = piece_type
        
    def __repr__(self) -> str:
        return f"{self.piece_type}, color: {self.color}"        

class Board:
    def __init__(self):
        self.board: list[Piece] = [Piece(PieceType.VOID) for _ in range(64)]
        self.active_color: Color = Color.WHITE
        self.white_can_castle_queen_side: bool = False
        self.white_can_castle_king_side: bool = False
        self.black_can_castle_queen_side: bool = False
        self.black_can_castle_king_side: bool = False
        self.half_move: int = 0 # how many moves both players have made since the last pawn advance or piece capture
        self.full_move: int = 0 # number of time black played
        self.en_passant_target: str | None = None # possible en passant targets
        
    def load_fen_notation(self, fen: str) -> None:
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
        
        if castling == "-":
            self.black_can_castle_king_side = False
            self.black_can_castle_queen_side = False
            self.white_can_castle_king_side = False
            self.white_can_castle_queen_side = False
        else:
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
        self.board = [Piece(PieceType.VOID) for _ in range(64)]
        
        # Place pieces
        board_index = 0
        for char in pieces:
            if char == '/':
                continue
            elif char.isdigit():
                board_index += int(char)
            else:
                color = Color.WHITE if char.islower() else Color.BLACK
                piece_type = PieceType(char.lower())
                self.board[board_index] = Piece(piece_type, color)
                board_index += 1
        
        
    def return_fen_notation(self) -> str:
        fen_string: str
        row = 0
        counter = 0
        for piece in self.board:
            if piece == 0:
                counter += 1
            else:
                if counter < 0:
                    fen_string + counter
                fen_string + piece
                
        
    
    def print_current_board(self):
        for row in range(8):
            for col in range(8):
                piece: Piece = self.board[row * 8 + col]
                if piece.piece_type == PieceType.VOID:
                    print(".", end=" ")
                else:
                    print(piece.piece_type.value if piece.color == Color.WHITE else piece.piece_type.value.upper(), end=" ")
            print()
        print("white" if self.active_color == Color.WHITE else "black", "turn")
        print(f"White: King side: {self.white_can_castle_king_side}, Queen side: {self.white_can_castle_queen_side}")
        print(f"Black: King side: {self.black_can_castle_king_side}, Queen side: {self.black_can_castle_queen_side}")
        print(f"Full move: {self.full_move}")
        print(f"Half move: {self.half_move}")
        print(f"En passant: {self.en_passant_target}")

if __name__ == "__main__":
    b = Board()
    b.load_fen_notation("r4b1r/pppk2pp/5P2/5p1Q/1q1npK2/1bN5/P1P2P1P/R4BNR w - - 0 14")
    b.print_current_board()
    print(b.board)    