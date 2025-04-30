import re, os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)  # add path
from prompt_check_intermediate import system_prompt_tictactoe
from agent_list import InitAgent
from datetime import datetime
import argparse
import logging
import random

parser = argparse.ArgumentParser(description='Parser for test of agent')

# Add arguments
parser.add_argument('agent1_str')
parser.add_argument('agent2_str')
parser.add_argument('--cycles', type=int, help='Times of game cycles', default=1)
parser.add_argument('--test_type', help='Type of test', default='normal')
parser.add_argument('--key_start', type=int, default=0)
parser.add_argument('--prompt_type_agent1', type=str, help='Type of prompt, no|naive|cot', default='cot')
parser.add_argument('--prompt_type_agent2', type=str, help='Type of prompt, no|naive|cot', default='cot')

# Parse the arguments
args = parser.parse_args()
# if args.test_type == 'normal':
#     system_prompt = system_prompt_tictactoe
# else:
#     system_prompt = system_prompt_tictactoe_llmarena

prompt1 = system_prompt_tictactoe
prompt2 = system_prompt_tictactoe
current_time = datetime.now()
date_string = current_time.strftime("%m-%d-%H-%M")

print(date_string)

init_agent = InitAgent(key_start=args.key_start)
if args.agent1_str not in ['random','algorithm','human']:
    agent1 = init_agent.init_agent(args.agent1_str)
if args.agent2_str not in ['random','algorithm','human']:
    agent2 = init_agent.init_agent(args.agent2_str)

if args.agent1_str not in ['random','algorithm','human']:
    agent1_str = args.agent1_str+'_'+args.prompt_type_agent1
else:
    agent1_str = args.agent1_str
if args.agent2_str not in ['random','algorithm','human']:
    agent2_str = args.agent2_str+'_'+args.prompt_type_agent2
else:
    agent2_str = args.agent2_str

# generate random string with 2 characters.
random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=2))

run_category = 'running_log/tictactoe/{}_vs_{}_'.format(agent1_str,agent2_str) + date_string + random_string

if not os.path.exists(run_category):
    # Create the directory
    # os.mkdir(run_category)
    os.makedirs(run_category, exist_ok=True)
    print("Directory created:", run_category)
else:
    print("Directory", run_category, "already exists")

print('#INFO: The log category is', run_category)
# Configure logging
logger1 = logging.getLogger('logger1')
logger2 = logging.getLogger('logger2')
logger_game = logging.getLogger('game')
logger1.setLevel(logging.INFO)
logger2.setLevel(logging.INFO)
logger_game.setLevel(logging.INFO)
file_handler1 = logging.FileHandler('{}/{}.log'.format(run_category, agent1_str))
file_handler2 = logging.FileHandler('{}/{}.log'.format(run_category, agent2_str))
file_handler_game = logging.FileHandler('{}/game.log'.format(run_category))
logger1.addHandler(file_handler1)
logger2.addHandler(file_handler2)
logger_game.addHandler(file_handler_game)
logger_game.info('Prompt1:\n {}'.format(prompt1))


def find_action(response):
    response_split = response.split('Chosen Move')
    if len(response_split) == 1:
        print('#### No action find!!!')
        print(response)
    action_text = response_split[-1].strip()
    pattern = r"\((\d),\s*(\d)\)\s*"

    match = re.search(pattern, action_text)

    if match:
        coordinates = [int(group) for group in match.groups() if group is not None]
        logger_game.info(coordinates)
    else:
        print("Invalid move input format.")
        print(response)
        coordinates = []
    return coordinates


agent1_scores = 0
agent2_scores = 0
total_requests_per_agent = 0


