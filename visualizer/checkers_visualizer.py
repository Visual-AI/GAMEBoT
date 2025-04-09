import pygame
import pygame.freetype
from PIL.ImageOps import scale
from moviepy.editor import ImageSequenceClip,VideoClip
import os
import re
import math
import numpy as np
# Initialize Pygame
pygame.init()

# Constants
BOARD_SIZE = 8
CELL_SIZE = 100
WIDTH = HEIGHT = BOARD_SIZE * CELL_SIZE
PIECE_RADIUS = CELL_SIZE // 2 - 10
FPS = 1

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
BEIGE = (245, 222, 179)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
RED=(255, 0, 0)

# Set up the display with scaling
SCALE = 4
SCALED_WIDTH = WIDTH * SCALE
SCALED_HEIGHT = HEIGHT * SCALE
screen = pygame.display.set_mode((SCALED_WIDTH, SCALED_HEIGHT))
clock = pygame.time.Clock()

# Fonts
result_font = pygame.freetype.SysFont(None, 50 * SCALE)
move_font = pygame.freetype.SysFont(None, 30 * SCALE)

def pygame_surface_to_numpy(surface):
    """Convert Pygame surface to numpy array in the format moviepy expects."""
    surf_string = pygame.image.tostring(surface, 'RGB')
    surf_array = np.frombuffer(surf_string, dtype=np.uint8)
    return surf_array.reshape((HEIGHT*SCALE, WIDTH*SCALE, 3))

def draw_board():
    """Draw the checkers board"""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect = pygame.Rect(col * CELL_SIZE * SCALE, row * CELL_SIZE * SCALE,
                               CELL_SIZE * SCALE, CELL_SIZE * SCALE)
            color = BEIGE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, rect)


