from engine import Engine, Color, PieceType
import pygame

LIGHT_BG_COLOR = pygame.Color(245, 164, 66)
DARK_BG_COLOR = pygame.Color(54, 32, 6)
CELL_SIZE: int = 80


def draw_grid(screen: pygame.Surface) -> None:
    for row in range(8):
        for column in range(8):
            color = LIGHT_BG_COLOR if (row + column) % 2 != 0 else DARK_BG_COLOR
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
            "/home/zach/Dev/ChessEngine/assets/Classic/Pieces/Chess - black classic/Rook.png"
        ),
    }


def draw_pieces(
    screen: pygame.Surface, engine: Engine, dict_of_sprite: dict[str, pygame.Surface]
) -> None:
    counter = 0
    for row in range(8):
        for column in range(8):
            piece = engine.board[counter]
            color = piece.color
            piece_type = piece.piece_type
            if piece_type == PieceType.EMPTY:
                print("NONE")
            else:
                letter = (
                    piece.piece_type.value
                    if color == Color.BLACK
                    else piece.piece_type.value.upper()
                )
                screen.blit(
                    dict_of_sprite[letter], (column * CELL_SIZE, row * CELL_SIZE)
                )
            counter += 1


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    engine = Engine()

    dict_of_sprite = load_assets()

    running = True

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")
        draw_grid(screen)
        draw_pieces(screen, engine, dict_of_sprite)
        # flip() the display to put your work on screen
        pygame.display.flip()

        dt = clock.tick(60) / 1000
    pygame.quit()


if __name__ == "__main__":
    main()
