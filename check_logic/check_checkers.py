import re


def check_checkers(intermediate_results, game_matrix, player, action, valid_actions):
    # Problem1:
    #     Output all moves that give you a new king piece. The format is "[Intermediate Thinking Results 1: (X,X)->(X,X), ...]". If no such a move, output "[Intermediate Thinking Results 1: None]".
    #     Black should try to reach row 0. White should try to reach row 7.
    #     Problem2:
    #     No worthless die: Example: Consider a game board [(0,5):_, (0,3):_, (1,4):w, (2,3):_, (3,2):b]. For White, move from (1,4)->(2,3) is a bad move, since it would be captured by (3,2):b immediately, but no capture back since (0,5) and (0,3) are both empty.
    #     * Output all of the bad moves that lead to a worthless die. The format is "[Intermediate Thinking Results 2: (X,X)->(X,X), ...]". If no such a move, output "[Intermediate Thinking Results 2: None]".
    #     Problem3:
    # 	For example, if the game board is [(1,4):w, (2,7):_, (3,4):w, (3,6):w, (4,5):_, (5,4):b, (5,6):b, (6,7):b, empty else] advancing the black piece (5,6) -> (4,5) forces the white piece (3,4) to capture this black piece and become (5:6):w. Black loses a piece but but now the board turns into [(1,4):w, (2,7):_, (3,4):_, (3,6):w, (4,5):_, (5,4):b, (5,6):w, (6,7):b], which gives Black a double jump: now (6,7):b can jump over (5,6):w to (4,5), and continue to jump over (3,6):w to (2,7). So Black sacrifice one piece to capture two White's pieces.
    # 	For Three-for-One or Three-for-Two Shot, they work on the same principles.
    # 	* Output all moves that can create a Two-for-One Shot in the format "[Intermediate Thinking Results 3: (X,X)->(X,X), ...]". If no such a move, output "[Intermediate Thinking Results 3: None]".
    """
        :param intermediate_results: [Str,Str,Str],
            result1 str="(X,X)->(X,X), ...", or "None", or if format error, str='Format Error',
            result2 str="(X,X)->(X,X), ...", or "None", or if format error, str='Format Error',
        :param game_matrix: 'w' for white, 'b' for black, '_' for empty, 'W' for white king, 'B' for black king
        :param player: 'w' or 'b'
        :param action: str, '(2, 1)->(3, 0)' for example
        :param valid_actions: list of valid actions, ['(2, 1)->(3, 0)', '(2, 1)->(3, 2)'] for example
        :return: [tp, fp, tn, fn], [tp, fp, tn, fn], [tp, fp, tn, fn], format_error, valid_action, invalid_action, action_format_error, action_total
    """

    true_positive1, false_positive1, true_negative1, false_negative1, mm1 = 0, 0, 0, 0
    true_positive2, false_positive2, true_negative2, false_negative2, mm2 = 0, 0, 0, 0
    # true_positive3, false_positive3, true_negative3, false_negative3 = 0, 0, 0, 0

    format_error = 0
    valid_action, invalid_action, action_format_error, action_total = 0, 0, 0, 1
    opponent = 'w' if player == 'b' else 'b'
    action = action.replace(' ', '')
    valid_actions = [valid_action.replace(' ', '') for valid_action in valid_actions]
    if len(find_coordinates(action)) != 4:
        action_format_error = 1
    elif action not in valid_actions:
        invalid_action = 1
    else:
        valid_action = 1

    # check the first of the intermediate results
    result1, result2 = intermediate_results[0].strip(), intermediate_results[1].strip()
    # calculate the ground truth
    # calculate ground_truth1
    ground_truth1 = []  # tuple of 4 int
    for valid_action in valid_actions:
        valid_action = find_coordinates(valid_action)[0]
        if player == 'b':
            if valid_action[0] != 0 and valid_action[2] == 0:
                ground_truth1.append(valid_action)
        if player == 'w':
            if valid_action[0] != 7 and valid_action[2] == 7:
                ground_truth1.append(valid_action)
    # calculate ground_truth2
    ground_truth2 = []  # tuple of 4 int
    for valid_action in valid_actions:
        valid_action = find_coordinates(valid_action)[0]
        if is_worthless_move(game_matrix, (valid_action[0], valid_action[1]), (valid_action[2], valid_action[3]),
                             player, opponent):
            ground_truth2.append(valid_action)

    if result1 == 'Format Error':
        format_error += 1
    else:
        all_moves1 = find_coordinates(result1)
        if len(all_moves1) == 0:
            if len(ground_truth1) == 0:
                true_negative1 = 1
            else:
                false_negative1 = 1
        else:
            if set(all_moves1) == set(ground_truth1):
                true_positive1 = 1
            else:
                if len(ground_truth1) == 0:
                    false_positive1 = 1
                else:
                    mm1 = 1

    # check the second of the intermediate results
    if result2 == 'Format Error':
        format_error += 1
    else:
        all_moves2 = find_coordinates(result2)
        if len(all_moves2) == 0:
            if len(ground_truth2) == 0:
                true_negative2 = 1
            else:
                false_negative2 = 1
        else:
            if set(all_moves2) == set(ground_truth2):
                true_positive2 = 1
            else:
                if len(ground_truth2) == 0:
                    false_positive2 = 1
                else:
                    mm2 = 1

    return [true_positive1, false_positive1, true_negative1, false_negative1, mm1], [true_positive2, false_positive2, true_negative2, false_negative2, mm2], format_error, valid_action, invalid_action, action_format_error, action_total


