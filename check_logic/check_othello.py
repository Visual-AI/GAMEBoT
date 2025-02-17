import re


def check_othello(intermediate_results, game_matrix, player, action, valid_actions):
    """
    problem1: Output whether you have a move to directly occupy the corners. The format is "[Intermediate Thinking Results 1: True/False]"
    problem2: ‘wedge’ in Othello is when a player can place a piece between two of the opponent’s stable pieces on the edge of the board. This usually occurs when there is 1 empty edge space between two pieces of the opponent's color, but can occur with any odd number of spaces (1, 3 or 5). Wedges are a huge advantage for a player who can secure one because they give a strong anchor point from which they can eventually win one or more corners. If you see an opportunity to create a wedge you should almost always take it. They severely limit your opponent’s viable moves.
        For example, if one of the edge is: [(A,1):O (B,1):O (C,1):B (D,1):O (E,1):B (F,1):O (G,1):O (H,1):O], since (D,1) is an empty edge space between two pieces of B, if (D,1) is a legal move for W player, it will create a wedge. Output all of the coordinates that can create a wedge in the format "[Intermediate Thinking Results 2: (X,X), (X,X), ...]".
    :param intermediate_results: [Str,Str], result1 str="True" or "False", or "Format Error", result2 str="(X,X), (X,X), ..." or "None" or other string, if not found intermediate result 2, return "Format Error"
    :param game_matrix: matrix of the game, 8x8 str matrix, with 'O' for empty, 'B' for black, 'W' for white
    :param player: 'B' or 'W'
    :param action: move of the player, tuple of (str, int), ('F',4) for example
    :param valid_actions: all valid actions for the player, list of tuple of (str, int), [('A',1), ('A',8), ('H',1), ('H',8)] for example
    :return:
    """
    true_positive1, false_positive1, true_negative1, false_negative1 = 0, 0, 0, 0
    true_positive2, false_positive2, true_negative2, false_negative2, mm = 0, 0, 0, 0,0
    format_error = 0
    valid_action, invalid_action, action_format_error, action_total = 0, 0, 0, 1
    opponent = 'B' if player == 'W' else 'W'
    if action[0] not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] or action[1] not in range(1, 9):
        action_format_error = 1
    elif action not in valid_actions:
        invalid_action = 1
    else:
        valid_action = 1
    # check the first of the intermediate results
    result1 = intermediate_results[0].strip()
    if result1 == 'Format Error':
        format_error += 1
    elif result1 == 'True' or result1 == 'true':
        if any([('A', 1) in valid_actions, ('A', 8) in valid_actions, ('H', 1) in valid_actions,
                ('H', 8) in valid_actions]):
            true_positive1 += 1
        else:
            false_positive1 += 1
    elif result1 == 'False' or result1 == 'false':
        if any([('A', 1) in valid_actions, ('A', 8) in valid_actions, ('H', 1) in valid_actions,
                ('H', 8) in valid_actions]):
            false_negative1 += 1
        else:
            true_negative1 += 1

    # check the second of the intermediate results
    result2 = intermediate_results[1].strip()
    if result2 == 'Format Error':
        format_error += 1
    else:
        moves_list = extract_moves(result2)
        # check ground truth for wedge move
        ground_truth_wedge_moves = []
        for move in valid_actions:
            if move[0] == 'A' or move[0] == 'H' or move[1] == 1 or move[1] == 8: # is edge
                if move not in [('A', 1), ('A', 8), ('H', 1), ('H', 8)]: # is not corner
                    if move[0] == 'A' or move[0] == 'H':
                        if game_matrix[move[1]-1-1][ord(move[0])-ord('A')]==opponent and game_matrix[move[1]-1+1][ord(move[0])-ord('A')]==opponent:
                            ground_truth_wedge_moves.append(move)
                    elif move[1] == 1 or move[1] == 8:
                        if game_matrix[move[1]-1][ord(move[0])-ord('A')-1]==opponent and game_matrix[move[1]-1][ord(move[0])-ord('A')+1]==opponent:
                            ground_truth_wedge_moves.append(move)
        if len(ground_truth_wedge_moves)>0:
            if set(moves_list) == set(ground_truth_wedge_moves):
                true_positive2 += 1
            else:
                if len(moves_list) == 0:
                    false_negative2 += 1
                else:
                    mm += 1
        else:
            if len(moves_list) == 0:
                true_negative2 += 1
            else:
                false_positive2 += 1

    return [true_positive1, false_positive1, true_negative1, false_negative1], [true_positive2, false_positive2, true_negative2, false_negative2,mm], format_error, valid_action, invalid_action, action_format_error, action_total


def extract_moves(moves_string):
    """Extracts moves from a string in the format "(C,2) (D,2) ..." and converts them to a list of tuples.

    Args:
        moves_string: The string containing the moves.

    Returns:
        A list of tuples, where each tuple represents a move in the format (str, int).
    """

    moves_list = []
    for move in re.findall(r"\((\s*[A-H])\s*,\s*(\d+\s*)\)", moves_string):
        moves_list.append((move[0], int(move[1])))

    return moves_list


if __name__ == '__main__':
    # test check_othello
    # intermediate_results = ['True', '(D,1), (D,3), (D,5), (D,7)']
    # game_matrix = [['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    #                ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    #                ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    #                ['O', 'O', 'O', 'B', 'O', 'B', 'O', 'O'],
    #                ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    #                ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    #                ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'],
    #                ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O']]
    # player = 'W'
    # action = ('D', 1)
    # valid_actions = [('A', 1), ('A', 8), ('H', 1), ('H', 8)]
    # check_othello(intermediate_results, game_matrix, player, action, valid_actions)
    # print('Test passed')
    moves_string = " (E,1)"
    moves_list = extract_moves(moves_string)
    print(moves_list)
    print(len(moves_list))
    # Expected output: [('C', 2), ('D', 2), ('B', 4), ('C', 5), ('C', 6), ('D', 6)]
