from engine import Engine, Color, PieceType
import pygame

from ui import ChessUI

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


def handle_chess_input(
    engine: Engine,
    mouse_pos: tuple[int, int],
    mouse_state: bool,
    mouse_pos_prev: tuple[int, int],
    time_mouse_down: float,
    current_time: float,
    selected_index: int,
    dragging: bool,
    drag_piece_index: int,
    drag_offset: float,
    list_of_moves: list[float],
    scaled_asset: dict[str, pygame.Surface],
):
    """
    Unified input handling system supporting both click and drag-and-drop.

    Args:
        engine: The chess engine instance
        mouse_pos: Current mouse position (x, y)
        mouse_state: Tuple of mouse button states (left, middle, right)
        mouse_pos_prev: Previous mouse position for detecting movement
        time_mouse_down: Time when mouse was pressed down (or None)
        current_time: Current game time in milliseconds
        selected_index: Currently selected piece index (for click mode)
        dragging: Boolean indicating if a piece is being dragged
        drag_piece_index: Index of the piece being dragged
        drag_offset: Offset from mouse to piece center
        list_of_moves: List of legal moves for the selected piece
        scaled_asset: Dictionary of scaled piece images

    Returns:
        tuple: (selected_index, dragging, drag_piece_index, drag_offset, list_of_moves,
               time_mouse_down, did_move)
    """
    mouse_x, mouse_y = mouse_pos
    left_button, _, _ = mouse_state
    did_move = False

    # Convert mouse position to board coordinates (used in multiple places)
    board_x = int(mouse_x / CELL_SIZE)
    board_y = int(mouse_y / CELL_SIZE)

    # Check if coordinates are valid
    valid_coords = 0 <= board_x < 8 and 0 <= board_y < 8
    current_index = board_y * 8 + board_x if valid_coords else -1

    # Constants
    DRAG_THRESHOLD_PX = 5  # Pixels of movement to trigger drag mode
    CLICK_THRESHOLD_MS = 300  # Max milliseconds to register as a click

    # START MOUSE DOWN
    if left_button and time_mouse_down is None:
        # Mouse just pressed down, record the time
        time_mouse_down = current_time

        # Pre-select a piece if it's valid, but don't commit to click or drag yet
        if valid_coords:
            piece = engine.board[current_index]
            if (
                piece.piece_type != PieceType.EMPTY
                and piece.color == engine.active_color
            ):
                # Calculate drag offset for potential dragging
                piece_center_x = (board_x * CELL_SIZE) + (CELL_SIZE / 2)
                piece_center_y = (board_y * CELL_SIZE) + (CELL_SIZE / 2)
                drag_offset = (piece_center_x - mouse_x, piece_center_y - mouse_y)

                # Get legal moves
                list_of_moves = engine.get_legal_moves(current_index)

                # Store the index for both potential click and drag
                selected_index = current_index
                drag_piece_index = current_index

    # WHILE MOUSE DOWN
    elif left_button and time_mouse_down is not None:
        # Check if we should enter drag mode
        if not dragging and drag_piece_index is not None:
            # Calculate distance moved since mouse down
            prev_x, prev_y = mouse_pos_prev
            dx = mouse_x - prev_x
            dy = mouse_y - prev_y
            distance_moved = (dx**2 + dy**2) ** 0.5

            if distance_moved > DRAG_THRESHOLD_PX:
                # Enter drag mode
                dragging = True

    # END MOUSE UP
    elif not left_button and time_mouse_down is not None:
        time_pressed = current_time - time_mouse_down

        # Check if we were dragging
        if dragging and drag_piece_index is not None:
            # Handle drop
            if valid_coords and current_index in list_of_moves:
                engine.make_move(drag_piece_index, current_index)
                did_move = True

            # Reset drag state
            dragging = False
            drag_piece_index = None
            drag_offset = (0, 0)
            list_of_moves = []

        # Handle click (if short press and not dragging)
        elif time_pressed < CLICK_THRESHOLD_MS and not dragging:
            if valid_coords:
                # If we already had a piece selected
                if selected_index is not None:
                    # Try to move if it's a legal move
                    if current_index in list_of_moves:
                        engine.make_move(selected_index, current_index)
                        selected_index = None
                        list_of_moves = []
                        did_move = True
                    # If clicking on our own piece, select it instead
                    elif (
                        engine.board[current_index].piece_type != PieceType.EMPTY
                        and engine.board[current_index].color == engine.active_color
                    ):
                        selected_index = current_index
                        list_of_moves = engine.get_legal_moves(selected_index)
                    # Clicking elsewhere deselects
                    else:
                        selected_index = None
                        list_of_moves = []
                # No piece was selected yet
                else:
                    piece = engine.board[current_index]
                    if (
                        piece.piece_type != PieceType.EMPTY
                        and piece.color == engine.active_color
                    ):
                        selected_index = current_index
                        list_of_moves = engine.get_legal_moves(selected_index)
            else:
                # Clicking outside the board deselects
                selected_index = None
                list_of_moves = []

        # Reset time tracker
        time_mouse_down = None

    return (
        selected_index,
        dragging,
        drag_piece_index,
        drag_offset,
        list_of_moves,
        time_mouse_down,
        did_move,
    )


