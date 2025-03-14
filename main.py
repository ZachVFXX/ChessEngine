import pygame_gui.core.text
import pygame_gui.ui_manager
from engine import Engine, Color
import pygame
from ui import ChessUI
from enum import Enum
import pygame_gui

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


class GameState(str, Enum):
    PLAYING = "playing"
    BLACK_WIN = "black_win"
    WHITE_WIN = "white_win"
    MAIN_MENU = "main_menu"
    OPTION_MENU = "option_menu"


def main() -> None:
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((1280, 720))

    play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((350, 275), (100, 50)),
        text="Play",
        object_id="main_menu_play_game",
        visible=False,
    )

    engine = Engine()

    # Create the Chess UI system
    chess_ui = ChessUI(engine)

    game_state: GameState = GameState.MAIN_MENU

    # Load assets
    chess_ui.load_assets(asset_paths)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play_button:
                    game_state = GameState.PLAYING
            manager.process_events(event)

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
            go_back_button = pygame_gui.elements.UIButton((250, 250), "Go back")

        if game_state == GameState.WHITE_WIN:
            screen.fill(pygame.Color(255, 255, 255))
            go_back_button = pygame_gui.elements.UIButton((250, 250), "Go back")

        if game_state == GameState.MAIN_MENU:
            screen.fill(pygame.Color(36, 26, 4))
            play_button.visible = True
            pygame_gui.elements.UILabel((1000, 100), "Coucou")
        else:
            play_button.visible = False
        manager.update(dt)
        manager.draw_ui(screen)
        # Update display
        pygame.display.flip()
        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()
