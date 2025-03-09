from board import Board, Color, PieceType, Piece


class Engine(Board):
    def __init__(self):
        super().__init__()
        self.load_fen_notation(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )

    def _get_pawn_moves(self, position: int) -> list[int]:
        moves = []
        piece = self.board[position]
        row, col = position // 8, position % 8

        # Direction depends on color
        direction = -1 if piece.color == Color.WHITE else 1

        # Forward move (1 square)
        new_row = row + direction
        if 0 <= new_row < 8:
            new_pos = new_row * 8 + col
            if self.board[new_pos].piece_type == PieceType.EMPTY:
                moves.append(new_pos)

                # Double move from starting position
                if (piece.color == Color.WHITE and row == 6) or (
                    piece.color == Color.BLACK and row == 1
                ):
                    new_row = row + 2 * direction
                    if 0 <= new_row < 8:
                        new_pos = new_row * 8 + col
                        if self.board[new_pos].piece_type == PieceType.EMPTY:
                            moves.append(new_pos)

        # Capture moves (diagonal)
        for col_offset in [-1, 1]:
            new_col = col + col_offset
            new_row = row + direction

            # Check board boundaries
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                new_pos = new_row * 8 + new_col
                target = self.board[new_pos]

                # Regular capture
                if target.piece_type != PieceType.EMPTY and target.color != piece.color:
                    moves.append(new_pos)

                # En passant capture
                elif self.board:
                    if self.en_passant_target is not None:
                        ep_pos = self._get_index_from_pgn(self.en_passant_target)
                        if new_pos == ep_pos:
                            moves.append(new_pos)

        return moves

    def _get_knight_moves(self, position: int) -> list[int]:
        moves = []
        piece = self.board[position]
        row, col = position // 8, position % 8

        # Knight moves in an L-shape: 2 squares in one direction, 1 square perpendicular
        knight_moves = [
            (-2, -1),
            (-2, 1),
            (2, -1),
            (2, 1),  # 2 vertical, 1 horizontal
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),  # 1 vertical, 2 horizontal
        ]

        for row_offset, col_offset in knight_moves:
            new_row, new_col = row + row_offset, col + col_offset

            # Check if the new position is on the board
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                new_pos = new_row * 8 + new_col
                target_piece = self.board[new_pos]

                # Can move if square is empty or contains enemy piece
                if (
                    target_piece.piece_type == PieceType.EMPTY
                    or target_piece.color != piece.color
                ):
                    moves.append(new_pos)

        return moves

    def _get_bishop_moves(self, position: int) -> list[int]:
        moves = []
        piece = self.board[position]
        row, col = position // 8, position % 8

        # Bishops move diagonally
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for row_dir, col_dir in directions:
            new_row, new_col = row, col

            # Continue moving in this direction until we hit the edge or another piece
            while True:
                new_row += row_dir
                new_col += col_dir

                # Check if we're still on the board
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break

                new_pos = new_row * 8 + new_col
                target_piece = self.board[new_pos]

                # Empty square - valid move
                if target_piece.piece_type == PieceType.EMPTY:
                    moves.append(new_pos)
                    continue

                # Enemy piece - valid move, but can't go further
                if target_piece.color != piece.color:
                    moves.append(new_pos)

                # After hitting any piece (friend or foe), we can't continue in this direction
                break

        return moves

    def _get_rook_moves(self, position: int) -> list[int]:
        moves = []
        piece = self.board[position]
        row, col = position // 8, position % 8

        # Rooks move horizontally and vertically
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for row_dir, col_dir in directions:
            new_row, new_col = row, col

            # Continue moving in this direction until we hit the edge or another piece
            while True:
                new_row += row_dir
                new_col += col_dir

                # Check if we're still on the board
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break

                new_pos = new_row * 8 + new_col
                target_piece = self.board[new_pos]

                # Empty square - valid move
                if target_piece.piece_type == PieceType.EMPTY:
                    moves.append(new_pos)
                    continue

                # Enemy piece - valid move, but can't go further
                if target_piece.color != piece.color:
                    moves.append(new_pos)

                # After hitting any piece (friend or foe), we can't continue in this direction
                break

        return moves

    def _get_queen_moves(self, position: int) -> list[int]:
        # Queen combines bishop and rook movements
        assert self.board[position].piece_type == PieceType.QUEEN
        return self._get_bishop_moves(position) + self._get_rook_moves(position)

    def _get_king_moves(self, position: int) -> list[int]:
        moves = []
        piece = self.board[position]
        row, col = position // 8, position % 8

        # Normal king moves (one square in any direction)
        for row_offset in [-1, 0, 1]:
            for col_offset in [-1, 0, 1]:
                if row_offset == 0 and col_offset == 0:
                    continue  # Skip the king's current position

                new_row, new_col = row + row_offset, col + col_offset

                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    new_pos = new_row * 8 + new_col
                    target = self.board[new_pos]

                    if (
                        target.piece_type == PieceType.EMPTY
                        or target.color != piece.color
                    ):
                        moves.append(new_pos)

        # Castling
        if not self.is_in_check(piece.color):
            if piece.color == Color.WHITE:
                # Kingside castling
                if self.white_can_castle_king_side:
                    if (
                        self.board[position + 1].piece_type == PieceType.EMPTY
                        and self.board[position + 2].piece_type == PieceType.EMPTY
                        and not self._is_square_attacked(position + 1, Color.BLACK)
                    ):
                        print("White castling king side")
                        moves.append(position + 2)

                # Queenside castling
                if self.white_can_castle_queen_side:
                    if (
                        self.board[position - 1].piece_type == PieceType.EMPTY
                        and self.board[position - 2].piece_type == PieceType.EMPTY
                        and self.board[position - 3].piece_type == PieceType.EMPTY
                        and not self._is_square_attacked(position - 2, Color.BLACK)
                    ):
                        print("White castling queen side")
                        moves.append(position - 2)
            else:
                # Kingside castling for black
                if self.black_can_castle_king_side:
                    if (
                        self.board[position + 1].piece_type == PieceType.EMPTY
                        and self.board[position + 2].piece_type == PieceType.EMPTY
                        and not self._is_square_attacked(position + 2, Color.WHITE)
                    ):
                        print("Black castling king side")
                        moves.append(position + 2)

                # Queenside castling for black
                if self.black_can_castle_queen_side:
                    if (
                        self.board[position - 1].piece_type == PieceType.EMPTY
                        and self.board[position - 2].piece_type == PieceType.EMPTY
                        and self.board[position - 3].piece_type == PieceType.EMPTY
                        and not self._is_square_attacked(position - 2, Color.WHITE)
                    ):
                        print("Black castling queen side")
                        moves.append(position - 2)

        return moves

    def _is_square_attacked(self, position: int, by_color: Color) -> bool:
        """Check if a square is under attack by pieces of the given color"""
        # Save the current piece at this position
        original_piece = self.board[position]

        # Place a temporary piece of the opposite color
        temp_color = Color.BLACK if by_color == Color.WHITE else Color.WHITE
        self.board[position] = Piece(PieceType.PAWN, position, temp_color)

        # Check if any of the opponent's pieces can move to this square
        for i, piece in enumerate(self.board):
            if piece.color == by_color:
                # Use appropriate move generation based on piece type
                if piece.piece_type == PieceType.PAWN:
                    # Special handling for pawns since they capture differently than they move
                    row, col = i // 8, i % 8
                    direction = 1 if by_color == Color.WHITE else -1

                    for col_offset in [-1, 1]:
                        new_col = col + col_offset
                        new_row = row + direction

                        if 0 <= new_row < 8 and 0 <= new_col < 8:
                            new_pos = new_row * 8 + new_col
                            if new_pos == position:
                                # Restore the original piece and return True
                                self.board[position] = original_piece
                                return True
                else:
                    # For other pieces, use their normal move generation
                    moves = []
                    if piece.piece_type == PieceType.KNIGHT:
                        moves = self._get_knight_moves(i)
                    elif piece.piece_type == PieceType.BISHOP:
                        moves = self._get_bishop_moves(i)
                    elif piece.piece_type == PieceType.ROOK:
                        moves = self._get_rook_moves(i)
                    elif piece.piece_type == PieceType.QUEEN:
                        moves = self._get_queen_moves(i)
                    elif piece.piece_type == PieceType.KING:
                        # For the king, we need basic moves without castling
                        row, col = i // 8, i % 8
                        for row_offset in [-1, 0, 1]:
                            for col_offset in [-1, 0, 1]:
                                if row_offset == 0 and col_offset == 0:
                                    continue
                                new_row, new_col = row + row_offset, col + col_offset
                                if 0 <= new_row < 8 and 0 <= new_col < 8:
                                    moves.append(new_row * 8 + new_col)

                    if position in moves:
                        # Restore the original piece and return True
                        self.board[position] = original_piece
                        return True

        # Restore the original piece
        self.board[position] = original_piece
        return False

    def _is_king_in_check_after_move(self, from_pos: int, to_pos: int) -> bool:
        """Test if a move would leave or put the king in check"""
        # Save current board state
        original_to_piece = self.board[to_pos]
        original_from_piece = self.board[from_pos]

        # Make the move temporarily
        self._move(from_pos, to_pos)

        # Find the king of the current player
        king_pos = None
        for i, p in enumerate(self.board):
            if p.piece_type == PieceType.KING and p.color == self.active_color:
                king_pos = i
                break

        # If king not found, something went wrong
        if king_pos is None:
            # Restore the board
            self.board[from_pos] = original_from_piece
            self.board[to_pos] = original_to_piece
            return True

        # Check if the king is under attack
        opponent_color = (
            Color.BLACK if self.active_color == Color.WHITE else Color.WHITE
        )
        is_in_check = self._is_square_attacked(king_pos, opponent_color)

        # Restore the board
        self.board[from_pos] = original_from_piece
        self.board[to_pos] = original_to_piece

        return is_in_check

    def is_in_check(self, color: Color) -> bool:
        """Check if the given color's king is in check"""
        # Find the king
        king_pos = None
        for i, p in enumerate(self.board):
            if p.piece_type == PieceType.KING and p.color == color:
                king_pos = i
                break

        if king_pos is None:
            return False  # Should not happen in a valid game

        # Check if the king is under attack
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self._is_square_attacked(king_pos, opponent_color)

    def is_checkmate(self, color: Color) -> bool:
        """Check if the given color is in checkmate"""
        # If not in check, it's not checkmate
        if not self.is_in_check(color):
            return False

        # Check if any move can get out of check
        saved_active_color = self.active_color
        self.active_color = color  # Temporarily set active color to check moves

        for i, p in enumerate(self.board):
            if p.color == color:
                legal_moves = self.get_legal_moves(i)
                if legal_moves:
                    self.active_color = saved_active_color
                    return False

        # Restore active color
        self.active_color = saved_active_color

        # No legal moves and in check = checkmate
        return True

    def get_legal_moves(self, position: int) -> list[int]:
        """
        Returns a list of all legal destination indices for the piece at the given position

        Args:
            position (int): The index of the piece on the board

        Returns:
            list[int]: List of indices where the piece can legally move
        """
        piece = self.board[position]

        # If there's no piece or it's not this player's turn, return empty list
        if piece.piece_type == PieceType.EMPTY or piece.color != self.active_color:
            return []

        # Get basic moves for the piece
        if piece.piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(position)
        elif piece.piece_type == PieceType.KNIGHT:
            moves = self._get_knight_moves(position)
        elif piece.piece_type == PieceType.BISHOP:
            moves = self._get_bishop_moves(position)
        elif piece.piece_type == PieceType.ROOK:
            moves = self._get_rook_moves(position)
        elif piece.piece_type == PieceType.QUEEN:
            moves = self._get_queen_moves(position)
        elif piece.piece_type == PieceType.KING:
            moves = self._get_king_moves(position)
        else:
            return []

        # Filter out moves that would leave the king in check
        return [
            move
            for move in moves
            if not self._is_king_in_check_after_move(position, move)
        ]

    def make_move(self, from_pos: int, to_pos: int) -> bool:
        """
        Make a move if it's legal and update the board state

        Args:
            from_pos (int): Starting position index
            to_pos (int): Destination position index

        Returns:
            bool: True if move was made, False if illegal
        """
        # Get the piece and check if it exists and belongs to current player
        piece = self.board[from_pos]
        if piece.piece_type == PieceType.EMPTY or piece.color != self.active_color:
            return False

        # Get legal moves and check if destination is legal
        legal_moves = self.get_legal_moves(from_pos)
        if to_pos not in legal_moves:
            return False

        # Special handling for castling
        if piece.piece_type == PieceType.KING and abs(from_pos - to_pos) == 2:
            # Kingside castling
            if to_pos > from_pos:
                rook_from = from_pos + 3
                rook_to = from_pos + 1
            # Queenside castling
            else:
                rook_from = from_pos - 4
                rook_to = from_pos - 1

            # Move the rook
            self._move(rook_from, rook_to)

        # Special handling for en passant capture
        is_en_passant = False
        if piece.piece_type == PieceType.PAWN and self.en_passant_target:
            ep_pos = self._get_index_from_pgn(self.en_passant_target)
            if to_pos == ep_pos:
                is_en_passant = True
                # Remove the captured pawn
                capture_pos = to_pos + (8 if piece.color == Color.WHITE else -8)
                self.board[capture_pos] = Piece(
                    PieceType.EMPTY, capture_pos, Color.EMPTY
                )

        # Save capture info for halfmove clock
        is_capture = self.board[to_pos].piece_type != PieceType.EMPTY

        # Make the move
        self._move(from_pos, to_pos)

        # Handle pawn promotion (in a real game you would prompt for piece type)
        if piece.piece_type == PieceType.PAWN:
            # Check if pawn reached the last rank
            if (piece.color == Color.WHITE and to_pos // 8 == 7) or (
                piece.color == Color.BLACK and to_pos // 8 == 0
            ):
                # Auto-promote to queen for this demo
                self.board[to_pos].piece_type = PieceType.QUEEN

        # Update castling rights if king or rook moved
        if piece.piece_type == PieceType.KING:
            if piece.color == Color.WHITE:
                self.white_can_castle_king_side = False
                self.white_can_castle_queen_side = False
            else:
                self.black_can_castle_king_side = False
                self.black_can_castle_queen_side = False

        elif piece.piece_type == PieceType.ROOK:
            # Update based on which rook moved
            if from_pos == 7:  # h1
                self.white_can_castle_king_side = False
            elif from_pos == 0:  # a1
                self.white_can_castle_queen_side = False
            elif from_pos == 63:  # h8
                self.black_can_castle_king_side = False
            elif from_pos == 56:  # a8
                self.black_can_castle_queen_side = False

        # Update en passant target
        if piece.piece_type == PieceType.PAWN and abs(from_pos - to_pos) == 16:
            # Pawn made a double move, set en passant target
            middle_pos = (from_pos + to_pos) // 2
            self.en_passant_target = self._get_pgn_from_index(middle_pos)
        else:
            self.en_passant_target = None

        # Update halfmove clock (reset on pawn move or capture)
        if piece.piece_type == PieceType.PAWN or is_capture or is_en_passant:
            self.half_move = 0
        else:
            self.half_move += 1

        # Update fullmove number after black moves
        if self.active_color == Color.BLACK:
            self.full_move += 1

        # Switch the active player
        self.active_color = (
            Color.BLACK if self.active_color == Color.WHITE else Color.WHITE
        )

        return True
