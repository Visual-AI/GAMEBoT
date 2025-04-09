import pygame
import pygame.freetype
from moviepy.editor import ImageSequenceClip
import os
import re

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = (700 + 80) * 6, (600 + 60) * 6
BOARD_ROWS, BOARD_COLS = 6, 7
CELL_SIZE = min(700 * 6 // BOARD_COLS, 600 * 6 // BOARD_ROWS)
FPS = 2  # Frames per second for the video

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
result_font = pygame.freetype.SysFont(None, 60 * 6)


def draw_board():
    screen.fill(BACKGROUND_COLOR)
    # pygame.draw.rect(screen, BLUE, (0, 0, WIDTH, HEIGHT))
    for row in range(BOARD_ROWS):
        for col in range(BOARD_COLS):
            pygame.draw.circle(screen, WHITE,
                               (col * CELL_SIZE + CELL_SIZE // 2 + 240,
                                row * CELL_SIZE + CELL_SIZE // 2 + 180),
                               CELL_SIZE // 2 - 40, 0)


def draw_piece(row, col, piece):
    color = O_COLOR if piece == 'O' else X_COLOR if piece == 'X' else WHITE
    pygame.draw.circle(screen, color,
                       (col * CELL_SIZE + CELL_SIZE // 2 + 240,
                        row * CELL_SIZE + CELL_SIZE // 2 + 180),
                       CELL_SIZE // 2 - 40, 0)


def draw_result(result):
    # screen.fill(WHITE)
    text_surface, text_rect = result_font.render(result, BLACK)
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(text_surface, text_rect)


def parse_board_state(board_state):
    lines = board_state.strip().split('\n')  # Skip the column numbers
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
        if not history:
            continue
        draw_board()
        board = parse_board_state(state)
        for row, line in enumerate(board):
            for col, piece in enumerate(line):
                if piece != '_':
                    draw_piece(row, col, piece)

        pattern = r"(.+?)\s+wins!"
        match = re.search(pattern, state)
        if match:
            winner = match.group(1)
            draw_result('{} Wins!'.format(winner))
        pygame.display.flip()
        frame_name = f"frame_{frame_num:03d}.png"
        pygame.image.save(screen, frame_name)
        frames.append(frame_name)

        clock.tick(FPS)

    durations = [1.5] * len(frames)

    # Create video from frames
    clip = ImageSequenceClip(frames, durations=durations)
    clip.write_videofile(args.output, fps=FPS)

    for frame in frames:
        os.remove(frame)


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
    parser.add_argument('--output', default='connect4_game.mp4')
    args = parser.parse_args()
    main()
