from pettingzoo.classic import texas_holdem_no_limit_v6
import random
import sys
import time, os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir) # add path

from prompt_check_intermediate import *
import logging
from datetime import datetime
import argparse
from agent_list import InitAgent
from utils.util import *
from check_and_random import *

class TexasHoldem:
    action = None

    def __init__(self):
        self.first_check = True
        self.idx2card = {
            0: "A",
            1: "2",
            2: "3",
            3: "4",
            4: "5",
            5: "6",
            6: "7",
            7: "8",
            8: "9",
            9: "10",
            10: "J",
            11: "Q",
            12: "K",
        }
        self.act2pos = {
            0: "Fold",
            1: "Check and Call",
            2: "Raise Half Pot",
            3: "Raise Full Pot",
            4: "All in"
        }
        self.act2des = {
            0: "Fold: Choosing 'Fold' means the player is out of the hand, forfeiting any potential claim to the pot and not committing any more chips to the pot.",
            1: "Check and Call: If no bet has been made, a player can choose to 'Check', which means they do not wish to make a bet, and play passes to the next player. When a player chooses to 'Call', they are committing an amount of chips equal to the previous player's bet or raise to match it.",
            2: "Raise Half Pot: The player raises an amount equal to half the size of the current pot.",
            3: "Raise Full Pot: The player raises an amount equal to the full size of the current pot.",
            4: "All in: This is a bet where the player wagers all of their remaining chips.",

        }
        self.pos2act = {value.replace(" ", "").lower(): key for (key, value) in self.act2pos.items()}
        self.private = set()

    def _extract_card(self, observation):
        cards = set()
        observation = observation[:52]
        for idx, card in enumerate(observation[:13]):
            if card == 1:
                cards.add("Spades " + self.idx2card[idx])
        for idx, card in enumerate(observation[13:26]):
            if card == 1:
                cards.add("Hearts " + self.idx2card[idx])
        for idx, card in enumerate(observation[26:39]):
            if card == 1:
                cards.add("Diamonds " + self.idx2card[idx])
        for idx, card in enumerate(observation[39:52]):
            if card == 1:
                cards.add("Clubs " + self.idx2card[idx])
        return cards

    def _get_board_status(
            self, observation
    ):
        if self.first_check is True:
            self.first_check = False
            self.private = self._extract_card(observation['observation'])
        self.public = self._extract_card(observation['observation']) - self.private

    def get_state_message(
            self, action_mask, observation, info=None
    ):
        self._get_board_status(observation=observation)
        if len(self.public) == 0:
            round='Pre-flop'
        elif len(self.public) == 3:
            round='Flop'
        elif len(self.public) == 4:
            round='Turn'
        elif len(self.public) == 5:
            round='River'
        chips = observation['observation'][52]
        message = f"Current round is {round}\n"
        message += f"The cards in your hands is [{', '.join(list(self.private))}]\n"
        message += f"The community cards is [{', '.join(list(self.public))}]\n"
        message += f"You now have {100 - chips} chips. You has put in the pot {chips} chips. Your opponent has put in the pot {observation['observation'][53]} chips. \n"
        message += f"You can choose one of the following actions: "
        available = [self.act2pos[idx] for idx, action in enumerate(action_mask) if action == 1]
        message += f"[ {', '.join(available)} ]"
        print(message)
        return message

    def find_action_texas(self, answer):
        answer_split = answer.lower().split('chosen action')[-1]
        pos = re.findall(r'\s*(fold|check and call|raise half pot|raise full pot|all in)', answer_split)
        if len(pos)<1:
            action = 0
            print('not find any valid!!!')
            print(answer)
        else:
            pos = pos[0].replace(" ", "")
            action = self.pos2act[pos]
        return action