def draw_crown(surface, center_x, center_y, size, color):
    """Draw a realistic crown with aligned points and base"""
    # Scale factor for crown size
    crown_scale = size * 0.8

    # Base points of the crown
    base_width = crown_scale * 1.4
    base_height = crown_scale * 0.4
    base_left = center_x - base_width / 2
    base_right = center_x + base_width / 2
    base_top = center_y - base_height / 2
    base_bottom = center_y + base_height / 2

    # Draw the base of the crown
    base_points = [
        (base_left, base_bottom),
        (base_left, base_top),
        (base_right, base_top),
        (base_right, base_bottom)
    ]
    pygame.draw.polygon(surface, color, base_points)
    pygame.draw.polygon(surface, BLACK, base_points, max(2, SCALE // 2))

    # Draw the points of the crown
    num_points = 3
    point_height = crown_scale * 0.8

    # Adjust point positions to align with base width
    point_spacing = base_width / (num_points - 1)  # Space between points

    for i in range(num_points):
        # Calculate x position for each point
        x_base = base_left + point_spacing * i

        # For the middle point
        if i == 1:
            point_points = [
                (x_base - point_spacing / 4, base_top),  # Left base of point
                (x_base, base_top - point_height),  # Top of point
                (x_base + point_spacing / 4, base_top),  # Right base of point
            ]
        # For the outer points
        else:
            point_points = [
                (x_base - point_spacing / 4, base_top),  # Left base of point
                (x_base, base_top - point_height),  # Top of point
                (x_base + point_spacing / 4, base_top),  # Right base of point
            ]

        pygame.draw.polygon(surface, color, point_points)
        pygame.draw.polygon(surface, BLACK, point_points, max(2, SCALE // 2))

        # Draw a small circle (jewel) at the top of each point
        jewel_radius = crown_scale * 0.12
        pygame.draw.circle(surface, color,
                           (int(x_base), int(base_top - point_height)),
                           int(jewel_radius))
        pygame.draw.circle(surface, BLACK,
                           (int(x_base), int(base_top - point_height)),
                           int(jewel_radius), max(1, SCALE // 4))

    # Draw decorative circles (jewels) on the base
    jewel_radius = crown_scale * 0.15
    for i in range(2):
        x_pos = base_left + base_width * (i + 1) / 3
        y_pos = base_top + base_height * 0.5
        pygame.draw.circle(surface, color,
                           (int(x_pos), int(y_pos)),
                           int(jewel_radius))
        pygame.draw.circle(surface, BLACK,
                           (int(x_pos), int(y_pos)),
                           int(jewel_radius), max(1, SCALE // 4))


def draw_piece(row, col, piece_type):
    """Draw a checker piece at the correct position"""
    # Center the piece in the cell
    center_x = (col * CELL_SIZE + CELL_SIZE // 2) * SCALE
    center_y = (row * CELL_SIZE + CELL_SIZE // 2) * SCALE

    # Draw the main piece
    color = WHITE if piece_type.lower() == 'w' else BLACK
    pygame.draw.circle(screen, color, (center_x, center_y), PIECE_RADIUS * SCALE)

    # Draw a border around the piece
    border_color = BLACK if piece_type.lower() == 'w' else WHITE
    pygame.draw.circle(screen, border_color, (center_x, center_y), PIECE_RADIUS * SCALE, max(2, SCALE))

    # If it's a king (uppercase), draw a crown
    if piece_type.isupper():
        crown_color = GOLD if piece_type == 'W' else SILVER
        crown_size = PIECE_RADIUS * SCALE * 0.8
        draw_crown(screen, center_x, center_y, crown_size, crown_color)


def draw_result(result):
    text_surface, text_rect = result_font.render(result, SILVER)
    text_rect.center = (WIDTH*SCALE // 2, HEIGHT*SCALE // 2)
    screen.blit(text_surface, text_rect)


def draw_move_indicator(move_text):
    """Draw the current move text"""
    text_surface, text_rect = move_font.render(move_text, BLACK)
    text_rect.bottomleft = (10, SCALED_HEIGHT - 10)
    screen.blit(text_surface, text_rect)


def parse_board_state(state_text):
    """Parse the board state from the text format"""
    board_matches = re.findall(r"\[(.*?)\]", state_text)

    if not board_matches:
        return None, None

    board = []
    for row in board_matches:
        pieces = [piece.strip().strip("'\"") for piece in row.split(',')]
        board.append(pieces)

    move_match = re.search(r"takes move ([^D\n]*)", state_text)
    move_text = move_match.group(1) if move_match else ""

    return board, move_text


def create_video(history):
    """Create a video from the game history"""
    frames_array = []

    for frame_num, state in enumerate(history):
        screen.fill(WHITE)
        draw_board()

        board, move_text = parse_board_state(state)
        if board:
            for row_idx, row in enumerate(board):
                for col_idx, piece in enumerate(row):
                    if piece != '_':
                        draw_piece(row_idx, col_idx, piece)

        if move_text:
            draw_move_indicator(f"Move: {move_text}")
        result_match = re.search(r"([^\n]*)!!!!!!", state)
        result_text = result_match.group(1) if result_match else ""
        if result_text:
            draw_result(result_text)
        pygame.display.flip()
        #
        # frame_name = f"frame_{frame_num:03d}.png"
        # pygame.image.save(screen, frame_name)
        # frames.append(frame_name)
        # clock.tick(FPS)

        # Convert the current screen to numpy array and store
        frame_array = pygame_surface_to_numpy(screen)
        frames_array.append(frame_array)
        if result_text:
            frames_array.append(frame_array)
        clock.tick(FPS)
    # clip = ImageSequenceClip(frames, fps=FPS)
    # clip.write_videofile("checkers_game.mp4", fps=FPS)

    # for frame in frames:
    #     os.remove(frame)
    def make_frame(t):
        frame_idx = min(int(t * FPS), len(frames_array) - 1)
        return frames_array[frame_idx]

    # Calculate duration based on number of frames and FPS
    duration = 1.5

    # Create and save the video
    clip = VideoClip(make_frame, duration=duration)
    clip.write_videofile("checkers_game.mp4", fps=FPS)
    print("Video creation complete.")


def main():
    history = open(args.path)

    for line in history:
        if line.startswith('Cycle 0='):
            break
    clean_history = ''
    for line in history:
        clean_history += line
    clean_history = clean_history.split('Step')
    # print(clean_history)
    print("Starting video creation...")
    create_video(clean_history)
    print("Video creation process completed.")
    pygame.quit()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Parser for visualizer')
    parser.add_argument('path', type=str, help='Path to the input file', default='game.log')
    parser.add_argument('--output', default='checkers_game.mp4')
    args = parser.parse_args()
    main()