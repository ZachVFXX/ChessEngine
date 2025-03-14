import pygame
import sys
from pathlib import Path
from client import Client
from network_ui import NetworkChessUI  # Our refactored UI class


def main():
    # Initialize pygame

    client = Client()
    client.nickname = input("Enter your nickname: ")
    client.start()

    pygame.init()
    screen = pygame.display.set_mode((640, 700))
    pygame.display.set_caption("Networked Chess")
    clock = pygame.time.Clock()

    # Create client
    # Create UI with the client
    chess_ui = NetworkChessUI(client)

    MAIN = Path(__file__).parent

    # Load piece assets
    asset_paths = {
        "k": MAIN.joinpath("assets/Classic/Pieces/Chess - black classic/King.png"),
        "b": MAIN.joinpath("assets/Classic/Pieces/Chess - black classic/Bishop.png"),
        "n": MAIN.joinpath("assets/Classic/Pieces/Chess - black classic/Knight.png"),
        "p": MAIN.joinpath("assets/Classic/Pieces/Chess - black classic/Pawn.png"),
        "q": MAIN.joinpath("assets/Classic/Pieces/Chess - black classic/Queen.png"),
        "r": MAIN.joinpath("assets/Classic/Pieces/Chess - black classic/Rook.png"),
        "K": MAIN.joinpath("assets/Classic/Pieces/Chess - white classic/King.png"),
        "N": MAIN.joinpath("assets/Classic/Pieces/Chess - white classic/Knight.png"),
        "B": MAIN.joinpath("assets/Classic/Pieces/Chess - white classic/Bishop.png"),
        "P": MAIN.joinpath("assets/Classic/Pieces/Chess - white classic/Pawn.png"),
        "Q": MAIN.joinpath("assets/Classic/Pieces/Chess - white classic/Queen.png"),
        "R": MAIN.joinpath("assets/Classic/Pieces/Chess - white classic/Rook.png"),
    }

    chess_ui.load_assets(asset_paths)

    # Game loop
    running = True
    while running and not client.closed:
        current_time = pygame.time.get_ticks()

        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get mouse state
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Handle input and animations
        chess_ui.handle_input(mouse_pos, mouse_buttons, current_time)
        chess_ui.update_animations(current_time)

        # Render
        screen.fill((0, 0, 0))
        chess_ui.draw(screen)
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Clean up
    client.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