def main():

    #---------------To be modified: define game and prompt----------------
    game_str = "texas_holdem"
    system_prompt = system_prompt_texas_holdem
    #---------------------------------------------

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
    run_category_game =  'running_log/{}'.format(game_str)
    if not os.path.exists(run_category_game):
        # Create the directory
        # os.mkdir(run_category_game)
        os.makedirs(run_category_game, exist_ok=True)
        print("Directory created:", run_category_game)

    run_category = run_category_game+'/{}_vs_{}_'.format(agent1_str, agent2_str) + date_string

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
        env = texas_holdem_no_limit_v6.env(render_mode="rgb_array")
        env.reset()
        texas_class1 = TexasHoldem()
        texas_class2 = TexasHoldem()
        # ---------------------------------------------
        step = 0
        logger_game.info('Cycle {}===================='.format(cycle))
        logger1.info('Cycle {}===================='.format(cycle))
        logger2.info('Cycle {}===================='.format(cycle))
        agent1_reward, agent2_reward = 0, 0

        # ---------------To be modified: define stop of game----------------
        for agent in env.agent_iter():
            observation, reward, termination, truncation, info = env.last()
            print(agent)
            mask = observation["action_mask"]

            if termination or truncation:
                action = None
            else:
                # ---------------To be modified: get game state from env and call llm to get actions----------------
                if agent == 'player_0':
                    game_state = texas_class1.get_state_message(mask, observation)
                    logger_game.info(f'\n{agent1_str}\'s turn------------')
                    logger_game.info(game_state)
                else:
                    game_state = texas_class2.get_state_message(mask, observation)
                    logger_game.info(f'\n{agent2_str}\'s turn------------')
                    logger_game.info(game_state)

                state_prompt = 'Current Game State: \n\n' + game_state + '\n'
                if agent=='player_0':
                    if agent1_str == 'random':
                        intermediate_results, action = random_texas(mask)
                        logger_game.info(f'{agent1_str} {texas_class1.act2pos[action]}')
                        print(f'{agent1_str} {texas_class1.act2pos[action]}')
                    else:
                        intermediate_results, action = call_llm_api_check_intermediate(state_prompt, system_prompt, logger1, agent1, "texas", find_action_function=texas_class1.find_action_texas)
                        logger_game.info(f'{agent1_str} {texas_class1.act2pos[action]}')
                        print(f'{agent1_str} {texas_class1.act2pos[action]}')
                    logger_game.info(f'Intermediate results: {intermediate_results}')
                    # check_results = check_intermediate_texas(intermediate_results, texas_class1.private, texas_class1.public)
                    # agent1_intermediate_correct += check_results[0]
                    # agent1_intermediate_total += check_results[1]
                else:
                    if agent2_str == 'random':
                        intermediate_results, action = random_texas(mask)
                        logger_game.info(f'{agent2_str} {texas_class2.act2pos[action]}')
                        print(f'{agent2_str} {texas_class2.act2pos[action]}')
                    else:
                        intermediate_results, action = call_llm_api_check_intermediate(state_prompt, system_prompt, logger2, agent2, "texas", find_action_function=texas_class2.find_action_texas)
                        logger_game.info(f'{agent2_str} {texas_class2.act2pos[action]}')
                        print(f'{agent2_str} {texas_class2.act2pos[action]}')
                    logger_game.info(f'Intermediate results: {intermediate_results}')
                    # check_results = check_intermediate_texas(intermediate_results, texas_class2.private, texas_class2.public)
                    # agent2_intermediate_correct += check_results[0]
                    # agent2_intermediate_total += check_results[1]
                
            indices_of_ones = [i for i, value in enumerate(mask) if value == 1]
            if action not in indices_of_ones and len(indices_of_ones)>0:
                action = indices_of_ones [-1]
            env.step(action)
            step += 1

            curr_time = time.time()
            duration_seconds = curr_time - start_time
            # Convert duration to hours, minutes, and seconds
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            count_for_request+=1
            # Print the duration
            logger_game.info(f"Duration: {hours} hours, {minutes} minutes, {seconds} seconds")

            # ---------------To be modified: log results at every cycle----------------
            if reward!=0:
                if agent == 'player_0':
                    agent1_reward = reward
                else:
                    agent2_reward = reward

            # ---------------------------------------------
        agent1_scores+=agent1_reward
        agent2_scores+=agent2_reward
        logger_game.info('Cycle {} results: {} {}:{} {};'.format(cycle, agent1_str, agent1_reward, agent2_str, agent2_reward))
        env.close()

    # ---------------To be modified: log final results----------------
    logger_game.info('Final score: {} {}:{} {}; total {} requests'.format(agent1_str, agent1_scores, agent2_str, agent2_scores, count_for_request))
    # logger_game.info('Agent1 intermediate correct rate: {}/{}, {}'.format(agent1_intermediate_correct, agent1_intermediate_total, agent1_intermediate_correct/agent1_intermediate_total))
    # logger_game.info('Agent2 intermediate correct rate: {}/{}, {}'.format(agent2_intermediate_correct, agent2_intermediate_total, agent2_intermediate_correct/agent2_intermediate_total))
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