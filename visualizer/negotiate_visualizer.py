import pygame
import pygame.gfxdraw
import cv2
import numpy as np
import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GameState:
    cycle: int
    pool: List[int]
    p1_values: List[int]
    p2_values: List[int]
    rounds: List[dict]
    agreement: bool
    rewards: dict


def parse_game_history(history_text: str) -> List[GameState]:
    game_states = []

    # Split into individual cycles
    cycles = re.split(r'Cycle \d+====================', history_text)[1:]  # Skip empty first split
    cycle_numbers = re.findall(r'Cycle (\d+)====================', history_text)

    for cycle_num, cycle_text in zip(cycle_numbers, cycles):
        # Parse initial state
        pool = [int(x) for x in re.findall(r'Pool:\s*\[([\d,\s]+)\]', cycle_text)[0].split(',')]
        p1_values = [int(x) for x in re.findall(r'P1 values: \[([\d,\s]+)\]', cycle_text)[0].split(',')]
        p2_values = [int(x) for x in re.findall(r'P2 values: \[([\d,\s]+)\]', cycle_text)[0].split(',')]

        # Parse rounds
        rounds = []
        round_matches = re.finditer(r'Round \d+ Player(\d) proposes: P1 \[([\d,\s]+)\], P2 \[([\d,\s]+)\]', cycle_text)

        for match in round_matches:
            player = int(match.group(1))
            p1_proposal = [int(x) for x in match.group(2).split(',')]
            p2_proposal = [int(x) for x in match.group(3).split(',')]
            rounds.append({
                'player': player,
                'p1': p1_proposal,
                'p2': p2_proposal
            })

        # Parse outcome
        agreement = 'Agreement reached' in cycle_text
        if agreement:
            rewards_match = re.search(r'Rewards: P1 (\d+), P2 (\d+)', cycle_text)
            rewards = {'p1': int(rewards_match.group(1)), 'p2': int(rewards_match.group(2))}
        else:
            rewards = {'p1': 0, 'p2': 0}

        game_states.append(GameState(
            cycle=int(cycle_num),
            pool=pool,
            p1_values=p1_values,
            p2_values=p2_values,
            rounds=rounds,
            agreement=agreement,
            rewards=rewards
        ))

    return game_states


