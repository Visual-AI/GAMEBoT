def check_surround(intermediate_results, game_matrix, current_position, action_text):
    """
    :param intermediate_results: [result1,result2,result3],
    result1: str:"Up 0, Down 0, Left 0, Right 4", result2: str, "Move Down, Move Left", result3: str, "Move Right Unsafe, Move Left Safe"
    if format error, result is "Format Error"
    :param game_matrix: 20x40 int matrix
    :param current_position: last position in the moving trace, list, [x,y]
    :param action_text: str, the action text
    :return: acc_list, total_list, format_error, valid_action, action_format_error, action_total
    """
    x, y = current_position[0], current_position[1]
    acc1, acc2, acc3, total1, total2, total3, format_error = 0, 0, 0, 1, 1, 1, 0
    valid_action, action_format_error, action_total = 0, 0, 1 # no invalid action in surround

    # check the first of the intermediate results
    result1 = intermediate_results[0]
    result1s = result1.split(",")
    result1s = [x.lower().strip() for x in result1s]
    if len(result1s) != 4:
        format_error += 1
    else:
        is_result1_correct = True
        for r in result1s:
            r = r.split(" ")
            if len(r) != 2:
                format_error += 1
                break
            if r[0] not in ["up", "down", "left", "right"]:
                format_error += 1
                break
            if not r[1].isdigit():
                format_error += 1
                break
            if r[0] == "up":
                if game_matrix[current_position[0] - 1][current_position[1]] != int(r[1]):
                    is_result1_correct = False
                    break
            elif r[0] == "down":
                if game_matrix[current_position[0] + 1][current_position[1]] != int(r[1]):
                    is_result1_correct = False
                    break
            elif r[0] == "left":
                if game_matrix[current_position[0]][current_position[1] - 1] != int(r[1]):
                    is_result1_correct = False
                    break
            elif r[0] == "right":
                if game_matrix[current_position[0]][current_position[1] + 1] != int(r[1]):
                    is_result1_correct = False
                    break
        if is_result1_correct:
            acc1 = 1

    # check the second of the intermediate results
    result2 = intermediate_results[1]
    result2s = result2.split(",")
    result2s = [x.lower().strip() for x in result2s]
    ground_truth_result2 = []
    if game_matrix[current_position[0] - 1][current_position[1]] == 0:
        ground_truth_result2.append("move up")
    if game_matrix[current_position[0] + 1][current_position[1]] == 0:
        ground_truth_result2.append("move down")
    if game_matrix[current_position[0]][current_position[1] - 1] == 0:
        ground_truth_result2.append("move left")
    if game_matrix[current_position[0]][current_position[1] + 1] == 0:
        ground_truth_result2.append("move right")
    if set(result2s) == set(ground_truth_result2):
        acc2 = 1

    # check the third of the intermediate results
    result3 = intermediate_results[2]
    result3s = result3.split(",")
    result3s = [x.lower().strip() for x in result3s]

    # write program to generate ground truth for result3
    ground_truth_result3 = []
    for dx, dy, direction in [(0, 1, "right"), (0, -1, "left"), (1, 0, "down"), (-1, 0, "up")]:
        empty_length = find_connected_empty_cells(game_matrix, x + dx, y + dy)
        if empty_length >0:
            if empty_length>=10:
                ground_truth_result3.append(f"move {direction} safe")
            else:
                ground_truth_result3.append(f"move {direction} unsafe")
    if set(result3s) == set(ground_truth_result3):
        acc3 = 1

    # check action_text
    action_text = action_text.lower().strip()
    if 'move up' in action_text or 'move right' in action_text or 'move left' in action_text or 'move down' in action_text:
        valid_action=1
    else:
        action_format_error=1
    return [acc1, acc2, acc3], [total1, total2, total3], format_error, valid_action, action_format_error, action_total


def find_connected_empty_cells(game_state, start_x, start_y):
    """
    Find connected empty cells starting from (start_x, start_y) in the game state.
    :param game_state: A matrix representing the game state.
    :param start_x: The x-coordinate of the starting position.
    :param start_y: The y-coordinate of the starting position.
    :return: The number of the connected empty cells.
    """
    connected_empty_cells = []
    visited = set()
    stack = [(start_x, start_y)]
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if game_state[x][y] == 0:
            connected_empty_cells.append((x, y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                stack.append((x + dx, y + dy))
    # print(connected_empty_cells)
    return len(connected_empty_cells)


if __name__ == "__main__":
    # intermediate_results = ["Up 0, Down 0, Left 0, Right 4", "Move Down, Move Left", "Move Right Unsafe, Move Left Safe"]
    # game_matrix = [[0 for _ in range(40)] for _ in range(20)]
    # current_position = [1,1]
    # check_surround(intermediate_results,game_matrix,current_position)

    # Example usage (based on the provided partial game state):
    game_state = [[1 for _ in range(40)] for _ in range(20)]
    game_state_cor = {
        (0, 23): 1, (0, 24): 1, (0, 25): 1, (0, 26): 1, (0, 27): 1,
        (1, 23): 0, (1, 24): 0, (1, 25): 0, (1, 26): 1, (1, 27): 1,
        (2, 23): 0, (2, 24): 0, (2, 25): 0, (2, 26): 0, (2, 27): 1,
        (3, 23): 0, (3, 24): 1, (3, 25): 0, (3, 26): 1, (3, 27): 1,
        (4, 23): 0, (4, 24): 1, (4, 25): 1, (4, 26): 1, (4, 27): 1,
    }
    for (x, y), value in game_state_cor.items():
        game_state[x][y] = value

    x, y = 0, 24  # Current position

    for dx, dy, direction in [(0, 1, "Right"), (0, -1, "Left"), (1, 0, "Down"), (-1, 0, "Up")]:
        find_connected_empty_cells(game_state, x + dx, y + dy)