def find_coordinates(action_text):
    pattern = r"\((\d),\s*(\d)\)\s*->\s*\((\d),\s*(\d)\)"

    match_list = re.findall(pattern, action_text)
    result_list = []
    for match in match_list:
        coordinates = tuple([int(group) for group in match if group is not None])
        result_list.append(coordinates)
    return result_list


def is_worthless_move(board, origin_pos, new_pos, player, opponent):
    """Checks if a move to new_pos would be immediately captured with no recapture."""
    if new_pos[0] == 0 or new_pos[0] == 7 or new_pos[1] == 0 or new_pos[1] == 7:
        return False
    if origin_pos[0] - new_pos[0] != 1 and origin_pos[0] - new_pos[0] != -1:
        return False
    if opponent == 'w':  # move from row 0 to row 7
        row_col_diff_list_oppo = [(-1, 1), (-1, -1)]
        row_col_diff_list_player = [(1, 1), (1, -1)]
    else:
        row_col_diff_list_oppo = [(1, 1), (1, -1)]
        row_col_diff_list_player = [(-1, 1), (-1, -1)]
    king_col_diff_list = [(-1, 1), (-1, -1), (1, 1), (1, -1)]

    res = False
    for row_diff, col_diff in row_col_diff_list_oppo:

        capture_row, capture_col = new_pos[0] + row_diff, new_pos[1] + col_diff
        if 0 <= capture_row <= 7 and 0 <= capture_col <= 7 and board[capture_row][capture_col] == opponent:
            opponent_jump_row, opponent_jump_col = (new_pos[0] - row_diff, new_pos[1] - col_diff)
            # Check for immediate recapture possibility from opponent_jump_pos

            if (not any(
                    0 <= opponent_jump_row + r <= 7 and 0 <= opponent_jump_col <= 7 and board[opponent_jump_row + r][
                        opponent_jump_col + c] == player for r, c in row_col_diff_list_player)) and not any(
                0 <= opponent_jump_row + r <= 7 and 0 <= opponent_jump_col + c <= 7 and board[opponent_jump_row + r][
                    opponent_jump_col + c] == player.upper() for r, c in king_col_diff_list):
                res = True  # Worthless move

    for row_diff, col_diff in king_col_diff_list:
        capture_row, capture_col = new_pos[0] + row_diff, new_pos[1] + col_diff
        if 0 <= capture_row <= 7 and 0 <= capture_col <= 7 and board[capture_row][capture_col] == opponent.upper():
            # opponent future jump pos
            opponent_jump_row, opponent_jump_col = (new_pos[0] - row_diff, new_pos[1] - col_diff)
            if (not any(
                    0 <= opponent_jump_row + r <= 7 and 0 <= opponent_jump_col <= 7 and board[opponent_jump_row + r][
                        opponent_jump_col + c] == player for r, c in row_col_diff_list_player)) and not any(
                0 <= opponent_jump_row + r <= 7 and 0 <= opponent_jump_col + c <= 7 and board[opponent_jump_row + r][
                    opponent_jump_col + c] == player.upper() for r, c in king_col_diff_list):
                res = True  # Worthless move
    return res


