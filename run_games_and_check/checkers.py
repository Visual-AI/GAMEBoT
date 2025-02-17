import time, os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir) # add path
from prompt_check_intermediate import *
import logging
from datetime import datetime
import argparse
from agent_list import InitAgent
from game_env.checkers.game import Game, pos2rowcol
from utils.util import *


# print(game.board.get_possible_moves_rowcol())
#
# pprint.pprint(game.board.print_board())
# game.move_with_rowcol(2, 3, 3, 2)
# pprint.pprint(game.board.print_board())
# print(game.whose_turn())
# print(game.board.get_possible_moves_rowcol())
# game.move_with_rowcol(5, 2, 4, 1)
# pprint.pprint(game.board.print_board())
# print(game.whose_turn())
# print(game.board.get_possible_moves_rowcol())
# game.move_with_rowcol(3, 0, 5, 2)
# pprint.pprint(game.board.print_board())
# print(game.whose_turn())
# print(game.board.get_possible_moves_rowcol())

def call_llm_api(state_prompt, system_prompt, logger, agent):
    logger.info(state_prompt)
    final_input1 = system_prompt + state_prompt
    response = agent.get_response_text(final_input1)
    logger.info(response)
    actions = find_action_checkers(response)
    return actions

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
    run_category = 'running_log/checkers/{}_vs_{}_'.format(agent1_str, agent2_str) + date_string

    if not os.path.exists(run_category):
        # Create the directory
        # os.mkdir(run_category)
        os.makedirs(run_category)
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
    logger_game.info(system_prompt_checkers)
    count_for_request = 0
    start_time = time.time()

    for cycle in range(cycles):
        game = Game()
        step = 0
        logger_game.info('Cycle {}===================='.format(cycle))
        logger1.info('Cycle {}===================='.format(cycle))
        logger2.info('Cycle {}===================='.format(cycle))
        while not game.is_over():
            step+=1
            logger_game.info('Step {}------------'.format(step))
            logger1.info('Step {}------------'.format(step))
            logger2.info('Step {}------------'.format(step))
            board_state = game.board.print_board(with_coordinates=False)
            for row in board_state:
                logger_game.info(row)
            state_prompt = 'Current Game Board: \n' + str(game.board.print_board(with_coordinates=True)) + '\n'

            if game.whose_turn()==1:
                if agent1_str == 'random':
                    actions_pos = random.choice(game.get_possible_moves())
                    actions = pos2rowcol(actions_pos[0]) + pos2rowcol(actions_pos[1])
                else:
                    state_prompt+='Current valid moves for player White: '+str(game.board.get_possible_moves_rowcol())+'\n'
                    state_prompt+='You are player White, please choose the best move considering the current board state.\n'
                    actions = call_llm_api(state_prompt, system_prompt_checkers, logger1, agent1)
                logger_game.info(f'{agent1_str} takes move ({actions[0]},{actions[1]})->({actions[2]},{actions[3]})')
                    
            else:
                if agent2_str == 'random':
                    actions_pos = random.choice(game.get_possible_moves())
                    actions = pos2rowcol(actions_pos[0]) + pos2rowcol(actions_pos[1])
                else:
                    state_prompt+='Current valid moves for player Black: '+str(game.board.get_possible_moves_rowcol())+'\n'
                    state_prompt+='You are player Black, please choose the best move considering the current board state.\n'
                    actions = call_llm_api(state_prompt, system_prompt_checkers, logger2, agent2)
                logger_game.info(f'{agent2_str} takes move ({actions[0]},{actions[1]})->({actions[2]},{actions[3]})')

            game.move_with_rowcol(actions[0], actions[1], actions[2], actions[3])

            curr_time = time.time()
            duration_seconds = curr_time - start_time
            # Convert duration to hours, minutes, and seconds
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            count_for_request+=1
            # Print the duration
            logger_game.info(f"Duration: {hours} hours, {minutes} minutes, {seconds} seconds")

        if game.get_winner()==1:
            log_result_str = f'{agent1_str} wins!!!!!!!!!'
            agent1_scores += 1

        elif game.get_winner()==2:
            log_result_str = f'{agent2_str} wins!!!!!!!!!'
            agent2_scores += 1
        else:
            log_result_str = 'Draw!!!!!!!!!'
        logger_game.info(log_result_str)
    logger_game.info('Final score: {} {}:{} {}; total {} requests'.format(agent1_str, agent1_scores, agent2_str, agent2_scores, count_for_request))
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