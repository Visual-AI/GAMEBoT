from pettingzoo.classic import connect_four_v3
import time, os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)  # add path
from prompt_check_intermediate import *
import logging
from datetime import datetime
import random
import argparse
from agent_list import InitAgent
from utils.util import *
from check_and_random import *
import prompt_for_comparison

# common setup =========================
parser = argparse.ArgumentParser(description='Parser for test of agent')

# Add arguments
parser.add_argument('agent1_str', help='Path to the input file')
parser.add_argument('agent2_str', help='Path to the output file')
parser.add_argument('--cycles', type=int, help='Times of game cycles', default=1)
parser.add_argument('--key_start', type=int, help='Times of game cycles', default=0)
parser.add_argument('--prompt_type_agent1', type=str, help='Type of prompt, no|naive|cot', default='cot')
parser.add_argument('--prompt_type_agent2', type=str, help='Type of prompt, no|naive|cot', default='cot')

# Parse the arguments
args = parser.parse_args()
current_time = datetime.now()
date_string = current_time.strftime("%m-%d-%H-%M")

print(date_string)

game_str = "connect4"
cycles = args.cycles
agent1_scores = 0
agent2_scores = 0
init_agent = InitAgent(key_start=args.key_start)
agent1 = init_agent.init_agent(args.agent1_str)
agent2 = init_agent.init_agent(args.agent2_str)

if args.agent1_str != 'random':
    agent1_str = args.agent1_str+'_'+args.prompt_type_agent1
else:
    agent1_str = 'random'
if args.agent2_str != 'random':
    agent2_str = args.agent2_str+'_'+args.prompt_type_agent2
else:
    agent2_str = 'random'

run_category = 'running_log/{}/{}_vs_{}_'.format(game_str, agent1_str,agent2_str) + date_string

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

rgb_list = []

count_for_request = 0
start_time = time.time()

if args.prompt_type_agent1 == 'no':
    prompt1 = prompt_for_comparison.system_prompt_connect4_non_reason
elif args.prompt_type_agent1 == 'naive':
    prompt1 = prompt_for_comparison.system_prompt_connect4_simple_cot
else:
    prompt1 = system_prompt_connect4

if args.prompt_type_agent2 == 'no':
    prompt2 = prompt_for_comparison.system_prompt_connect4_non_reason
elif args.prompt_type_agent2 == 'naive':
    prompt2 = prompt_for_comparison.system_prompt_connect4_simple_cot
else:
    prompt2 = system_prompt_connect4
logger_game.info('Prompt1:\n {}'.format(prompt1))


# common setup end =========================

# Connect4 component =========================
def get_board_status(observation, player_type, with_position=False):
    opposite_mark = "X" if player_type == "O" else "O"
    marks_matrix = [["_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_"],
                    ["_", "_", "_", "_", "_", "_", "_"], ["_", "_", "_", "_", "_", "_", "_"]]
    for i, rows in enumerate(observation['observation']):
        for j, cols in enumerate(rows):
            if cols[0] == 1:
                marks_matrix[i][j] = player_type
            if cols[1] == 1:
                marks_matrix[i][j] = opposite_mark

    if with_position:
        board_status = ""
        for i, marks in enumerate(marks_matrix):
            for j, mark in enumerate(marks):
                board_status = board_status + f"({5 - i},{j}):{mark} "
            board_status = board_status + "\n"
    else:
        board_status = "\n  0   1   2   3   4   5   6   \n"

        for mark in marks_matrix:
            for m in mark:
                board_status = board_status + f"| {m} "
            board_status = board_status + "|\n"
    return board_status, marks_matrix


for cycle in range(cycles):
    logger_game.info('Cycle {}===================='.format(cycle))

    env = connect_four_v3.env(render_mode="rgb_array")
    env.reset(seed=random.randint(0, 9999))

    step = 0
    for agent in env.agent_iter():
        step += 1
        observation, reward, termination, truncation, info = env.last()

        if agent == 'player_0':
            player_type = 'X'
        else:
            player_type = 'O'
        board_status, status_matrix = get_board_status(observation, player_type)
        board_status_with_position, _ = get_board_status(observation, player_type, with_position=True)
        logger_game.info('Step {}------------'.format(step))
        logger_game.info('{}'.format(board_status))
        print(board_status)
        print(board_status_with_position)
        if termination or truncation:
            action = None
        else:
            state_prompt = f'\nCurrent Game Board: \n{board_status_with_position}'

            action_mask = observation["action_mask"]
            indices_of_ones = [i for i, value in enumerate(action_mask) if value == 1]
            # get available coordinates from status_matrix
            available_coordinates = []
            for column in indices_of_ones:
                for row in range(6):
                    reverse_row = 5 - row
                    if status_matrix[reverse_row][column] == "_":
                        available_coordinates.append(f'({row},{column})')
                        break
            state_prompt += f'\nCurrent valid moves for player {player_type}: {available_coordinates}\n'
            state_prompt += f'You are player {player_type}, please choose the best move considering the current board state.\n'
            count_for_request += 1
            if player_type == "X":
                if agent1_str == "random":
                    logger1.info(f'step {step}-------------------')
                    intermediate_results, action = random_connect4(indices_of_ones)
                    logger_game.info(f'{agent1_str} takes move {action}')
                else:
                    logger1.info(f'step {step}-------------------')
                    action_coordinate = call_llm_api_connect4(state_prompt, prompt1, logger1, agent1)
                    if len(action_coordinate) > 1:
                        action = action_coordinate[1]
                        logger_game.info(f'{agent1_str} takes move {action}')

                    elif len(action_coordinate) == 0:
                        action = None
                    else:
                        print(action_coordinate)
                        if 0 <= action_coordinate[0] <= 6:
                            action = action_coordinate[0]
                            logger_game.info(f'{agent1_str} takes move {action}')
                        else:
                            action = None

            else:
                if agent2_str == "random":
                    logger2.info(f'step {step}-------------------')
                    intermediate_results, action = random_connect4(indices_of_ones)
                    logger_game.info(f'{agent2_str} takes move {action}')
                else:
                    logger2.info(f'step {step}-------------------')
                    action = call_llm_api_connect4(state_prompt, prompt2, logger2, agent2)[1]
                    logger_game.info(f'{agent2_str} takes move {action}')
            # print(env.render())
        if reward == -1:
            if agent == 'player_0':
                agent2_scores += 1
                logger_game.info(f'{agent2_str} wins!!!!!!!!!!')
            else:
                agent1_scores += 1
                logger_game.info(f'{agent1_str} wins!!!!!!!!!!')
        env.step(action)
    env.close()

logger_game.info(f'Final scores: {agent1_str} {agent1_scores} - {agent2_str} {agent2_scores}')
logger_game.info(f'Total time: {time.time() - start_time}')
logger_game.info(f'Total requests per agents: {count_for_request}')
