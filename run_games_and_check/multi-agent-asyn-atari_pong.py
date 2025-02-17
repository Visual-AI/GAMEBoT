from pettingzoo.atari import pong_v3
from collections import deque
from gymnasium.utils.save_video import save_video
import time, os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)  # add path
from utils.get_real_position import *
from prompt_check_intermediate import *
import logging
from datetime import datetime
import asyncio
import keys
import random
import argparse
from agent_list import InitAgent
from utils.util import ram2label, find_action


async def async_call_llm_api(frame_input, logger, agent, agent_str):
    if agent_str == 'random':
        return random.choice([0, 1, 2])
    else:
        logger.info(frame_input)
        final_input1 = system_prompt_pong + frame_input
        response = agent.get_response_text(final_input1)
        if response.startswith("None - failed to generate content after"):
            logger.info('None - failed to generate content')
            return -1
        logger.info(response)
        action = find_action(response)
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
    game_str = "pong"
    cycles = args.cycles
    agent1_scores = 0
    agent2_scores = 0
    draw_scores = 0
    init_agent = InitAgent(key_start=args.key_start)
    agent1 = init_agent.init_agent(agent1_str)
    agent2 = init_agent.init_agent(agent2_str)
    run_category = 'running_log/{}/{}_vs_{}_'.format(game_str, agent1_str, agent2_str) + date_string

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
    # logging.basicConfig(filename='{}/logfile.log'.format(run_category), level=logging.INFO)

    env = pong_v3.parallel_env(num_players=2, render_mode="rgb_array",auto_rom_install_path='path/to/roms')
    env.reset(seed=random.randint(0, 9999))
    rgb_list = []
    action2 = 0
    action1 = 0
    refined_info_queue = deque(maxlen=4)
    info_flipped_queue = deque(maxlen=4)
    count_for_request = 0
    start_time = time.time()
    step_skim = 4

    for cycle in range(cycles):
        step = 0
        logger_game.info('Cycle {}===================='.format(cycle))
        logger1.info('Cycle {}===================='.format(cycle))
        logger2.info('Cycle {}===================='.format(cycle))
        while env.agents:
            step += 1
            if step % step_skim == 0:
                ram_res = env.unwrapped.ale.getRAM()
                labels = ram2label('pong', ram_res)
                refined_info = get_real_position_pong(labels)
                refined_info_queue.append(refined_info)
                info_flipped = get_real_position_pong_flipped(labels)
                info_flipped_queue.append(info_flipped)
                if refined_info['ball_y'] == 222:
                    action1 = 1
                    action2 = 1
                else:
                    logger_game.info('step {}----------'.format(step))
                    logger1.info('step {}----------'.format(step))
                    logger2.info('step {}----------'.format(step))
                    logger_game.info(labels)
                    logger_game.info(refined_info)
                    if step > 60:
                        # if 21 < refined_info['ball_x'] <= 143:
                        if 60 < refined_info['ball_x'] <= 104:
                            step_skim=12
                        elif 40< refined_info['ball_x'] <= 124:
                            step_skim=8
                        else:
                            step_skim=4
                        frame_input1 = 'Input:\n\n Frame {}\n {} \n Frame {}\n {}\n Frame {}\n {} \nOutput:'.format(
                            step - 2,str(refined_info_queue[1]),step - 1,str(refined_info_queue[2]),step,str(refined_info_queue[3]))
                        frame_input2 = 'Input:\n\n Frame {}\n {} \n Frame {}\n {}\n Frame {}\n {} \nOutput:'.format(
                            step - 2,str(info_flipped_queue[1]),step - 1,str(info_flipped_queue[2]),step,str(info_flipped_queue[3]))
                        task1 = async_call_llm_api(frame_input1, logger1, agent1, agent1_str)
                        task2 = async_call_llm_api(frame_input2, logger2, agent2, agent2_str)
                        action_gather = await asyncio.gather(task1, task2)
                        action1 = action_gather[0]
                        action2 = action_gather[1]
                        if action1 == -1 or action2 == -1:
                            logger_game.info('Rate limit or network problem, break')
                            break
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

                        count_for_request += 1
                        if count_for_request % 9500 == 0:
                            agent1 = init_agent.init_agent(agent1_str)
                            agent2 = init_agent.init_agent(agent2_str)
                            print('too many requests, reinit agent with different api key')

                        elif count_for_request % 950 == 0:
                            if agent1_str == 'gemini-1.5-pro-latest':
                                agent1 = init_agent.init_agent(agent1_str)
                            if agent2_str == 'gemini-1.5-pro-latest':
                                agent2 = init_agent.init_agent(agent2_str)
                            print('too many requests, reinit gemini 1.5 agent with different api key')

                        if labels['player_score'] == 1:
                            logger_game.info(
                                f"{agent1_str} wins!!!!!!!!!!!!!!!!!!!!!!!!!!! Cost total {count_for_request} requests")
                            agent1_scores += 1
                            env.reset(seed=random.randint(0, 9999))
                            break
                        if labels['enemy_score'] == 1:
                            logger_game.info(
                                f"{agent2_str} wins!!!!!!!!!!!!!!!!!!!!!!!!!!! Cost total {count_for_request} requests")
                            agent2_scores += 1
                            env.reset(seed=random.randint(0, 9999))
                            break
            if step > 1000:
                logger_game.info('step > 1000, break')
                logger_game.info('Draw!!!!!!!!!!!!!!!!!!!!!!!!!!! Both add 1 score')
                draw_scores += 1
                break
            '''
                agents[0] is the right paddle, agents[1] is the left paddle.
            '''
            actions = {env.agents[0]: action1, env.agents[1]: action2}
            observations, rewards, terminations, truncations, infos = env.step(actions)
            rgb_list.append(env.render())

        # if step > 100:
        #     break
        # if labels
    save_video(rgb_list[60:], run_category, fps=60, step_starting_index=0, episode_index=0,
               name_prefix='{}_vs_{}'.format(agent1_str, agent2_str))
    env.close()
    logger_game.info(
        'Final result: {} scores {}, and {} scores {}, draw {} times'.format(agent1_str, agent1_scores, agent2_str,
                                                                             agent2_scores, draw_scores))


# Create the parser
parser = argparse.ArgumentParser(description='Parser for test of agent')

# Add arguments

parser.add_argument('agent1_str', help='agent1')
parser.add_argument('agent2_str', help='agent2')
# parser.add_argument('game', help='which game to play')

parser.add_argument('--cycles', type=int, help='Times of game cycles', default=1)
parser.add_argument('--key_start', type=int, help='Times of game cycles', default=0)
# Parse the arguments
args = parser.parse_args()
asyncio.run(main())
