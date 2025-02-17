from pettingzoo.atari import surround_v2
from collections import deque
from gymnasium.utils.save_video import save_video
import time, os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir) # add path
from prompt_check_intermediate import *
import logging
from datetime import datetime
import asyncio
import keys
import random
import argparse
from agent_list import InitAgent
from utils.util import ram2label, find_action_surround
from tabulate import tabulate


async def async_call_llm_api(frame_input, system_prompt, logger, agent, agent_str):
    if agent_str == 'random':
        action = random.choice([0, 1, 2, 3, 4])
    else:
        logger.info(frame_input)
        final_input1 = system_prompt + frame_input
        response = agent.get_response_text(final_input1)
        if response.startswith("None - failed to generate content after"):
            logger.info('None - failed to generate content')
            return -1
        logger.info(response)
        action = find_action_surround(response)
    return action


async def main():
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
    game_str = "surround"
    cycles = args.cycles
    agent1_scores = 0
    agent2_scores = 0
    draw_count = 0
    init_agent = InitAgent(key_start=args.key_start)
    agent1 = init_agent.init_agent(agent1_str)
    agent2 = init_agent.init_agent(agent2_str)
    # action1_list = [1,1,2,2,3,3,4,4,1,1,2,2,3,3,4,4]
    run_category = 'running_log/{}/{}_vs_{}_'.format(game_str, agent1_str, agent2_str) + date_string

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
    env = surround_v2.parallel_env(render_mode="rgb_array", auto_rom_install_path='path/to/roms')
    observations, infos = env.reset(seed=random.randint(0, 9999))

    rgb_list = []

    count_for_request = 0
    start_time = time.time()
    rows = 20
    cols = 40
    logger1.info('Prompt:\n {}'.format(system_prompt_surround_agent1))
    logger2.info('Prompt:\n {}'.format(system_prompt_surround_agent2))

    for cycle in range(cycles):
        action2 = 0
        action1 = 0
        game_state = [[0 for _ in range(cols)] for _ in range(rows)]
        # Set edge values to 1
        for i in range(len(game_state)):
            for j in range(len(game_state[0])):
                if i == 0 or i == len(game_state) - 1 or j == 0 or j == len(game_state[0]) - 1:
                    game_state[i][j] = 1

        agent1_coordinates_deque = deque(maxlen=3)
        agent1_coordinates_deque.append((10, 30))
        agent2_coordinates_deque = deque(maxlen=3)
        agent2_coordinates_deque.append((10, 10))
        trace_str1 = '({},{})'.format(agent1_coordinates_deque[-1][0], agent1_coordinates_deque[-1][1])
        trace_str2 = '({},{})'.format(agent2_coordinates_deque[-1][0], agent2_coordinates_deque[-1][1])
        game_state[agent1_coordinates_deque[-1][0]][agent1_coordinates_deque[-1][1]] = 5
        game_state[agent2_coordinates_deque[-1][0]][agent2_coordinates_deque[-1][1]] = 3
        step = 0
        render_longer = 0
        logger_game.info('Cycle {}===================='.format(cycle))
        logger1.info('Cycle {}===================='.format(cycle))
        logger2.info('Cycle {}===================='.format(cycle))
        while env.agents:
            ram_res = env.unwrapped.ale.getRAM()
            labels = ram2label("surround", ram_res)
            step += 1

            no_change = labels['player_i'] == agent1_coordinates_deque[-1][0] and labels['player_j'] == \
                        agent1_coordinates_deque[-1][1]
            agent1_out_of_boundary = (labels['player_i'] < 1 or labels['player_i'] > 18) or (
                    labels['player_j'] < 1 or labels['player_j'] > 38)
            agent2_out_of_boundary = (labels['enemy_i'] < 1 or labels['enemy_i'] > 18) or (
                    labels['enemy_j'] < 1 or labels['enemy_j'] > 38)
            if render_longer > 1:
                action1 = 0
                action2 = 0
                render_longer -= 1
            elif render_longer == 1:
                env.reset()
                break
            elif agent1_out_of_boundary:
                print('agent1 out of boundary')
                action1 = 0
            elif agent2_out_of_boundary:
                print('agent2 out of boundary')
                action2 = 0
            elif step == 1 or not no_change:
                if step != 1 and not no_change:
                    agent1_coordinates_deque.append((labels['player_i'], labels['player_j']))
                    agent2_coordinates_deque.append((labels['enemy_i'], labels['enemy_j']))
                    game_state[agent1_coordinates_deque[-1][0]][agent1_coordinates_deque[-1][1]] = 5
                    game_state[agent2_coordinates_deque[-1][0]][agent2_coordinates_deque[-1][1]] = 3
                    game_state[agent1_coordinates_deque[-2][0]][agent1_coordinates_deque[-2][1]] = 4
                    game_state[agent2_coordinates_deque[-2][0]][agent2_coordinates_deque[-2][1]] = 2
                    if len(agent1_coordinates_deque) == 3:
                        game_state[agent1_coordinates_deque[0][0]][agent1_coordinates_deque[0][1]] = 1
                        game_state[agent2_coordinates_deque[0][0]][agent2_coordinates_deque[0][1]] = 1
                    trace_str1 = trace_str1 + '->' + '({},{})'.format(agent1_coordinates_deque[-1][0],
                                                                         agent1_coordinates_deque[-1][1])
                    trace_str2 = trace_str2 + '->' + '({},{})'.format(agent2_coordinates_deque[-1][0],
                                                                         agent2_coordinates_deque[-1][1])
                print(labels)
                print(tabulate(game_state))
                logger_game.info('step {}----------'.format(step))
                logger1.info('step {}----------'.format(step))
                logger2.info('step {}----------'.format(step))
                array_string = '\n'.join(
                    [' '.join('({},{}):{}'.format(i, j, game_state[i][j]) for j in range(len(game_state[0]))) for i
                     in range(len(game_state))])
                frame_input2 = '\nInput:\n\nYour moving trace:\n {}\n\nCurrent Game State:\n{} \n\nOutput:\n'.format(trace_str2,
                                                                                                      array_string)
                frame_input1 = '\nInput:\n\nYour moving trace:\n {}\n\nCurrent Game State:\n{} \n\nOutput:\n'.format(trace_str1,
                                                                                                      array_string)

                if agent1_coordinates_deque[-1][0] == agent2_coordinates_deque[-1][0] and agent1_coordinates_deque[-1][
                    1] == agent2_coordinates_deque[-1][1] and render_longer == 0:
                    print('agent1 and agent2 collide, draw')
                    draw_count += 1
                    logger_game.info(
                        f" agent1 and agent2 collide, draw!!!!!!!!!!!!!! Cost total {count_for_request} requests")
                    render_longer = 80

                task1 = async_call_llm_api(frame_input1, system_prompt_surround_agent1, logger1, agent1, agent1_str)
                task2 = async_call_llm_api(frame_input2, system_prompt_surround_agent2, logger2, agent2, agent2_str)
                action_gather = await asyncio.gather(task1, task2)
                action1 = action_gather[0]
                action2 = action_gather[1]
                if action1 == -1 or action2 == -1:
                    logger_game.info('Rate limit or network problem, break')
                    break
                logger_game.info(tabulate(game_state))
                logger_game.info('{} takes action {}; {} takes action {}'.format(agent1_str, action1, agent2_str, action2))

                curr_time = time.time()
                duration_seconds = curr_time - start_time
                # Convert duration to hours, minutes, and seconds
                hours = int(duration_seconds // 3600)
                minutes = int((duration_seconds % 3600) // 60)
                seconds = int(duration_seconds % 60)

                # Print the duration
                logger_game.info(f"Duration: {hours} hours, {minutes} minutes, {seconds} seconds")
                # #
                count_for_request += 1
                # if count_for_request % 9500 == 0:
                #     agent1 = init_agent.init_agent(agent1_str)
                #     agent2 = init_agent.init_agent(agent2_str)
                #     print('too many requests, reinit agent with different api key')
                #
                # elif count_for_request % 950 == 0:
                #     if agent1_str == 'gemini-1.5-pro-latest':
                #         agent1 = init_agent.init_agent(agent1_str)
                #     if agent2_str == 'gemini-1.5-pro-latest':
                #         agent2 = init_agent.init_agent(agent2_str)
                #     print('too many requests, reinit gemini 1.5 agent with different api key')
            # action1 = 0
            # action2 = 0
            actions = {env.agents[0]: action1, env.agents[1]: action2}
            observations, rewards, terminations, truncations, infos = env.step(actions)
            # print('action space', env.action_space(env.agents[0]))
            # print('rewards:', rewards)
            # print('infos', infos)

            if rewards['first_0'] == 1 and render_longer == 0:
                agent1_scores += 1
                logger_game.info(
                    f"{agent1_str} wins!!!!!!!!!!!!!!!!!!!!!!!!!!! Cost total {count_for_request} requests")
                render_longer = 80
            if rewards['second_0'] == 1 and render_longer == 0:
                agent2_scores += 1
                logger_game.info(
                    f"{agent2_str} wins!!!!!!!!!!!!!!!!!!!!!!!!!!! Cost total {count_for_request} requests")
                render_longer = 80
            rgb_list.append(env.render())

    save_video(rgb_list, run_category, fps=60, step_starting_index=0, episode_index=0,
               name_prefix='{}_vs_{}'.format(agent1_str, agent2_str))
    env.close()
    logger_game.info(
        'Final result: {} scores {}, and {} scores {}'.format(agent1_str, agent1_scores, agent2_str, agent2_scores))


# Create the parser
parser = argparse.ArgumentParser(description='Parser for test of agent')

# Add arguments

parser.add_argument('agent1_str', help='agent1')
parser.add_argument('agent2_str', help='agent2')

parser.add_argument('--cycles', type=int, help='Times of game cycles', default=1)
parser.add_argument('--key_start', type=int, help='Times of game cycles', default=0)
# Parse the arguments
args = parser.parse_args()
asyncio.run(main())