def draw_chess_board(
    screen: pygame.Surface,
    engine: Engine,
    scaled_asset: dict[str, pygame.Surface],
    selected_index: int,
    list_of_moves: list[int],
    dragging: bool,
    drag_piece_index: int,
    mouse_pos: tuple[int, int],
    drag_offset: float,
):
    """
    Draw the complete chess board including pieces, selection, legal moves, and dragged piece.

    Args:
        screen: Pygame screen surface
        engine: The chess engine instance
        scaled_asset: Dictionary of scaled piece images
        selected_index: Currently selected piece index (for click mode)
        list_of_moves: List of legal moves for the selected/dragged piece
        dragging: Boolean indicating if a piece is being dragged
        drag_piece_index: Index of the piece being dragged
        mouse_pos: Current mouse position (x, y)
        drag_offset: Offset from mouse to piece center
    """
    # Draw the board grid
    draw_grid(screen)

    # Highlight selected piece (click mode)
    if selected_index is not None and not dragging:
        row = selected_index // 8
        col = selected_index % 8
        highlight_rect = pygame.Rect(
            col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE
        )
        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 0, 90))  # Yellow highlight with alpha
        screen.blit(highlight_surface, highlight_rect)

    # Draw legal move indicators
    for move in list_of_moves:
        row = move // 8
        col = move % 8
        pos_x = int(col * CELL_SIZE + CELL_SIZE / 2)
        pos_y = int(row * CELL_SIZE + CELL_SIZE / 2)

        # Draw a semi-transparent circle
        circle_surface = pygame.Surface(
            (CELL_SIZE // 2, CELL_SIZE // 2), pygame.SRCALPHA
        )
        pygame.draw.circle(
            circle_surface,
            (255, 255, 255, 150),
            (CELL_SIZE // 4, CELL_SIZE // 4),
            CELL_SIZE // 4,
        )
        screen.blit(circle_surface, (pos_x - CELL_SIZE // 4, pos_y - CELL_SIZE // 4))

    # Draw all pieces except the dragged one
    counter = 0
    for row in range(8):
        for column in range(8):
            # Skip the piece being dragged
            if counter == drag_piece_index and dragging:
                counter += 1
                continue

            piece = engine.board[counter]
            color = piece.color
            piece_type = piece.piece_type
            if piece_type != PieceType.EMPTY:
                letter = (
                    piece.piece_type.value
                    if color == Color.BLACK
                    else piece.piece_type.value.upper()
                )
                image = scaled_asset[letter]
                screen.blit(
                    image,
                    (column * CELL_SIZE, row * CELL_SIZE),
                )
            counter += 1

    # Draw the dragged piece on top
    if dragging and drag_piece_index is not None:
        piece = engine.board[drag_piece_index]
        color = piece.color
        piece_type = piece.piece_type
        if piece_type != PieceType.EMPTY:
            letter = (
                piece.piece_type.value
                if color == Color.BLACK
                else piece.piece_type.value.upper()
            )
            image = scaled_asset[letter]

            # Adjust position with offset for smooth dragging
            mouse_x, mouse_y = mouse_pos
            offset_x, offset_y = drag_offset
            draw_x = mouse_x + offset_x - (CELL_SIZE / 2)
            draw_y = mouse_y + offset_y - (CELL_SIZE / 2)

            screen.blit(image, (draw_x, draw_y))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    engine = Engine()

    # Create the Chess UI system
    chess_ui = ChessUI(engine)

    # Load assets
    asset_paths = {
        "k": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/King.png",
        "n": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Knight.png",
        "b": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Bishop.png",
        "p": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Pawn.png",
        "q": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Queen.png",
        "r": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Rook.png",
        "K": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/King.png",
        "N": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Knight.png",
        "B": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Bishop.png",
        "P": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Pawn.png",
        "Q": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Queen.png",
        "R": "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - white classic/Rook.png",
    }
    chess_ui.load_assets(asset_paths)

    running = True
    while running:
        # Get current time
        current_time = pygame.time.get_ticks()

        # Poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear screen
        screen.fill("purple")

        # Update animations
        chess_ui.update_animations(current_time)

        # Handle input
        mouse_pos = pygame.mouse.get_pos()
        mouse_state = pygame.mouse.get_pressed()
        chess_ui.handle_input(mouse_pos, mouse_state, current_time)

        # Draw the chess board
        chess_ui.draw(screen)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