class NegotiateVisualizer:
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.Surface((width, height))
        self.fps = 30
        self.frames_per_round = 90  # 3 seconds per round at 30 fps

        # Colors
        self.bg_color = (240, 240, 240)
        self.text_color = (30, 30, 30)
        self.item_colors = [
            (66, 135, 245),  # Blue
            (52, 199, 89),  # Green
            (175, 82, 222)  # Purple
        ]

        # Fonts
        pygame.font.init()
        self.title_font = pygame.font.Font(None, 48)
        self.main_font = pygame.font.Font(None, 36)
        self.value_font = pygame.font.Font(None, 32)

    def draw_item(self, pos: Tuple[int, int], item_type: int, count: int, value: int = None):
        x, y = pos
        radius = 30

        # Draw the shape based on item_type
        color = self.item_colors[item_type]
        if item_type == 0:  # Circle
            pygame.gfxdraw.aacircle(self.screen, x, y, radius, color)
            pygame.gfxdraw.filled_circle(self.screen, x, y, radius, color)
        elif item_type == 1:  # Square
            rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            pygame.draw.rect(self.screen, color, rect)
        else:  # Triangle
            points = [
                (x, y - radius),
                (x - radius, y + radius),
                (x + radius, y + radius)
            ]
            pygame.gfxdraw.aapolygon(self.screen, points, color)
            pygame.gfxdraw.filled_polygon(self.screen, points, color)

        # Draw count
        count_text = self.main_font.render(str(count), True, (255, 255, 255))
        count_rect = count_text.get_rect(center=(x, y))
        self.screen.blit(count_text, count_rect)

        # Draw value if provided
        if value is not None:
            value_text = self.value_font.render(f"Value: {value}", True, self.text_color)
            value_rect = value_text.get_rect(center=(x, y + radius + 20))
            self.screen.blit(value_text, value_rect)

    def draw_frame(self, game_state: GameState, current_round: int):
        # Clear screen
        self.screen.fill(self.bg_color)

        # Draw title
        title = f"Negotiate Game - Cycle {game_state.cycle} - Round {current_round + 1}"
        title_text = self.title_font.render(title, True, self.text_color)
        self.screen.blit(title_text, (20, 20))

        # Draw pool items
        pool_title = self.main_font.render("Pool", True, self.text_color)
        self.screen.blit(pool_title, (20, 100))
        for i, (count, value1, value2) in enumerate(zip(game_state.pool,
                                                        game_state.p1_values,
                                                        game_state.p2_values)):
            self.draw_item((150 + i * 200, 150), i, count)
            # Draw values below
            p1_value = self.value_font.render(f"P1: {value1}", True, self.text_color)
            p2_value = self.value_font.render(f"P2: {value2}", True, self.text_color)
            self.screen.blit(p1_value, (120 + i * 200, 200))
            self.screen.blit(p2_value, (120 + i * 200, 230))

        # Draw current proposals
        if current_round < len(game_state.rounds):
            round_data = game_state.rounds[current_round]

            # Player 1's proposal
            p1_title = self.main_font.render("Player 1's Proposal", True, self.text_color)
            self.screen.blit(p1_title, (20, 350))
            for i, count in enumerate(round_data['p1']):
                self.draw_item((150 + i * 200, 400), i, count)

            # Player 2's share
            p2_title = self.main_font.render("Player 2's Share", True, self.text_color)
            self.screen.blit(p2_title, (20, 500))
            for i, count in enumerate(round_data['p2']):
                self.draw_item((150 + i * 200, 550), i, count)

            # Draw whose turn it is
            turn_text = self.main_font.render(f"Player {round_data['player']}'s turn",
                                              True, self.text_color)
            self.screen.blit(turn_text, (self.width - 250, 50))

        # Draw final results if last round
        if current_round == len(game_state.rounds) - 1:
            if game_state.agreement:
                result = f"Agreement reached! P1: {game_state.rewards['p1']}, P2: {game_state.rewards['p2']}"
            else:
                result = "No agreement reached (0 points each)"
            result_text = self.main_font.render(result, True, self.text_color)
            self.screen.blit(result_text, (self.width // 2 - result_text.get_width() // 2,
                                           self.height - 50))

    def generate_video(self, game_states: List[GameState], output_path: str):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps,
                              (self.width, self.height))

        for game_state in game_states:
            for round_idx in range(len(game_state.rounds)):
                for frame in range(self.frames_per_round):
                    self.draw_frame(game_state, round_idx)

                    # Convert Pygame surface to OpenCV format
                    pygame_surface = pygame.surfarray.array3d(self.screen)
                    cv2_frame = cv2.transpose(pygame_surface)
                    cv2_frame = cv2.cvtColor(cv2_frame, cv2.COLOR_RGB2BGR)

                    out.write(cv2_frame)

        out.release()
        pygame.quit()


