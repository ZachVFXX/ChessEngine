from engine import Engine, Color
import pygame
from button import Button
from ui import ChessUI
from enum import StrEnum

asset_paths = {
    "k": "assets/Classic/Pieces/Chess - black classic/King.png",
    "n": "assets/Classic/Pieces/Chess - black classic/Knight.png",
    "b": "assets/Classic/Pieces/Chess - black classic/Bishop.png",
    "p": "assets/Classic/Pieces/Chess - black classic/Pawn.png",
    "q": "assets/Classic/Pieces/Chess - black classic/Queen.png",
    "r": "assets/Classic/Pieces/Chess - black classic/Rook.png",
    "K": "assets/Classic/Pieces/Chess - white classic/King.png",
    "N": "assets/Classic/Pieces/Chess - white classic/Knight.png",
    "B": "assets/Classic/Pieces/Chess - white classic/Bishop.png",
    "P": "assets/Classic/Pieces/Chess - white classic/Pawn.png",
    "Q": "assets/Classic/Pieces/Chess - white classic/Queen.png",
    "R": "assets/Classic/Pieces/Chess - white classic/Rook.png",
}


class GameState(StrEnum):
    PLAYING = "playing"
    BLACK_WIN = "black_win"
    WHITE_WIN = "white_win"


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    engine = Engine()

    # Create the Chess UI system
    chess_ui = ChessUI(engine)

    game_state: GameState = GameState.PLAYING

    # Load assets

    chess_ui.load_assets(asset_paths)

    running = True
    while running:
        # Poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_state == GameState.PLAYING:
            if engine.is_checkmate(Color.BLACK):
                game_state = GameState.WHITE_WIN
            elif engine.is_checkmate(Color.WHITE):
                game_state = GameState.BLACK_WIN

            # Get current time
            current_time = pygame.time.get_ticks()

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

        if game_state == GameState.BLACK_WIN:
            screen.fill(pygame.Color(0, 0, 0))
            surface = pygame.font.SysFont("arial", 24).render(
                "Black win", True, pygame.Color(255, 255, 255)
            )
            screen.blit(
                surface,
                (
                    screen.get_width() / 2 - surface.get_width() / 2,
                    screen.get_height() / 2 - surface.get_height() / 2,
                ),
            )
            button = Button(
                (100, 100),
                (100, 50),
                (255, 255, 255),
                (0, 0, 0),
                (0, 0, 0),
                text="Back",
            )
            button.draw(screen)

        if game_state == GameState.WHITE_WIN:
            screen.fill(pygame.Color(255, 255, 255))
            surface = pygame.font.SysFont("arial", 24).render(
                "White win", True, pygame.Color(0, 0, 0)
            )
            screen.blit(
                surface,
                (
                    screen.get_width() / 2 - surface.get_width() / 2,
                    screen.get_height() / 2 - surface.get_height() / 2,
                ),
            )

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
