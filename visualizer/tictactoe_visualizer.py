import pygame
import pygame.freetype
from moviepy.editor import ImageSequenceClip
import os

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
BOARD_SIZE = 3
CELL_SIZE = WIDTH // BOARD_SIZE
FPS = 1  # Frames per second for the video

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Font
font = pygame.freetype.SysFont(None, 120)
result_font = pygame.freetype.SysFont(None, 60)


def draw_board():
    screen.fill(WHITE)
    for row,col in [(0,1),(1,0),(1,2),(2,1)]:
        pygame.draw.rect(screen, GRAY, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # for i in range(1, BOARD_SIZE):
    #     pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 2)
    #     pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 2)


def draw_piece(row, col, piece):
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = row * CELL_SIZE + CELL_SIZE // 2

    if piece == 'X':
        font.render_to(screen, (x - 40, y - 60), 'X', BLACK)
    elif piece == 'O':
        font.render_to(screen, (x - 40, y - 60), 'O', BLACK)
    # elif piece == '_':
    #     pygame.draw.rect(screen, GRAY, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_result(result):
    text_surface, text_rect = result_font.render(result, RED)
    text_rect.center = (WIDTH // 2, HEIGHT//3)
    # screen.fill(WHITE)
    screen.blit(text_surface, text_rect)


def create_video(history):
    frames = []

    for frame_num, board_state in enumerate(history):
        if "tie" in board_state:
            draw_result("It's a tie!")
        elif "win" in board_state:
            draw_result(board_state.strip())
        else:
            draw_board()

            for row, line in enumerate(board_state.split('\n')):
                for col, piece in enumerate(line.split()):
                    draw_piece(row, col, piece)


        pygame.display.flip()
        frame_name = f"frame_{frame_num:03d}.png"
        pygame.image.save(screen, frame_name)
        frames.append(frame_name)

        clock.tick(FPS)

    # Create video from frames
    clip = ImageSequenceClip(frames, fps=FPS)
    clip.write_videofile("tictactoe_game.mp4", fps=FPS)

    # Clean up temporary frame files
    for frame in frames:
        os.remove(frame)


# Example usage
from utils.generate_history_str import clean_history

create_video(clean_history)
pygame.quit()