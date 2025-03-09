from engine import Engine, Color, PieceType
import pygame

LIGHT_BG_COLOR = pygame.Color(245, 164, 66)
DARK_BG_COLOR = pygame.Color(54, 32, 6)
CELL_SIZE: int = 80


def draw_grid(screen: pygame.Surface) -> None:
    for row in range(8):
        for column in range(8):
            color = DARK_BG_COLOR if (row + column) % 2 != 0 else LIGHT_BG_COLOR
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(CELL_SIZE * row, CELL_SIZE * column, CELL_SIZE, CELL_SIZE),
            )


def load_assets() -> dict[str, pygame.Surface]:
    return {
        "k": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/King.png"
        ),
        "n": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Knight.png"
        ),
        "b": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Bishop.png"
        ),
        "p": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Pawn.png"
        ),
        "q": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Queen.png"
        ),
        "r": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Rook.png"
        ),
        "K": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/King.png"
        ),
        "N": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Knight.png"
        ),
        "B": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Bishop.png"
        ),
        "P": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Pawn.png"
        ),
        "Q": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Queen.png"
        ),
        "R": pygame.image.load(
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Rook.png"
        ),
    }


def scaled_assets(
    dict_of_surface: dict[str, pygame.Surface],
) -> dict[str, pygame.Surface]:
    for key in dict_of_surface:
        image = dict_of_surface[key]
        scale_factor = CELL_SIZE / image.get_width()
        dict_of_surface[key] = pygame.transform.scale(
            image,
            (
                image.get_width() * scale_factor,
                image.get_height() * scale_factor,
            ),
        )
    return dict_of_surface


def draw_pieces(
    screen: pygame.Surface, engine: Engine, dict_of_sprite: dict[str, pygame.Surface]
) -> None:
    counter = 0
    for row in range(8):
        for column in range(8):
            piece = engine.board[counter]
            color = piece.color
            piece_type = piece.piece_type
            if piece_type != PieceType.EMPTY:
                letter = (
                    piece.piece_type.value
                    if color == Color.BLACK
                    else piece.piece_type.value.upper()
                )
                image = dict_of_sprite[letter]
                screen.blit(
                    image,
                    (column * CELL_SIZE, row * CELL_SIZE),
                )
            counter += 1


def handle_piece_selection_and_movement(
    engine: Engine,
    mouse_pos: tuple[int, int],
    mouse_clicked: bool,
    selected_index: int,
    list_of_moves: list[int],
) -> tuple[int, list[int]]:
    """
    Handle selecting chess pieces and making moves when a user clicks on the board.

    Args:
        engine: The chess engine instance
        mouse_pos: The current mouse position (x, y)
        mouse_clicked: Boolean indicating if mouse was just clicked
        selected_index: The currently selected piece index (or None)
        list_of_moves: List of legal moves for the selected piece

    Returns:
        tuple: (new_selected_index, new_list_of_moves)
    """
    if not mouse_clicked:
        return selected_index, list_of_moves

    # Convert mouse position to board coordinates
    x, y = mouse_pos
    x = int(x / CELL_SIZE)
    y = int(y / CELL_SIZE)

    # Ensure coordinates are within board boundaries
    if not (0 <= x < 8 and 0 <= y < 8):
        return selected_index, list_of_moves

    # Calculate board index
    clicked_index = y * 8 + x

    # If a piece is already selected
    if selected_index is not None:
        # Check if the clicked position is a legal move
        if clicked_index in list_of_moves:
            # Make the move
            engine.make_move(selected_index, clicked_index)
            # Reset selection after move
            return None, []
        else:
            # If clicking on a different square that's not a legal move
            # Check if it's a piece that can be selected
            piece = engine.board[clicked_index]
            if (
                piece.piece_type != PieceType.EMPTY
                and piece.color == engine.active_color
            ):
                # Select new piece and get its legal moves
                legal_moves = engine.get_legal_moves(clicked_index)
                return clicked_index, legal_moves
            # If clicking on empty square or opponent's piece, deselect
            return None, []
    else:
        # If no piece is selected yet, try to select one
        piece = engine.board[clicked_index]
        if piece.piece_type != PieceType.EMPTY and piece.color == engine.active_color:
            # Get legal moves for the selected piece
            legal_moves = engine.get_legal_moves(clicked_index)
            return clicked_index, legal_moves

    # Default - no changes
    return selected_index, list_of_moves


def draw_legal_moves(screen, list_of_moves):
    """
    Draw indicators for legal moves on the screen.

    Args:
        screen: Pygame screen surface
        list_of_moves: List of legal move indices
    """
    for move in list_of_moves:
        pos_x = int((move % 8) * CELL_SIZE + CELL_SIZE / 2)
        pos_y = int((move // 8) * CELL_SIZE + CELL_SIZE / 2)
        pygame.draw.circle(
            screen, pygame.Color(255, 255, 255, 10), (pos_x, pos_y), CELL_SIZE / 4
        )


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    engine = Engine()
    engine.print_current_board()
    dict_of_sprite = load_assets()
    scaled_asset = scaled_assets(dict_of_sprite)

    running = True
    selected_index = None
    list_of_move = []

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")
        draw_grid(screen)
        draw_pieces(screen, engine, scaled_asset)

        selected_index, list_of_move = handle_piece_selection_and_movement(
            engine,
            pygame.mouse.get_pos(),
            pygame.mouse.get_just_pressed()[0],
            selected_index,
            list_of_move,
        )
        draw_legal_moves(screen, list_of_move)

        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.quit()


if __name__ == "__main__":
    main()
