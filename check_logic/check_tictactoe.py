import re

def check_tictactoe(intermediate_results, game_matrix, player, actions):
    # if actions format problem, give []

    """
    Output all of the winning moves for you in the format "[Intermediate Thinking Results 1: (X,X), (X,X), ...]". If none, output "[Intermediate Thinking Results 1: None]"
    :param intermediate_results: [Str,Str], if format error, str='Format Error'
    :param game_matrix:
        board = [
            ['_', 'O', 'X'],
            ['X', 'O', 'X'],
            ['O', 'X', '_']
        ]
    :param player: 'O' or 'X'
    :param actions: [row, col]
    :return: [acc1, acc2], [total1, total2], format_error, valid_action, invalid_action, action_format_error, action_total

    """
    # acc1, acc2, total1, total2, format_error = 0, 0, 1, 1, 0
    tp1, tn1, fp1, fn1, mm1 = 0, 0, 0, 0, 0
    tp2, tn2, fp2, fn2, mm2 = 0, 0, 0, 0, 0
    format_error = 0
    valid_action, invalid_action, action_format_error, action_total = 0, 0, 0, 1
    groundtruth_winning_moves_player, groundtruth_winning_moves_opponent = analyze_tic_tac_toe(game_matrix, player)

    if len(actions) != 2:
        action_format_error = 1
    else:
        row, col = actions[0], actions[1]
        if row < 0 or row >= 3 or col < 0 or col >= 3:
            invalid_action = 1
        elif game_matrix[row][col] != '_':
            invalid_action = 1
        else:
            valid_action = 1

    # check the first of the intermediate results
    result1 = intermediate_results[0].strip()
    if result1 == 'Format Error':
        format_error += 1
    elif result1 == 'None' or result1=='none':
        if groundtruth_winning_moves_player == []:
            tn1 = 1
        else:
            fn1 = 1
    else:
        all_moves = extract_coordinates(result1)
        if len(all_moves) == 0:
            format_error += 1
        else:
            if set(all_moves) == set(groundtruth_winning_moves_player):
                tp1 = 1
            else:
                if groundtruth_winning_moves_player == []:
                    fp1 = 1
                else:
                    mm1 = 1

    # check the second of the intermediate results
    result2 = intermediate_results[1].strip()
    if result2 == 'Format Error':
        format_error += 1
    elif result2 == 'None' or result2=='none':
        if groundtruth_winning_moves_opponent == []:
            tn2 = 1
        else:
            fn2 = 1
    else:
        all_moves = extract_coordinates(result2)
        if len(all_moves) == 0:
            format_error += 1
        else:
            if set(all_moves) == set(groundtruth_winning_moves_opponent):
                tp2 = 1
            else:
                if groundtruth_winning_moves_opponent == []:
                    fp2 = 1
                else:
                    mm2 = 1


    return [tp1, tn1, fp1, fn1, mm1], [tp2, tn2, fp2, fn2, mm2], format_error, valid_action, invalid_action, action_format_error, action_total

def check_winning_moves(board, player):
    """Checks for potential winning moves for a player in Tic Tac Toe.

    Args:
        board: A 3x3 matrix representing the game board.
        player: The player to check for ('X' or 'O').

    Returns:
        A list of tuples representing the winning moves for the player.
    """
    winning_moves = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == '_':  # Check only empty cells
                # Check horizontal
                if board[r][(c + 1) % 3] == player and board[r][(c + 2) % 3] == player:
                    winning_moves.append((r, c))
                # Check vertical
                if board[(r + 1) % 3][c] == player and board[(r + 2) % 3][c] == player:
                    winning_moves.append((r, c))
                # Check diagonal (top-left to bottom-right)
                if r == c and board[(r + 1) % 3][(c + 1) % 3] == player and board[(r + 2) % 3][(c + 2) % 3] == player:
                    winning_moves.append((r, c))
                # Check diagonal (top-right to bottom-left)
                if r + c == 2 and board[(r + 1) % 3][(c - 1) % 3] == player and board[(r + 2) % 3][
                    (c - 2) % 3] == player:
                    winning_moves.append((r, c))
    return winning_moves


def analyze_tic_tac_toe(board, player):
    """Analyzes the Tic Tac Toe board and finds potential winning moves.

    Args:
        board: A 3x3 matrix representing the game board.
        player: The current player ('X' or 'O').

    Returns:
        A tuple: (winning_moves_player, winning_moves_opponent)
        where each element is a list of winning moves for the respective player.
    """
    opponent = 'O' if player == 'X' else 'X'
    winning_moves_player = check_winning_moves(board, player)
    winning_moves_opponent = check_winning_moves(board, opponent)

    return winning_moves_player, winning_moves_opponent


def extract_coordinates(coordinates_string):
    """Extracts coordinates from a string in the format "(X,X), (X,X), ...".

    Args:
        coordinates_string: The string containing the coordinates.

    Returns:
        A list of tuples representing the coordinates.
    """
    # Remove parentheses and split by comma and space
    coordinates_list = re.findall(r"\((\d+),(\d+)\)", coordinates_string)

    # Convert to list of tuples of integers
    return [(int(x), int(y)) for x, y in coordinates_list]


def find_intermediate_and_action_tictactoe(response):

    response = response.lower()
    # Intermediate Thinking Results
    # Problem 1
    pattern_problem1 = re.compile(r"intermediate thinking results 1+: (.*?)\]")
    match_problem1 = re.search(pattern_problem1, response)
    if match_problem1:
        intermediate_results1 = match_problem1.group(1).strip()
    else:
        intermediate_results1 = 'Format Error'

    # Problem 2
    pattern_problem2 = re.compile(r"intermediate thinking results 2+: (.*?)\]")
    match_problem2 = re.search(pattern_problem2, response)
    if match_problem2:
        intermediate_results2 = match_problem2.group(1).strip()
    else:
        intermediate_results2 = 'Format Error'

    # Action
    response_split = response.split('Chosen Move')
    action_text = response_split[-1].strip()
    pattern = r"\((\d),\s*(\d)\)\s*"
    match = re.search(pattern, action_text)

    if match:
        action = [int(group) for group in match.groups() if group is not None]
    else:
        action = []
        
    return [intermediate_results1, intermediate_results2], action


if __name__ == "__main__":
    # board = [
    #     ['_', 'O', 'X'],
    #     ['X', 'O', 'X'],
    #     ['O', 'X', '_']
    # ]
    # player = 'O'  # Current player
    #
    # winning_moves_player, winning_moves_opponent = analyze_tic_tac_toe(board, player)
    #
    # print(f"[Intermediate Thinking Results 1: {winning_moves_player or 'None'}]")
    # print(f"[Intermediate Thinking Results 2: {winning_moves_opponent or 'None'}]")

    # Example usage
    coordinates_string = "(1,2),(3,4), (5,6)"
    coordinates_list = extract_coordinates(coordinates_string)
    print(coordinates_list)  # Output: [(1, 2), (3, 4), (5, 6)]