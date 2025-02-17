import pygame
import pygame.freetype
from moviepy.editor import ImageSequenceClip
import os
import re


# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = (700+80)*6, (600+60)*6
BOARD_ROWS, BOARD_COLS = 6, 7
CELL_SIZE = min(700*6 // BOARD_COLS, 600*6 // BOARD_ROWS)
FPS = 0.75  # Frames per second for the video

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
LIME = (0, 255, 0)
SILVER = (192, 192, 192)
LIGHT_BLUE = (82, 148, 255)
LIGHT_RED = (255, 64, 64)
LIGHT_YELLOW = (255, 229, 64)
BACKGROUND_COLOR = LIGHT_BLUE
O_COLOR = LIGHT_RED
X_COLOR = LIGHT_YELLOW
# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts
font = pygame.freetype.SysFont(None, 40)
result_font = pygame.freetype.SysFont(None, 60*6)


def draw_board():
    screen.fill(BACKGROUND_COLOR)
    # pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, HEIGHT))
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            pygame.draw.circle(screen, WHITE,
                               (col * CELL_SIZE + CELL_SIZE // 2+240,
                                row * CELL_SIZE + CELL_SIZE // 2+180),
                               CELL_SIZE // 2 - 40,0)


def draw_piece(row, col, piece):
    color = O_COLOR if piece == 'O' else X_COLOR if piece == 'X' else WHITE
    pygame.draw.circle(screen, color,
                       (col * CELL_SIZE + CELL_SIZE // 2+240,
                        row * CELL_SIZE + CELL_SIZE // 2+180),
                       CELL_SIZE // 2 - 40,0)


def draw_result(result):
    # screen.fill(WHITE)
    text_surface, text_rect = result_font.render(result, BLACK)
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(text_surface, text_rect)


def parse_board_state(board_state):
    lines = board_state.strip().split('\n') # Skip the column numbers
    board = []
    for line in lines:
        row = re.findall(r'\| (.) ', line)
        if len(row) == BOARD_COLS:
            board.append(row)
    # print(board)
    return board


def create_video(history):
    frames = []

    for frame_num, state in enumerate(history):

        draw_board()
        board = parse_board_state(state)
        for row, line in enumerate(board):
            for col, piece in enumerate(line):
                if piece != '_':
                    draw_piece(row, col, piece)
        if "O wins" in state:
            draw_result('Red Player Wins!')
        elif "X wins" in state:
            draw_result('Yellow Player Wins!')
        pygame.display.flip()
        frame_name = f"frame_{frame_num:03d}.png"
        pygame.image.save(screen, frame_name)
        frames.append(frame_name)

        clock.tick(FPS)

    # Create video from frames
    clip = ImageSequenceClip(frames, fps=FPS)
    clip.write_videofile("connect4_game.mp4", fps=FPS)

    # Clean up temporary frame files
    for frame in frames:
        os.remove(frame)


# Example usage
# history = [
#     """Step 20------------
#
#   0   1   2   3   4   5   6
# | * | * | * | * | * | * | * |
# | * | * | X | O | * | * | * |
# | * | * | O | X | * | * | * |
# | * | X | O | O | X | * | * |
# | O | X | O | X | X | * | * |
# | X | O | X | X | O | O | * |
#
# meta-llama3-405b-instruct-maas takes move 4""",
#     """Step 21------------
#
#   0   1   2   3   4   5   6
# | * | * | * | * | * | * | * |
# | * | * | X | O | * | * | * |
# | * | * | O | X | O | * | * |
# | * | X | O | O | X | * | * |
# | O | X | O | X | X | * | * |
# | X | O | X | X | O | O | * |
# """,
# """
# O wins!!!!!!!!!!"""
# ]
from clean_history_connect4 import clean_history
# print(clean_history)
create_video(clean_history)
pygame.quit()