class TicTacToe:
    def __init__(self):
        self.board = [["_" for _ in range(3)] for _ in range(3)]
        self.current_player = "X"

    def print_board(self, with_indices=False):
        """Prints the current state of the Tic-Tac-Toe board."""
        board_str = ""
        for i, row in enumerate(self.board):
            #             board_str+="|"
            for j, cell in enumerate(row):
                if with_indices:
                    board_str += f"({i},{j}):{cell} "
                else:
                    board_str += f"{cell} "
            board_str += "\n"
        #         print("---------")
        return board_str

    def get_valid_moves(self):
        valid_moves = []
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == "_":
                    valid_moves.append(f'({i},{j})')
        return valid_moves

    def get_random_move(self):
        """Gets a random move from the player."""
        valid_moves = []
        for i, row in enumerate(self.board):
            for j, cell in enumerate(row):
                if cell == "_":
                    valid_moves.append((i, j))
        return random.choice(valid_moves)

    def get_player_move(self):
        """Gets a valid move from the player."""
        while True:
            try:
                row, col = map(
                    int,
                    input(f"{self.current_player}, enter your move (row,col): ").split(
                        ","
                    ),
                )
                if 0 <= row <= 2 and 0 <= col <= 2 and self.board[row][col] == "_":
                    return row, col
                else:
                    print("Invalid move. Try again.")
            except (ValueError, IndexError):
                print(
                    "Invalid input. Please enter two numbers separated by a comma (e.g., 0,1)."
                )

    def get_llm_move(self, board_str, agent, agent_logger):
        i = 0
        while True:
            i += 1
            if i > 5:
                logger_game.info("Too many invalid moves. Game over.")
                break
            try:
                state_prompt = f"\nCurrent Game Board:\n{board_str}\nYou are playing pieces {self.current_player}, choose a best move from legal moves: {self.get_valid_moves()}\n"
                if self.current_player == "X":
                    prompt = prompt1 + state_prompt
                else:
                    prompt = prompt2 + state_prompt
                response = agent.get_response_text(prompt)
                agent_logger.info(state_prompt)
                agent_logger.info(response)
                agent_logger.info("---------------------------\n")
                logger_game.info("---------------------------\n")

                action_list = find_action(response)
                row, col = action_list[0], action_list[1]
                if 0 <= row <= 2 and 0 <= col <= 2 and self.board[row][col] == "_":
                    return row, col
                else:
                    print("Invalid move. Try again.")
            except (ValueError, IndexError):
                print(
                    "Invalid input. Please enter two numbers separated by a comma (e.g., 0,1)."
                )

    def get_algorithm_move(self):
        """Returns optimal move using the MiniMax algorithm."""
        best_score = float('-inf')
        best_move = None

        # Try all possible moves
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "_":
                    # Make the move
                    self.board[i][j] = self.current_player
                    # Get score from minimax
                    score = self.minimax(0, False)
                    # Undo the move
                    self.board[i][j] = "_"

                    # Update best move if necessary
                    if score > best_score:
                        best_score = score
                        best_move = (i, j)

        return best_move

    def minimax(self, depth, is_maximizing):
        """
        Implements the MiniMax algorithm.

        Args:
            depth (int): Current depth in the game tree
            is_maximizing (bool): True if it's maximizing player's turn

        Returns:
            int: The best score that can be achieved from the current position
        """
        # Get the opponent's symbol
        opponent = "O" if self.current_player == "X" else "X"

        # Check terminal states
        winner = self.check_win()
        if winner == self.current_player:
            return 10 - depth  # Prefer winning sooner
        elif winner == opponent:
            return depth - 10  # Prefer losing later
        elif self.is_board_full():
            return 0

        # Recursive case
        if is_maximizing:
            best_score = float('-inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "_":
                        self.board[i][j] = self.current_player
                        score = self.minimax(depth + 1, False)
                        self.board[i][j] = "_"
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "_":
                        self.board[i][j] = opponent
                        score = self.minimax(depth + 1, True)
                        self.board[i][j] = "_"
                        best_score = min(score, best_score)
            return best_score

    def check_win(self):
        """Checks if there's a winner on the board."""
        # Check rows
        for row in self.board:
            if row[0] == row[1] == row[2] and row[0] != "_":
                return row[0]

        # Check columns
        for col in range(3):
            if (
                    self.board[0][col] == self.board[1][col] == self.board[2][col]
                    and self.board[0][col] != "_"
            ):
                return self.board[0][col]

        # Check diagonals
        if (
                (
                        self.board[0][0] == self.board[1][1] == self.board[2][2]
                        or self.board[0][2] == self.board[1][1] == self.board[2][0]
                )
                and self.board[1][1] != "_"
        ):
            return self.board[1][1]

        return None

    def is_board_full(self):
        """Checks if the board is full."""
        for row in self.board:
            for cell in row:
                if cell == "_":
                    return False
        return True

    def play_game(self, with_indices=False):
        """Starts and manages the Tic-Tac-Toe game loop."""
        global total_requests_per_agent
        while True:
            total_requests_per_agent += 1
            # Display the board
            board_str = self.print_board()
            logger_game.info(board_str)

            board_str_indices = self.print_board(with_indices=True)
            # Get the player's move

            if self.current_player == "X":
                if agent1_str == "random":
                    row, col = self.get_random_move()
                elif agent1_str == "algorithm":
                    row, col = self.get_algorithm_move()
                elif agent1_str == "human":
                    row, col = self.get_player_move()
                else:
                    row, col = self.get_llm_move(board_str_indices, agent1, logger1)
            else:
                if agent2_str == "random":
                    row, col = self.get_random_move()
                elif agent2_str == "algorithm":
                    row, col = self.get_algorithm_move()
                elif agent2_str == "human":
                    row, col = self.get_player_move()
                else:
                    row, col = self.get_llm_move(board_str_indices, agent2, logger2)
            # Update the board
            if self.board[row][col] != "_":
                logger_game.info("Invalid move. Cell already taken.")
                break
            self.board[row][col] = self.current_player

            # Check for a winner
            winner = self.check_win()
            if winner:
                self.print_board()
                if winner == 'X':
                    logger_game.info(f"Congratulations! {agent1_str} wins! {winner} wins! ")
                    global agent1_scores
                    agent1_scores += 1
                else:
                    logger_game.info(f"Congratulations! {agent2_str} wins! {winner} wins! ")
                    global agent2_scores
                    agent2_scores += 1
                break

            # Check for a tie
            if self.is_board_full():
                self.print_board()
                logger_game.info("It's a tie!")
                return 0
                break

            # Switch to the other player
            self.current_player = "O" if self.current_player == "X" else "X"


game = TicTacToe()
for cycle in range(args.cycles):
    game.play_game()
    game = TicTacToe()
logger_game.info(f"{agent1_str} wins {agent1_scores} times.")
logger_game.info(f"{agent2_str} wins {agent2_scores} times.")
logger_game.info(f"Total requests per agent: {total_requests_per_agent}")
