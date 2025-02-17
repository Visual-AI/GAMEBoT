# from pettingzoo.atari import pong_v3
# from utils.ram_annotations import atari_dict

from collections import deque
import time, os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir) # add path
from prompt_check_intermediate import *
import logging
from datetime import datetime
import pdb
import argparse
from agent_list import InitAgent
from game_env.othello import Othello
import re


def async_call_llm_api(frame_input, logger, agent, agent_str, random_move):
    if agent_str == 'random':
        return random_move
    else:
        logger.info(frame_input)
        final_input1 = system_prompt_othello + frame_input
        response = ''
        while len(response) == 0:
            response = agent.get_response_text(final_input1)
            if response == '':
                time.sleep(1)
        # response = agent.get_response_text(frame_input)
        # print(response)
        pattern = r"\(([A-Z]),?\s*(\d+)\)|([A-Z])(\d+)"
        match = re.findall(pattern, response)
        # action = ()
        # pdb.set_trace()
        logger.info(response)
        # action = find_action(response)
        if len(match) == 0:
            return 'D', 4
        print(match[-1])
        if match[-1][0] == '':
            return match[-1][2], match[-1][3]
        return match[-1][0], match[-1][1]


def main():
    current_time = datetime.now()
    date_string = current_time.strftime("%m-%d-%H-%M")

    print(date_string)
    # agent1_str = 'gemini-1.5-pro-latest'
    # agent1_str = 'mixtral-8x7b-32768'
    # agent1_str = 'llama3-8b-8192'
    # agent2_str = 'gemini-1.0-pro'
    # agent1_str = 'llama3-70b-8192'
    # agent2_str = 'mixtral-8x7b-32768'
    # agent2_str = 'llama3-70b-8192'
    # agent2_str = 'mixtral-8x7b-32768'
    agent1_str = args.agent1_str
    agent2_str = args.agent2_str
    cycles = args.cycles
    agent1_scores = 0
    agent2_scores = 0
    init_agent = InitAgent(key_start=args.key_start)
    agent1 = init_agent.init_agent(agent1_str)
    agent2 = init_agent.init_agent(agent2_str)
    run_category = 'running_log/othello/{}_vs_{}_'.format(agent1_str, agent2_str) + date_string

    if not os.path.exists(run_category):
        # Create the directory
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
    logger_game.info(system_prompt_othello)
    # logging.basicConfig(filename='{}/logfile.log'.format(run_category), level=logging.INFO)

    # env.reset(seed=random.randint(0, 9999))
    rgb_list = []
    action2 = 0
    action1 = 0
    refined_info_queue = deque(maxlen=4)
    info_flipped_queue = deque(maxlen=4)
    count_for_request = 0
    start_time = time.time()
    step_skim = 4

    hint_penalty = [0, 0]
    force_penalty = [0, 0]

    for cycle in range(cycles):
        game = Othello()
        step = 0
        logger_game.info('Cycle {}===================='.format(cycle))
        logger1.info('Cycle {}===================='.format(cycle))
        logger2.info('Cycle {}===================='.format(cycle))
        agent1_no_valid_moves = False
        agent2_no_valid_moves = False
        while True:
            step+=1
            logger_game.info('Step {}------------'.format(step))
            logger1.info('Step {}------------'.format(step))
            logger2.info('Step {}------------'.format(step))
            logger_game.info('{}'.format(game.print_board(False)))
            if not game.have_valid_moves():
                logger1.info('No valid moves\n')
                agent1_no_valid_moves = True
                action1='N/A'
                if agent2_no_valid_moves:
                    break
                game.current_player *= -1
            else:
                agent1_no_valid_moves = False
                frame_input = game.move_with_hint()
                col, row = async_call_llm_api(frame_input, logger1, agent1, agent1_str, game.force_move())

                if not game.make_move(col, row):
                    force_penalty[0] += 1
                    col, row = game.force_move()
                    print(f'wrong move of {agent1_str}!!!')
                    if not game.make_move(col, row):
                        pdb.set_trace()
                action1 = (col, row)

            logger_game.info('{}'.format(game.print_board(False)))

            if not game.have_valid_moves():
                logger2.info('No valid moves\n')

                agent2_no_valid_moves = True
                action2 = 'N/A'
                if agent1_no_valid_moves:
                    break
                game.current_player *= -1
            else:
                agent2_no_valid_moves = False
                frame_input = game.move_with_hint()
                col, row = async_call_llm_api(frame_input, logger2, agent2, agent2_str, game.force_move())
                if not game.make_move(col, row):
                    print(f'wrong move of {agent2_str}!!!')
                    force_penalty[1] += 1
                    col, row = game.force_move()
                    if not game.make_move(col, row):
                        pdb.set_trace()
                action2 = (col, row)

            logger_game.info(
                '{} takes action {}; {} takes action {}'.format(agent1_str, action1, agent2_str, action2))

            curr_time = time.time()
            duration_seconds = curr_time - start_time
            # Convert duration to hours, minutes, and seconds
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)

            # Print the duration
            logger_game.info(f"Duration: {hours} hours, {minutes} minutes, {seconds} seconds")

        agent1_score, agent2_score = game.get_score()
        logger_game.info(
            'Final result: {} scores {} hint_penalty {} force_penalty {}, and {} scores {} hint_penalty {} force_penalty {}'.format(
                agent1_str, agent1_score, hint_penalty[0], force_penalty[0], agent2_str, agent2_score, hint_penalty[1],
                force_penalty[1]))
        if agent1_score>agent2_score:
            agent1_scores += 1
        elif agent1_score<agent2_score:
            agent2_scores += 1
    logger_game.info('Final score: {} {}:{} {}'.format(agent1_str, agent1_scores, agent2_scores, agent2_str))
# Create the parser
parser = argparse.ArgumentParser(description='Parser for test of agent')

# Add arguments
parser.add_argument('agent1_str', help='Path to the input file')
parser.add_argument('agent2_str', help='Path to the output file')
parser.add_argument('--cycles', type=int, help='Times of game cycles', default=1)
parser.add_argument('--key_start', type=int, help='Times of game cycles', default=0)

# Parse the arguments
args = parser.parse_args()
main()