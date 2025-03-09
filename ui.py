import pygame
import time
from enum import Enum
from engine import Engine, PieceType, Piece, Color


class InputMode(Enum):
    """Enum to represent different input modes."""

    CLICK = 1
    DRAG = 2


class AnimationType(Enum):
    """Enum to represent different animation types."""

    MOVE = 1
    CAPTURE = 2
    CHECK = 3
    PROMOTION = 4


class ChessUI:
    """A reusable Chess UI system with animation and input handling."""

    def __init__(
        self,
        engine: Engine,
        cell_size=80,
        light_color=(245, 164, 66),
        dark_color=(54, 32, 6),
    ):
        """
        Initialize the Chess UI system.

        Args:
            engine: The chess engine instance
            cell_size: Size of each board cell in pixels
            light_color: RGB color for light squares
            dark_color: RGB color for dark squares
        """
        self.engine: Engine = engine
        self.cell_size = cell_size
        self.light_color = pygame.Color(*light_color)
        self.dark_color = pygame.Color(*dark_color)

        # Input state
        self.selected_index = None
        self.dragging = False
        self.drag_piece_index = None
        self.drag_offset = (0, 0)
        self.list_of_moves = []
        self.time_mouse_down = None
        self.mouse_pos_prev = (0, 0)

        # Animation state
        self.animations = []
        self.animation_speed = 12  # Cells per second

        # Configuration
        self.drag_threshold_px = 5
        self.click_threshold_ms = 300
        self.enable_animations = True

        # Assets
        self.piece_assets = {}

    def load_assets(self, asset_paths):
        """
        Load piece assets from given paths.

        Args:
            asset_paths: Dictionary mapping piece characters to image file paths
        """
        for key, path in asset_paths.items():
            self.piece_assets[key] = pygame.image.load(path)
        self.scale_assets()

    def scale_assets(self):
        """Scale all loaded assets to match the cell size."""
        for key in self.piece_assets:
            image = self.piece_assets[key]
            scale_factor = self.cell_size / image.get_width()
            self.piece_assets[key] = pygame.transform.scale(
                image,
                (
                    image.get_width() * scale_factor,
                    image.get_height() * scale_factor,
                ),
            )

    def handle_input(self, mouse_pos, mouse_state, current_time):
        """
        Handle mouse input for both click and drag modes.

        Args:
            mouse_pos: Current mouse position (x, y)
            mouse_state: Tuple of mouse button states (left, middle, right)
            current_time: Current game time in milliseconds

        Returns:
            bool: True if a move was made, False otherwise
        """
        mouse_x, mouse_y = mouse_pos
        left_button, _, _ = mouse_state
        did_move = False

        # Convert mouse position to board coordinates
        board_x = int(mouse_x / self.cell_size)
        board_y = int(mouse_y / self.cell_size)

        # Check if coordinates are valid
        valid_coords = 0 <= board_x < 8 and 0 <= board_y < 8
        current_index = board_y * 8 + board_x if valid_coords else -1

        # START MOUSE DOWN
        if left_button and self.time_mouse_down is None:
            # If there's an active animation, ignore input
            if self.animations:
                return False

            # Mouse just pressed down, record the time
            self.time_mouse_down = current_time

            # Pre-select a piece if it's valid, but don't commit to click or drag yet
            if valid_coords:
                piece = self.engine.board[current_index]
                if (
                    piece.piece_type != PieceType.EMPTY
                    and piece.color == self.engine.active_color
                ):
                    # Calculate drag offset for potential dragging
                    piece_center_x = (board_x * self.cell_size) + (self.cell_size / 2)
                    piece_center_y = (board_y * self.cell_size) + (self.cell_size / 2)
                    self.drag_offset = (
                        piece_center_x - mouse_x,
                        piece_center_y - mouse_y,
                    )

                    # Get legal moves
                    self.list_of_moves = self.engine.get_legal_moves(current_index)

                    # Store the index for both potential click and drag
                    self.selected_index = current_index
                    self.drag_piece_index = current_index

        # WHILE MOUSE DOWN
        elif left_button and self.time_mouse_down is not None:
            # Check if we should enter drag mode
            if not self.dragging and self.drag_piece_index is not None:
                # Calculate distance moved since mouse down
                prev_x, prev_y = self.mouse_pos_prev
                dx = mouse_x - prev_x
                dy = mouse_y - prev_y
                distance_moved = (dx**2 + dy**2) ** 0.5

                if distance_moved > self.drag_threshold_px:
                    # Enter drag mode
                    self.dragging = True

        # END MOUSE UP
        elif not left_button and self.time_mouse_down is not None:
            time_pressed = current_time - self.time_mouse_down

            # Check if we were dragging
            if self.dragging and self.drag_piece_index is not None:
                # Handle drop
                if valid_coords and current_index in self.list_of_moves:
                    self.engine.make_move(self.drag_piece_index, current_index)
                    did_move = True

                # Reset drag state
                self.dragging = False
                self.drag_piece_index = None
                self.drag_offPieceTypeset = (0, 0)
                self.list_of_moves = []

            # Handle click (if short press and not dragging)
            elif time_pressed < self.click_threshold_ms and not self.dragging:
                if valid_coords:
                    # If we already had a piece selected
                    if self.selected_index is not None:
                        # Try to move if it's a legal move
                        if current_index in self.list_of_moves:
                            if self.enable_animations:
                                self.animate_move(self.selected_index, current_index)
                            else:
                                self.engine.make_move(
                                    self.selected_index, current_index
                                )
                            self.selected_index = None
                            self.list_of_moves = []
                            did_move = True
                        # If clicking on our own piece, select it instead
                        elif (
                            self.engine.board[current_index].piece_type
                            != PieceType.EMPTY
                            and self.engine.board[current_index].color
                            == self.engine.active_color
                        ):
                            self.selected_index = current_index
                            self.list_of_moves = self.engine.get_legal_moves(
                                self.selected_index
                            )
                        # Clicking elsewhere deselects
                        else:
                            self.selected_index = None
                            self.list_of_moves = []
                    # No piece was selected yet
                    else:
                        piece = self.engine.board[current_index]
                        if (
                            piece.piece_type != PieceType.EMPTY
                            and piece.color == self.engine.active_color
                        ):
                            self.selected_index = current_index
                            self.list_of_moves = self.engine.get_legal_moves(
                                self.selected_index
                            )
                else:
                    # Clicking outside the board deselects
                    self.selected_index = None
                    self.list_of_moves = []

            # Reset time tracker
            self.time_mouse_down = None

        # Update previous mouse position for next frame
        self.mouse_pos_prev = mouse_pos

        return did_move

    def animate_move(self, from_index, to_index):
        """
        Create an animation for moving a piece.

        Args:
            from_index: Starting board index
            to_index: Ending board index
        """
        # Get piece details
        piece: list[Piece] = self.engine.board[from_index]

        # Calculate start and end positions
        from_row, from_col = from_index // 8, from_index % 8
        to_row, to_col = to_index // 8, to_index % 8

        start_pos = (from_col * self.cell_size, from_row * self.cell_size)
        end_pos = (to_col * self.cell_size, to_row * self.cell_size)

        # Create animation data
        anim_type = AnimationType.MOVE

        # Check if it's a capture
        if self.engine.board[to_index].piece_type != PieceType.EMPTY:
            anim_type = AnimationType.CAPTURE

        # Create the animation
        animation = {
            "type": anim_type,
            "piece": piece,
            "start_pos": start_pos,
            "end_pos": end_pos,
            "start_time": time.time(),
            "duration": self.calculate_animation_duration(from_index, to_index),
            "from_index": from_index,
            "to_index": to_index,
            "completed": False,
        }

        self.animations.append(animation)

    def calculate_animation_duration(self, from_index, to_index):
        """
        Calculate the duration of an animation based on distance.

        Args:
            from_index: Starting board index
            to_index: Ending board index

        Returns:
            float: Duration in seconds
        """
        from_row, from_col = from_index // 8, from_index % 8
        to_row, to_col = to_index // 8, to_index % 8

        # Calculate Manhattan distance
        distance = abs(from_row - to_row) + abs(from_col - to_col)

        # Convert distance to time based on animation speed
        return distance / self.animation_speed

    def update_animations(self, current_time):
        """
        Update all active animations.

        Args:
            current_time: Current game time

        Returns:
            bool: True if animations are still active, False otherwise
        """
        if not self.animations:
            return False

        completed_indices = []

        for i, anim in enumerate(self.animations):
            # Skip already completed animations
            if anim["completed"]:
                completed_indices.append(i)
                continue

            # Calculate progress (0.0 to 1.0)
            elapsed = time.time() - anim["start_time"]
            progress = min(elapsed / anim["duration"], 1.0)

            # Check if animation is complete
            if progress >= 1.0:
                anim["completed"] = True
                completed_indices.append(i)

                # Execute the move in the engine
                self.engine.make_move(anim["from_index"], anim["to_index"])

        # Remove completed animations from back to front
        for i in reversed(completed_indices):
            self.animations.pop(i)

        return bool(self.animations)

    def draw(self, screen):
        """
        Draw the complete chess board with all visual elements.

        Args:
            screen: Pygame screen surface
        """
        # Draw the board grid
        self.draw_grid(screen)

        # Highlight selected piece (click mode)
        if self.selected_index is not None and not self.dragging:
            row = self.selected_index // 8
            col = self.selected_index % 8
            highlight_rect = pygame.Rect(
                col * self.cell_size,
                row * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            highlight_surface = pygame.Surface(
                (self.cell_size, self.cell_size), pygame.SRCALPHA
            )
            highlight_surface.fill((255, 255, 0, 90))  # Yellow highlight with alpha
            screen.blit(highlight_surface, highlight_rect)

        # Get indices to skip drawing (animated or dragged pieces)
        skip_indices = []

        # Add dragged piece
        if self.dragging and self.drag_piece_index is not None:
            skip_indices.append(self.drag_piece_index)

        # Add animated pieces
        for anim in self.animations:
            if not anim["completed"]:
                skip_indices.append(anim["from_index"])

        # Draw all pieces except skipped ones
        self.draw_pieces(screen, skip_indices)

        # Draw animated pieces
        self.draw_animations(screen)

        # Draw legal move indicators
        for move in self.list_of_moves:
            row = move // 8
            col = move % 8
            pos_x = int(col * self.cell_size + self.cell_size / 2)
            pos_y = int(row * self.cell_size + self.cell_size / 2)

            # Draw a semi-transparent circle
            circle_surface = pygame.Surface(
                (self.cell_size // 2, self.cell_size // 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                circle_surface,
                (255, 255, 255, 150),
                (self.cell_size // 4, self.cell_size // 4),
                self.cell_size // 4,
            )
            screen.blit(
                circle_surface,
                (pos_x - self.cell_size // 4, pos_y - self.cell_size // 4),
            )

        # Draw the dragged piece on top
        if self.dragging and self.drag_piece_index is not None:
            self.draw_dragged_piece(screen)

    def draw_grid(self, screen):
        """Draw the chess board grid."""
        for row in range(8):
            for column in range(8):
                color = self.dark_color if (row + column) % 2 != 0 else self.light_color
                pygame.draw.rect(
                    screen,
                    color,
                    pygame.Rect(
                        self.cell_size * column,
                        self.cell_size * row,
                        self.cell_size,
                        self.cell_size,
                    ),
                )

    def draw_pieces(self, screen, skip_indices=None):
        """
        Draw all chess pieces except those in skip_indices.

        Args:
            screen: Pygame screen surface
            skip_indices: List of board indices to skip
        """
        if skip_indices is None:
            skip_indices = []

        counter = 0
        for row in range(8):
            for column in range(8):
                # Skip specified pieces
                if counter in skip_indices:
                    counter += 1
                    continue

                piece = self.engine.board[counter]
                color = piece.color
                piece_type = piece.piece_type
                if piece_type != PieceType.EMPTY:
                    letter = (
                        piece.piece_type.value
                        if color == Color.BLACK
                        else piece.piece_type.value.upper()
                    )
                    if letter in self.piece_assets:
                        image = self.piece_assets[letter]
                        screen.blit(
                            image,
                            (column * self.cell_size, row * self.cell_size),
                        )
                counter += 1

    def draw_dragged_piece(self, screen):
        """Draw the currently dragged piece."""
        piece = self.engine.board[self.drag_piece_index]
        color = piece.color
        piece_type = piece.piece_type
        if piece_type != PieceType.EMPTY:
            letter = (
                piece.piece_type.value
                if color == Color.BLACK
                else piece.piece_type.value.upper()
            )
            if letter in self.piece_assets:
                image = self.piece_assets[letter]
                image = pygame.transform.hsl(image, lightness=-0.5)

                # Get mouse position and apply offset
                mouse_x, mouse_y = pygame.mouse.get_pos()
                offset_x, offset_y = self.drag_offset
                draw_x = mouse_x + offset_x - (self.cell_size / 2)
                draw_y = mouse_y + offset_y - (self.cell_size / 2)

                screen.blit(image, (draw_x, draw_y))

    def draw_animations(self, screen):
        """Draw all active animations."""
        for anim in self.animations:
            if anim["completed"]:
                continue

            # Calculate current position based on progress
            elapsed = time.time() - anim["start_time"]
            progress = min(elapsed / anim["duration"], 1.0)

            # Use easing function for smoother animation
            eased_progress = self.ease_out_cubic(progress)

            start_x, start_y = anim["start_pos"]
            end_x, end_y = anim["end_pos"]

            current_x = start_x + (end_x - start_x) * eased_progress
            current_y = start_y + (end_y - start_y) * eased_progress

            # Draw the animated piece
            piece = anim["piece"]
            letter = (
                piece.piece_type.value
                if piece.color == Color.BLACK
                else piece.piece_type.value.upper()
            )
            if letter in self.piece_assets:
                image = self.piece_assets[letter]
                screen.blit(image, (current_x, current_y))

    def ease_out_cubic(self, x):
        """Cubic easing function for smooth animations."""
        return 1 - pow(1 - x, 3)
