import random

from utils.ram_annotations import atari_dict
import re


def ram2label(env_name, ram):
    game_name = env_name.split("-")[0].split("No")[0].split("Deterministic")[0]
    if game_name.lower() in atari_dict:
        label_dict = {k: ram[ind] for k, ind in atari_dict[game_name.lower()].items()}
    else:
        assert False, "{} is not currently supported by AARI. It's either not an Atari game or we don't have the ram annotations yet!".format(
            game_name)
    return label_dict


def find_action(response):
    response = response.lower()
    response_split = response.split('[action]')
    action_text = response_split[-1].strip()
    '''
    action space:   Discrete(6)
        0 - NOOP (No Operation, do nothing)
        1 - FIRE (Not used in the game of Pong)
        2 - RIGHT (Move the paddle up)
        3 - LEFT (Move the paddle down)
        4 - RIGHTFIRE (Not used in the game of Pong)
        5 - LEFTFIRE (Not used in the game of Pong)
    '''
    if 'move up' in action_text.lower():
        action = 2
    elif 'move down' in action_text.lower():
        action = 3
    elif 'stay still' in action_text.lower():
        action = 0
    else:
        print('#### No valid action find!!!')
        print(action_text)
        action = 0

    return action


def find_action_surround(response):
    response = response.lower()
    response_split = response.split('chosen action')
    action_text = response_split[-1].strip()
    """
        | Action    | Behavior  |
        |:---------:|-----------|
        | 0         | No operation |
        | 1         | Move up |
        | 2         | Move right |
        | 3         | Move left |
        | 4         | Move down |
    """

    if 'move up' in action_text.lower():
        action = 1
    elif 'move right' in action_text.lower():
        action = 2
    elif 'move left' in action_text.lower():
        action = 3
    elif 'move down' in action_text.lower():
        action = 4

    else:
        print('#### No valid action find!!!')
        print(action_text)
        action = 0

    return action


def find_action_checkers(response):
    response = response.lower()
    response_split = response.split('chosen move')
    if len(response_split) == 1:
        print('#### No action find!!!')
        print(response)
    action_text = response_split[-1].strip()
    pattern = r"\((\d),\s*(\d)\)\s*->\s*\((\d),\s*(\d)\)"

    match = re.search(pattern, action_text)

    if match:
        coordinates = [int(group) for group in match.groups() if group is not None]
        print(coordinates)  # 输出: [2, 3, 4, 5, 6, 7]
    else:
        print("Invalid move input format.")
        print(response)
        coordinates = []
    return coordinates


def find_action_connect4(response):
    response = response.lower()
    response_split = response.split('chosen move')
    if len(response_split) == 1:
        print('#### No action find!!!')
        print(response)
    action_text = response_split[-1].strip()
    pattern = r"\((\d),\s*(\d)\)\s*"

    match = re.search(pattern, action_text)

    if match:
        coordinates = [int(group) for group in match.groups() if group is not None]
    else:
        print("Invalid move input format.")
        print(response)
        coordinates = []
    return coordinates


def call_llm_api_connect4(state_prompt, system_prompt, logger, agent):
    logger.info(state_prompt)
    final_input1 = system_prompt + '\n' + state_prompt
    response = agent.get_response_text(final_input1)
    logger.info(response)
    actions = find_action_connect4(response)
    return actions


def find_action_negotiate(response):
    # Input: "Proposal: [Agree]" or "Proposal: [P1: (X,X,X), P2: (X,X,X)]", where X is an integer can be any number.
    # Output: [-1, -1, -1, -1, -1, -1] or [X, X, X, X, X, X]
    if response=='random':
        if random.random() < 0.5:
            return [-1, -1, -1, -1, -1, -1]
        else:
            return [random.randint(0, 10) for _ in range(6)]
    response = response.lower()
    response_split = response.split('proposal:')
    action_text = response_split[-1].strip()
    if 'agree' in action_text:
        action = [-1, -1, -1, -1, -1, -1]
    else:
        pattern = r"\((\d+),\s*(\d+),\s*(\d+)\),\s*p2:\s*\((\d+),\s*(\d+),\s*(\d+)\)"
        match = re.search(pattern, action_text)
        if match:
            coordinates = [int(group) for group in match.groups() if group is not None]
            action = coordinates
        else:
            print("Invalid proposal input format.")
            print(response)
            action = [-1, -1, -1, -1, -1, -1]
    return action