def main():
    # Example game history text
    game_history = """
Cycle 0====================
Pool:    [4, 1, 5]
P1 values: [4, 9, 1]
P2 values: [2, 7, 3]
Negotiation begins
Round 1 Player1 proposes: P1 [2, 1, 2], P2 [2, 0, 3]
Round 2 Player2 proposes: P1 [1, 1, 3], P2 [3, 0, 2]
Round 3 Player1 proposes: P1 [2, 1, 3], P2 [2, 0, 2]
Round 4 Player2 proposes: P1 [1, 0, 3], P2 [3, 1, 2]
Round 5 Player1 proposes: P1 [2, 0, 4], P2 [2, 1, 1]
Round 6 Player2 proposes: P1 [1, 0, 4], P2 [3, 1, 1]
Round 7 Player1 proposes: P1 [1, 1, 4], P2 [3, 0, 1]
Agreement reached
Rewards: P1 17, P2 9

Cycle 1====================
Pool:    [6, 1, 3]
P1 values: [1, 21, 1]
P2 values: [4, 6, 0]
Negotiation begins
Round 1 Player1 proposes: P1 [4, 1, 1], P2 [2, 0, 2]
Round 2 Player2 proposes: P1 [3, 0, 2], P2 [3, 1, 1]
Round 3 Player1 proposes: P1 [2, 1, 2], P2 [4, 0, 1]
Round 4 Player2 proposes: P1 [3, 0, 1], P2 [3, 1, 2]
Round 5 Player1 proposes: P1 [2, 1, 2], P2 [4, 0, 1]
Round 6 Player2 proposes: P1 [1, 1, 3], P2 [5, 0, 0]
Round 7 Player1 proposes: P1 [2, 1, 2], P2 [4, 0, 1]
Round 8 Player2 proposes: P1 [3, 0, 2], P2 [3, 1, 1]
Round 9 Player1 proposes: P1 [2, 1, 3], P2 [4, 0, 0]
Agreement reached
Rewards: P1 26, P2 16

Cycle 2====================
Pool:    [1, 3, 4]
P1 values: [3, 1, 6]
P2 values: [17, 3, 1]
Bargaining begins
Round 1 Player1 proposes: P1 [0, 1, 3], P2 [1, 2, 1]
Round 2 Player2 proposes: P1 [0, 2, 1], P2 [1, 1, 3]
Round 3 Player1 proposes: P1 [0, 1, 3], P2 [1, 2, 1]
Round 4 Player2 proposes: P1 [0, 2, 2], P2 [1, 1, 2]
Round 5 Player1 proposes: P1 [0, 1, 3], P2 [1, 2, 1]
Round 6 Player2 proposes: P1 [0, 2, 2], P2 [1, 1, 2]
Round 7 Player1 proposes: P1 [0, 1, 3], P2 [1, 2, 1]
Round 8 Player2 proposes: P1 [0, 2, 2], P2 [1, 1, 2]
Round 9 Player1 proposes: P1 [0, 1, 3], P2 [1, 2, 1]
Round 10 Player2 proposes: P1 [0, 2, 2], P2 [1, 1, 2]
Round 11 Player1 proposes: P1 [0, 1, 3], P2 [1, 2, 1]
Agreement reached
Rewards: P1 19, P2 24

Cycle 3====================
Pool:    [2, 4, 5]
P1 values: [3, 6, 0]
P2 values: [6, 2, 2]
Negotiation begins
Round 1 Player1 proposes: P1 [1, 4, 0], P2 [1, 0, 5]
Round 2 Player2 proposes: P1 [1, 3, 1], P2 [1, 1, 4]
Round 3 Player1 proposes: P1 [2, 3, 0], P2 [0, 1, 5]
Round 4 Player2 proposes: P1 [0, 2, 2], P2 [2, 2, 3]
Round 5 Player1 proposes: P1 [1, 3, 2], P2 [1, 1, 3]
Round 6 Player2 proposes: P1 [0, 3, 2], P2 [2, 1, 3]
Round 7 Player1 proposes: P1 [0, 4, 1], P2 [2, 0, 4]
Agreement reached
Rewards: P1 24, P2 20

Cycle 4====================
Pool:    [3, 2, 5]
P1 values: [4, 4, 2]
P2 values: [3, 8, 1]
Negotiation begins
Round 1 Player1 proposes: P1 [3, 1, 2], P2 [0, 1, 3]
Round 2 Player2 proposes: P1 [2, 0, 3], P2 [1, 2, 2]
Round 3 Player1 proposes: P1 [2, 1, 3], P2 [1, 1, 2]
Round 4 Player2 proposes: P1 [2, 0, 4], P2 [1, 2, 1]
Round 5 Player1 proposes: P1 [2, 0, 4], P2 [1, 2, 1]
Round 6 Player2 proposes: P1 [1, 1, 3], P2 [2, 1, 2]
Round 7 Player1 proposes: P1 [2, 1, 3], P2 [1, 1, 2]
Round 8 Player2 proposes: P1 [1, 0, 4], P2 [2, 2, 1]
Round 9 Player1 proposes: P1 [2, 0, 4], P2 [1, 2, 1]
Game ended without agreement, each with 0 point

"""
    # Parse game history
    game_states = parse_game_history(game_history)

    # Generate video
    visualizer = NegotiateVisualizer()
    visualizer.generate_video(game_states, "negotiate_game.mp4")


# Example usage
if __name__ == "__main__":
    main()