def is_two_for_one_shot(board, origin_pos, new_pos, player, opponent):
    """

    :param board: 8x8 matrix representing the game board, 'w' for white, 'b' for black, '_' for empty, 'W' for white king, 'B' for black king
    :param origin_pos: (x, y)
    :param new_pos: (x, y)
    :param player: 'w' or 'b'
    :param opponent: 'w' or 'b'
    :return: true if the move can create a two-for-one shot, false otherwise
    """

    """
    Checks if a move creates a two-for-one shot in Checkers.

    Args:
        board: 8x8 matrix representing the game board.
        origin_pos: Tuple (row, col) of the piece's starting position.
        new_pos: Tuple (row, col) of the piece's destination position.
        player: 'w' or 'b' representing the current player.
        opponent: 'w' or 'b' representing the opponent.

    Returns:
        True if the move creates a two-for-one shot, False otherwise.
    """

    # Create a copy of the board to simulate the move
    temp_board = [row[:] for row in board]  # Deep copy
    temp_board[new_pos[0]][new_pos[1]] = temp_board[origin_pos[0]][origin_pos[1]]
    temp_board[origin_pos[0]][origin_pos[1]] = '_'

    # Check for possible captures by the opponent after the move
    capture_moves = find_all_captures(temp_board, opponent, player)

    if not capture_moves:
        return False

    # Simulate the opponent's capture and check for double captures by the player
    for capture_move in capture_moves:
        capture_start = capture_move[0]
        capture_end = capture_move[-1]

        # Simulate opponent capture
        sim_board = [row[:] for row in temp_board]
        sim_board[capture_end[0]][capture_end[1]] = sim_board[capture_start[0]][capture_start[1]]

        # Clear captured pieces
        for i in range(1, len(capture_move)):
            sim_board[capture_move[i - 1][0] + (capture_move[i][0] - capture_move[i - 1][0]) // 2][
                capture_move[i - 1][1] + (capture_move[i][1] - capture_move[i - 1][1]) // 2] = '_'

        sim_board[capture_start[0]][capture_start[1]] = '_'

        double_captures = find_all_captures(sim_board, player, opponent)

        for double_capture in double_captures:
            if len(double_capture) > 2:  # Two or more captures for player
                return True

    return False


def find_all_captures(board, player_turn, opponent):
    captures = []
    for r in range(8):
        for c in range(8):
            if board[r][c].lower() == player_turn:
                piece_captures = find_captures_for_piece(board, (r, c), player_turn, opponent)
                for capture in piece_captures:
                    captures.append(capture)
    return captures


def find_captures_for_piece(board, pos, player_turn, opponent):
    # ... (implementation of find_captures_for_piece, as in a complete checkers game logic)
    # This function needs to recursively find all possible jump sequences for a given piece.
    # Refer to a complete checkers implementation for this part.
    pass  # Replace with actual implementation


if __name__ == '__main__':
    action_text = "(2,3) -> (4, 5)"
    find_coordinates(action_text)
    parts = {(0, 5): '_', (0, 3): '_', (1, 4): 'w', (2, 3): '_', (3, 2): 'b'}
    game_matrix = [['_' for _ in range(8)] for _ in range(8)]
    for index, value in parts.items():
        game_matrix[index[0]][index[1]] = value
    print(is_worthless_move(game_matrix, (1, 4), (2, 3), 'w', 'b'))  # True
