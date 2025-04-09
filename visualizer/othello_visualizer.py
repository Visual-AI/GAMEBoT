import pygame
import pygame.freetype
from moviepy.editor import VideoClip
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 660 * 4, 660 * 4
BOARD_SIZE = 8
CELL_SIZE = min(600 * 4 // BOARD_SIZE, 600 * 4 // BOARD_SIZE)
FPS = 0.75  # Frames per second for the video

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (50, 158, 50)
LIGHT_GREEN = (144, 238, 144)
BACKGROUND_COLOR = (110, 198, 110)
LIGHT_WHITE = (214, 245, 244)
LIGHT_BLACK = (10, 41, 40)
RED=(255, 0, 0)
# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts
font = pygame.freetype.SysFont(None, 40 * 4)
result_font = pygame.freetype.SysFont(None, 70 * 4)


def pygame_surface_to_numpy(surface):
    """Convert Pygame surface to numpy array in the format moviepy expects."""
    surf_string = pygame.image.tostring(surface, 'RGB')
    surf_array = np.frombuffer(surf_string, dtype=np.uint8)
    return surf_array.reshape((HEIGHT, WIDTH, 3))


def draw_board():
    screen.fill(BACKGROUND_COLOR)
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            pygame.draw.rect(screen, GREEN,
                             (col * CELL_SIZE + 120, row * CELL_SIZE + 120,
                              CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, LIGHT_GREEN,
                             (col * CELL_SIZE + 120, row * CELL_SIZE + 120,
                              CELL_SIZE, CELL_SIZE), 3)


def draw_disc(row, col, color):
    center_x = col * CELL_SIZE + CELL_SIZE // 2 + 120
    center_y = row * CELL_SIZE + CELL_SIZE // 2 + 120
    radius = CELL_SIZE // 2 - 30
    pygame.draw.circle(screen, color, (center_x, center_y), radius)


def draw_result(result):
    text_surface, text_rect = result_font.render(result, RED)
    text_rect.center = (WIDTH // 2, HEIGHT // 2)
    screen.blit(text_surface, text_rect)


def parse_board_state(board_state):
    lines = board_state.strip().split('\n')
    board = []
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:
            row = [char for char in cleaned_line if char in 'BWO']
            if len(row) == BOARD_SIZE:
                board.append(row)
    return board


def create_video(history):
    # List to store numpy arrays of frames
    frames_array = []

    for frame_num, state in enumerate(history):
        if "Black Wins" in state:
            draw_result('Black Wins!')
        elif "White Wins" in state:
            draw_result('White Wins!')
        else:
            draw_board()
            board = parse_board_state(state)

            # if not board:
            #     print(f"Warning: Empty board for frame {frame_num}")
            #     continue
            if board:
                for row, line in enumerate(board):
                    for col, piece in enumerate(line):
                        if piece == 'B':
                            draw_disc(row, col, LIGHT_BLACK)
                        elif piece == 'W':
                            draw_disc(row, col, LIGHT_WHITE)

        pygame.display.flip()

        # Convert the current screen to numpy array and store
        frame_array = pygame_surface_to_numpy(screen)
        frames_array.append(frame_array)
        if "Black Wins" in state or "White Wins" in state:
            for _ in range(2):
                frames_array.append(frame_array)
        clock.tick(FPS)

    print("Creating video from frames...")

    # Create make_frame function for MoviePy
    def make_frame(t):
        frame_idx = min(int(t * FPS), len(frames_array) - 1)
        return frames_array[frame_idx]

    # Calculate duration based on number of frames and FPS
    duration = len(frames_array) / FPS

    # Create and save the video
    clip = VideoClip(make_frame, duration=duration)
    clip.write_videofile("othello_game.mp4", fps=1)
    print("Video creation complete.")


def main():
    import re

    clean_history=[]
    board_line = ''
    line_count=0
    history = open(args.path)

    for line in history:
        if line.startswith('Cycle 0='):
            break

    for line in history:
        if line.startswith('O ') or line.startswith('B ') or line.startswith('W '):
            board_line += line + '\n'
            line_count += 1
        if line_count == 8:
            clean_history.append(board_line)
            board_line = ''
            line_count = 0
        if "Final result" in line:
            scores = re.findall("scores (\d+)", line)
            # print(scores)
            if scores[0]>scores[1]:
                clean_history.append("Black Wins")
            elif scores[0]<scores[1]:
                clean_history.append("White Wins")
            else:
                clean_history.append("Draw")
    print("Starting video creation...")
    create_video(clean_history)
    print("Video creation process completed.")
    pygame.quit()


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Parser for visualizer')
    # Add arguments
    parser.add_argument('path', type=str, help='Path to the input file', default='game.log')
    # Parse the arguments
    args = parser.parse_args()
    main()