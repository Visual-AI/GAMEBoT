import pygame
import pygame.freetype
from moviepy.editor import VideoClip
import numpy as np
import re

# Initialize Pygame
pygame.init()

# Constants - Increased sizes for better visibility
WIDTH, HEIGHT = 1500, 1100
FPS = 0.5  # Frames per second for the video
CARD_WIDTH = 140  # Increased from 100
CARD_HEIGHT = 196  # Increased from 140

# Colors
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (218, 165, 32)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLACK = (30, 51, 50)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Fonts - Increased sizes
font = pygame.freetype.SysFont(None, 48)  # Increased from 36
action_font = pygame.freetype.SysFont(None, 60)  # Increased from 48
round_font = pygame.freetype.SysFont(None, 56)  # Increased from 45
result_font = pygame.freetype.SysFont(None, 84)  # Increased from 72


def draw_suit(surface, suit, x, y, size):
    """Draw poker suit symbols - increased size."""
    size = int(size * 1.4)  # Increase suit size by 40%
    if suit == "Hearts" or suit == "H":
        points = [
            (x, y - size // 4),
            (x - size // 2, y - size // 2),
            (x - size // 2, y),
            (x, y + size // 2),
            (x + size // 2, y),
            (x + size // 2, y - size // 2),
        ]
        pygame.draw.polygon(surface, RED, points)
        pygame.draw.circle(surface, RED, (x - size // 4, y - size // 4), size // 4)
        pygame.draw.circle(surface, RED, (x + size // 4, y - size // 4), size // 4)
    elif suit == "Diamonds" or suit == "D":
        points = [(x, y - size // 2), (x - size // 2, y), (x, y + size // 2), (x + size // 2, y)]
        pygame.draw.polygon(surface, RED, points)
    elif suit == "Clubs" or suit == "C":
        pygame.draw.circle(surface, BLACK, (x - size // 4, y - size // 4), size // 4)
        pygame.draw.circle(surface, BLACK, (x + size // 4, y - size // 4), size // 4)
        pygame.draw.circle(surface, BLACK, (x, y + size // 4), size // 4)
        points = [(x, y), (x - size // 4, y + size // 2), (x + size // 4, y + size // 2)]
        pygame.draw.polygon(surface, BLACK, points)
    elif suit == "Spades" or suit == "S":
        points = [
            (x, y - size // 2),
            (x - size // 2, y),
            (x - size // 4, y),
            (x, y + size // 4),
            (x + size // 4, y),
            (x + size // 2, y),
        ]
        pygame.draw.polygon(surface, BLACK, points)
        points = [(x, y), (x - size // 4, y + size // 2), (x + size // 4, y + size // 2)]
        pygame.draw.polygon(surface, BLACK, points)


def draw_card(x, y, card_str, hidden=False):
    """Draw a playing card - adjusted for larger size."""
    pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT))
    pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 3)  # Increased border thickness

    if hidden:
        pygame.draw.rect(screen, RED, (x + 7, y + 7, CARD_WIDTH - 14, CARD_HEIGHT - 14))
        for i in range(0, CARD_WIDTH - 28, 14):
            pygame.draw.line(screen, GOLD, (x + 14 + i, y + 14), (x + 14 + i, y + CARD_HEIGHT - 14), 3)
    elif card_str:
        parts = card_str.strip().split()
        if len(parts) == 2:
            suit, value = parts
        else:
            value = card_str[:-1]
            suit = card_str[-1]

        suit_color_map = {'H': 'Hearts', 'D': 'Diamonds', 'C': 'Clubs', 'S': 'Spades'}
        full_suit = suit_color_map.get(suit, suit)
        color = RED if full_suit in ["Hearts", "Diamonds"] else BLACK

        font.render_to(screen, (x + 14, y + 14), value, color)
        draw_suit(screen, suit, x + CARD_WIDTH // 2, y + CARD_HEIGHT // 2, 42)  # Increased suit size
        draw_suit(screen, suit, x + 28, y + 70, 21)  # Adjusted small suit position and size


def draw_poker_table():
    """Draw the poker table and felt - made slightly smaller to focus on playing area."""
    pygame.draw.ellipse(screen, GREEN, (WIDTH // 10, HEIGHT // 5, 4 * WIDTH // 5, 3 * HEIGHT // 5))
    pygame.draw.ellipse(screen, GOLD, (WIDTH // 10, HEIGHT // 5, 4 * WIDTH // 5, 3 * HEIGHT // 5), 7)


def draw_chips(x, y, amount):
    """Draw stack of poker chips - increased size."""
    chip_colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0)]
    chip_radius = 21  # Increased from 15
    stack_offset = 7  # Increased from 5
    num_chips = min(int(amount / 10), 5)

    for i in range(num_chips):
        color = chip_colors[i % len(chip_colors)]
        pygame.draw.circle(screen, color, (x, y - i * stack_offset), chip_radius)
        pygame.draw.circle(screen, WHITE, (x, y - i * stack_offset), chip_radius, 3)

    font.render_to(screen, (x + chip_radius, y - chip_radius), f"POT: {amount}", WHITE)


def draw_player_info(name, chips, bet, x, y, action="", is_current_player=False):
    """Draw player information - adjusted positions and spacing."""
    if is_current_player:
        pygame.draw.rect(screen, GOLD, (x - 7, y - 7, 280, 140), 3)

    font.render_to(screen, (x, y), f"{name}", WHITE)
    chips = 100 - bet
    font.render_to(screen, (x, y + 42), f"Chips: {chips}", WHITE)
    font.render_to(screen, (x, y + 84), f"Bet: {bet}", WHITE)

    if action:
        action_font.render_to(screen, (x, y + 126), f"{action}", GOLD)


# Rest of the code remains the same, including parse_game_state and create_video functions
def parse_game_state(state, last_known_state):
    """Parse the game state string and extract relevant information."""
    game_info = {
        'gpt4_cards': last_known_state['gpt4_cards'],
        'claude_cards': last_known_state['claude_cards'],
        'community_cards': last_known_state['community_cards'],
        'gpt4_chips': last_known_state['gpt4_chips'],
        'claude_chips': last_known_state['claude_chips'],
        'gpt4_bet': last_known_state['gpt4_bet'],
        'claude_bet': last_known_state['claude_bet'],
        'current_player': '',
        'last_action': '',
        'round': ''
    }

    round_match = re.search(r"Current round is ([^\n]*)", state)
    if round_match:
        game_info['round'] = round_match.group(1)

    current_cards_match = re.search(r"cards in your hands is \[(.*?)\]", state)
    turn_match = re.search(r"([\w@-]+)'s turn", state)

    if turn_match and current_cards_match:
        current_player = turn_match.group(1)
        game_info['current_player'] = current_player
        cards = [c.strip() for c in current_cards_match.group(1).split(',')]

        if current_player == "gpt-4-1106":
            game_info['gpt4_cards'] = cards
        else:
            game_info['claude_cards'] = cards

    community_match = re.search(r"community cards is \[(.*?)\]", state)
    if community_match:
        cards = [c.strip() for c in community_match.group(1).split(',')]
        game_info['community_cards'] = cards

    chips_pattern = r"You now have ([\d.]+) chips"
    your_bet_pattern = r"You has put in the pot ([\d.]+) chips"
    opponent_bet_pattern = r"Your opponent has put in the pot ([\d.]+) chips"

    chips_match = re.search(chips_pattern, state)
    your_bet_match = re.search(your_bet_pattern, state)
    opponent_bet_match = re.search(opponent_bet_pattern, state)

    if chips_match and your_bet_match and opponent_bet_match:
        chips = float(chips_match.group(1))
        your_bet = float(your_bet_match.group(1))
        opponent_bet = float(opponent_bet_match.group(1))

        if game_info['current_player'] == "gpt-4-1106":
            game_info['gpt4_chips'] = chips
            game_info['gpt4_bet'] = your_bet
            game_info['claude_bet'] = opponent_bet
        else:
            game_info['claude_chips'] = chips
            game_info['claude_bet'] = your_bet
            game_info['gpt4_bet'] = opponent_bet

    action_match = re.search(
        r"(?:gpt-4-1106|claude-3-sonnet@20240229) ((?:Fold|Check and Call|Raise Half Pot|Raise Full Pot|All in))",
        state)
    if action_match:
        game_info['last_action'] = action_match.group(1)

    return game_info


def create_video(history):
    """Create a video from the game history."""
    frames_array = []
    last_known_state = {
        'gpt4_cards': [],
        'claude_cards': [],
        'community_cards': [],
        'gpt4_chips': 100,
        'claude_chips': 100,
        'gpt4_bet': 0,
        'claude_bet': 0
    }

    states = [s.strip() for s in history.split('\n\n') if "turn" in s and "Current round" in s]

    for state in states:
        game_info = parse_game_state(state, last_known_state)
        last_known_state = game_info.copy()

        screen.fill(LIGHT_BLACK)
        draw_poker_table()

        # Draw community cards in the center - adjusted spacing
        for i, card in enumerate(game_info['community_cards']):
            draw_card(WIDTH // 2 - 350 + i * 154, HEIGHT // 2 - 98, card)

        # Draw GPT-4's cards at the bottom - adjusted spacing
        for i, card in enumerate(game_info['gpt4_cards']):
            draw_card(WIDTH // 2 - 154 + i * 154, HEIGHT - 280, card)

        # Draw Claude's cards at the top - adjusted spacing
        for i, card in enumerate(game_info['claude_cards']):
            draw_card(WIDTH // 2 - 154 + i * 154, 180, card)

        # Draw player information with adjusted positions
        draw_player_info("GPT-4", game_info['gpt4_chips'], game_info['gpt4_bet'],
                         WIDTH // 4 - 140, HEIGHT - 300,
                         game_info['last_action'] if game_info['current_player'] == "gpt-4-1106" else "",
                         game_info['current_player'] == "gpt-4-1106")

        draw_player_info("Claude", game_info['claude_chips'], game_info['claude_bet'],
                         3 * WIDTH // 4 - 80, 60,
                         game_info['last_action'] if game_info['current_player'] == "claude-3-sonnet@20240229" else "",
                         game_info['current_player'] == "claude-3-sonnet@20240229")

        # Draw pot
        total_pot = game_info['gpt4_bet'] + game_info['claude_bet']
        draw_chips(WIDTH // 2 - 100, HEIGHT // 2 - 140, total_pot)

        # Draw round information
        round_font.render_to(screen, (WIDTH // 2 - 170, 50), f"Round: {game_info['round']}", RED)

        cycle_results1 = re.search(r"Cycle \d+ results: gpt-4-1106 ([-\d.]+):claude-3-sonnet@20240229 ([-\d.]+)", state)
        cycle_results2 = re.search(r"Cycle \d+ results: claude-3-sonnet@20240229 ([-\d.]+):gpt-4-1106 ([-\d.]+)", state)

        pygame.display.flip()

        frame_array = pygame.surfarray.array3d(screen)
        frame_array = np.transpose(frame_array, (1, 0, 2))
        frames_array.append(frame_array)

        if cycle_results1:
            result_font.render_to(screen, (WIDTH // 7, HEIGHT // 2),
                                  f"Scores: GPT-4 {cycle_results1.group(1)}, Claude {cycle_results1.group(2)}", RED)
        if cycle_results2:
            result_font.render_to(screen, (WIDTH // 7, HEIGHT // 2),
                                  f"Scores: Claude {cycle_results2.group(1)}, GPT-4 {cycle_results2.group(2)}", RED)
        if cycle_results1 or cycle_results2:
            pygame.display.flip()
            frame_array = pygame.surfarray.array3d(screen)
            frame_array = np.transpose(frame_array, (1, 0, 2))
            frames_array.append(frame_array)
        clock.tick(FPS)

    def make_frame(t):
        frame_idx = min(int(t * FPS), len(frames_array) - 1)
        return frames_array[frame_idx]

    # Create and save video
    duration = len(frames_array) / FPS
    clip = VideoClip(make_frame, duration=duration)
    clip.write_videofile("poker_game.mp4", fps=FPS)
    print("Video creation complete.")


# Example usage

def main():
    history = open(args.path)

    for line in history:
        if line.startswith('Cycle 0='):
            break
    clean_history = ''
    for line in history:
        clean_history += line
    # print(clean_history)
    print("Starting video creation...")
    create_video(clean_history)
    print("Video creation process completed.")
    pygame.quit()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Parser for visualizer')
    parser.add_argument('path', type=str, help='Path to the input file', default='game.log')
    parser.add_argument('--output', default='texas_game.mp4')
    args = parser.parse_args()
    main()

