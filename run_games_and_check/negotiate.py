import random
import time, os
import sys

from scipy.constants import value

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)  # add path
from prompt_check_intermediate import *
import logging
from datetime import datetime
import argparse
from agent_list import InitAgent
from utils.util import *
from game_env.my_negotiate import Negotiate


def random_agent_negotiate(pool_values):
    if random.random()<0.5:
        return [-1, -1, -1, -1, -1, -1]
    else:
        random_results = [random.randint(0, pool_values[0]), random.randint(0, pool_values[1]), random.randint(0, pool_values[2])]
        random_results.extend([pool_values[0]-random_results[0], pool_values[1]-random_results[1], pool_values[2]-random_results[2]])
        return random_results

def main():
    # ---------------To be modified: define game and prompt----------------
    game_str = "negotiate"
    system_prompt = system_prompt_negotiate
    # ---------------------------------------------

    current_time = datetime.now()
    date_string = current_time.strftime("%m-%d-%H-%M")

    print(date_string)
    agent1_str = args.agent1_str
    agent2_str = args.agent2_str
    cycles = args.cycles
    agent1_scores = 0
    agent2_scores = 0
    agent1_intermediate_correct = 0
    agent1_intermediate_total = 0
    agent2_intermediate_correct = 0
    agent2_intermediate_total = 0
    init_agent = InitAgent(key_start=args.key_start)
    agent1 = init_agent.init_agent(agent1_str)
    agent2 = init_agent.init_agent(agent2_str)
    run_category_game = 'running_log/{}'.format(game_str)
    if not os.path.exists(run_category_game):
        # Create the directory
        os.mkdir(run_category_game)
        print("Directory created:", run_category_game)

    run_category = run_category_game + '/{}_vs_{}_'.format(agent1_str, agent2_str) + date_string + ''.join(
        random.choices(
            'abcdefghijklmnopqrstuvwxyz', k=2))

    if not os.path.exists(run_category):
        # Create the directory
        os.mkdir(run_category)
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

    logger_game.info(system_prompt)
    count_for_request = 0
    start_time = time.time()

    for cycle in range(cycles):
        # ---------------To be modified: define game environment----------------
        game_env = Negotiate()
        pool_values, p1_values, p2_values = game_env.new_game_state()
        # ---------------------------------------------
        logger_game.info('Cycle {}===================='.format(cycle))
        logger1.info('Cycle {}===================='.format(cycle))
        logger2.info('Cycle {}===================='.format(cycle))
        step = 0

        # ---------------To be modified: define stop of game----------------
        while not game_env.is_over():
            # ---------------------------------------------
            step += 1
            logger_game.info('Step {}------------'.format(step))

            # ---------------To be modified: get game state from env and call llm to get actions----------------
            actions = [0, 0, 0, 0, 0, 0]
            state_prompt_p1 = 'Current Game State: \n' + game_env.game_info_str('Player1') + '\n' + 'Your are Player1, output your answer.\n'
            state_prompt_p2 = 'Current Game State: \n' + game_env.game_info_str('Player2') + '\n' + 'Your are Player2, output your answer.\n'
            if game_env.get_player_type() == 'Player1':
                logger1.info('Step {}------------'.format(step))
                if agent1_str == 'random':
                    actions = random_agent_negotiate(pool_values)
                    intermediate_results=[-1,-1]
                else:
                    intermediate_results, actions = call_llm_api_check_intermediate(state_prompt_p1, system_prompt, logger1, agent1, game_str)
                check_results = game_env.check_intermediate_results(intermediate_results, actions)
                agent1_intermediate_correct += check_results[0]
                agent1_intermediate_total += check_results[1]

            elif game_env.get_player_type() == 'Player2':
                logger2.info('Step {}------------'.format(step))
                if agent2_str == 'random':
                    actions = random_agent_negotiate(pool_values)
                    intermediate_results=[-1,-1]
                else:
                    intermediate_results, actions = call_llm_api_check_intermediate(state_prompt_p2, system_prompt, logger2, agent2, game_str)
                check_results = game_env.check_intermediate_results(intermediate_results, actions)
                agent2_intermediate_correct += check_results[0]
                agent2_intermediate_total += check_results[1]

            game_env.apply_action(actions)
            # ---------------------------------------------

            curr_time = time.time()
            duration_seconds = curr_time - start_time
            # Convert duration to hours, minutes, and seconds
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            count_for_request += 1
            # Print the duration
            logger_game.info(f"Duration: {hours} hours, {minutes} minutes, {seconds} seconds")
        # ---------------To be modified: log results at every cycle----------------
        logger_game.info(game_env.game_info_str())
        agent1_scores += game_env.reward1
        agent2_scores += game_env.reward2
        # ---------------------------------------------

    # ---------------To be modified: log final results----------------
    logger_game.info(
        'Final score: {} {}:{} {}; total {} requests for two agents'.format(agent1_str, agent1_scores, agent2_str,
                                                                            agent2_scores, count_for_request))
    logger_game.info('Agent1 intermediate correct rate: {}/{}, {}'.format(agent1_intermediate_correct, agent1_intermediate_total, agent1_intermediate_correct/agent1_intermediate_total))
    logger_game.info('Agent2 intermediate correct rate: {}/{}, {}'.format(agent2_intermediate_correct, agent2_intermediate_total, agent2_intermediate_correct/agent2_intermediate_total))
    # ---------------------------------------------


# Create the parser
parser = argparse.ArgumentParser(description='Parser for test of agent')

# Add arguments
parser.add_argument('agent1_str', type=str, help='Agent 1 string')
parser.add_argument('agent2_str', type=str, help='Agent 2 string')
parser.add_argument('--cycles', type=int, help='Times of game cycles', default=1)
parser.add_argument('--key_start', type=int, help='', default=0)
# Parse the arguments
args = parser.parse_args()
main()