def find_intermediate_negotiate(response):
    # Problem 1: in the opponent's latest proposal, the total value of the items for you and provide the result in the format [Intermediate Thinking Results 1: XXX].
    # Problem 2: When making a new proposal, Output the total value of the items for you in the new proposal in the format [Intermediate Thinking Results 2: XXX].
    response = response.lower()
    response_split = response.split('proposal:')
    action_text = response_split[-1].strip()

    # Intermediate Thinking Results
    # Problem 1
    pattern_problem1 = r"intermediate thinking results 1: (\d+)"
    match_problem1 = re.search(pattern_problem1, response)
    if match_problem1:
        try:
            intermediate_results1 = int(match_problem1.group(1))
        except:
            intermediate_results1 = -1
    else:
        intermediate_results1 = -1

    # Problem 2
    pattern_problem2 = r"intermediate thinking results 2: (\d+)"
    match_problem2 = re.search(pattern_problem2, response)
    if match_problem2:
        try:
            intermediate_results2 = int(match_problem2.group(1))
        except:
            intermediate_results2 = -1
    else:
        intermediate_results2 = -1
    return intermediate_results1, intermediate_results2


def find_intermediate_texas(response):
    # Problem 1: Judge which is your private hand and output the corresponding winning probability in the format [Intermediate Thinking Results 1: XXX].
    # Problem 2: At flop, turn, and river round, first analyse your best five-card hand and output your hand ranking according to the game rules in the format [Intermediate Thinking Results 2: XXX].
    response = response.lower()
    response_split = response.split('proposal:')
    action_text = response_split[-1].strip()

    # Intermediate Thinking Results
    # Problem 1
    pattern_problem1 = r"intermediate thinking results 1: (\d+(\.\d+)?)%"
    match_problem1 = re.search(pattern_problem1, response)
    if match_problem1:
        intermediate_results1 = float(match_problem1.group(1))
    else:
        intermediate_results1 = -1

    # Problem 2
    pattern_problem2 = r"intermediate thinking results 2: (\d+)"
    match_problem2 = re.search(pattern_problem2, response)
    if match_problem2:
        intermediate_results2 = int(match_problem2.group(1))
    else:
        intermediate_results2 = -1
    return intermediate_results1, intermediate_results2


def find_intermediate_tictactoe(response):
    pass

def find_intermediate_checkers(response):
    pass

def find_intermediate_connect4(response):
    pass

def find_intermediate_surround(response):
    pass

def find_intermediate_pong(response):
    pass

def find_intermediate(response):
    pass


def call_llm_api(state_prompt, system_prompt, logger, agent, find_action_function):
    logger.info(state_prompt)
    final_input1 = system_prompt + '\n' + state_prompt
    response = agent.get_response_text(final_input1)
    logger.info(response)
    actions = find_action_function(response)
    return actions


def call_llm_api_check_intermediate(state_prompt, system_prompt, logger, agent, game_name, find_action_function=None):
    logger.info(state_prompt)
    final_input1 = system_prompt + '\n' + state_prompt
    response = agent.get_response_text(final_input1)
    logger.info(response)
    intermediate_results = game_intermediate_function_dict[game_name](response)

    if find_action_function is not None:
        actions = find_action_function(response)
    else:
        actions = game_function_dict[game_name](response)

    return intermediate_results, actions


game_function_dict = {
    'connect4': find_action_connect4,
    'checkers': find_action_checkers,
    'tictactoe': find_action,
    'pong': find_action,
    'surround': find_action_surround,
    'negotiate': find_action_negotiate,
}

game_intermediate_function_dict = {
    'connect4': find_intermediate_connect4,
    'checkers': find_intermediate_checkers,
    'tictactoe': find_intermediate_tictactoe,
    'pong': find_intermediate_pong,
    'surround': find_intermediate_surround,
    'negotiate': find_intermediate_negotiate,
    'texas': find_intermediate_texas,
}

if __name__ == '__main__':
    to_find = '''
    in the format [Intermediate Thinking Results 1: 36]. 
    
    [Intermediate Thinking Results 2: 15].
    '''
    print(find_intermediate_negotiate(to_find))