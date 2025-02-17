import re

def check_pong(intermediate_results, ball_x1, ball_y1, ball_x2, ball_y2, action_text):
    """
    Check the intermediate results of the pong game.
    :param intermediate_results: [result1->str, result2->float], for example, ['right up', 100.0], res1: if format error, str='Format Error'; res2: if format error, float=-9999
    :param ball_x1:
    :param ball_y1:
    :param ball_x2:
    :param ball_y2:
    :param action_text: str, the action text
    :return: [acc1, acc2], [total1, total2], format_error, valid_action, action_format_error, action_total
    """
    acc_list = [0, 0]
    total_list = [1, 1]
    result1 = intermediate_results[0]
    result2 = intermediate_results[1]
    format_error = 0
    valid_action, action_format_error, action_total = 0, 0, 1 # no invalid action in pong

    if 'move up' in action_text.lower() or 'move down' in action_text.lower() or 'stay still' in action_text.lower():
        valid_action=1
    else:
        action_format_error+=1
    # check the first of the intermediate results
    if ball_y1==222 or ball_y2==222:
        return [0, 0], [0, 0], 0, 0, 0, 0, 0
    if ball_x2 > ball_x1 and ball_y2 > ball_y1:
        # ball is moving right and up
        ground_truth1 = "right up"
    elif ball_x2 > ball_x1 and ball_y2 < ball_y1:
        # ball is moving right and down
        ground_truth1 = "right down"
    elif ball_x2 < ball_x1 and ball_y2 > ball_y1:
        # ball is moving left and up
        ground_truth1 = "left up"
    elif ball_x2 < ball_x1 and ball_y2 < ball_y1:
        # ball is moving left and down
        ground_truth1 = "left down"
    else:
        return [0, 0], [0, 0], 0, 0, 0, 0, 0
    if ground_truth1 == result1.lower().strip():
        acc_list[0] += 1
    elif result1 not in ["right up", "right down", "left up", "left down"] and total_list[0] != 0:
        format_error += 1
    # check the second of the intermediate results
    # print(ball_x1, ball_y1, ball_x2, ball_y2)
    # print(predict_ball_y_with_bounce(ball_x1, ball_y1, ball_x2, ball_y2))
    if 'left' in ground_truth1:
        total_list[1] = 0
        return acc_list, total_list, format_error, valid_action, 0, action_format_error, action_total
    
    if type(result2) != float:
        format_error += 1
    elif abs(result2 + 9999) < 0.1:
        format_error += 1
    elif abs(result2 - predict_ball_y_with_bounce(ball_x1, ball_y1, ball_x2, ball_y2)) < 0.1:
        acc_list[1] += 1


    return acc_list, total_list, format_error, valid_action, 0, action_format_error, action_total


def predict_ball_y_with_bounce(ball_x1, ball_y1, ball_x2, ball_y2):
    """
    Predicts the y-coordinate of a ball when its x-coordinate is target_x,
    considering potential bounces off the upper and lower walls.

    Args:
      ball_x1: X-coordinate of the first point.
      ball_y1: Y-coordinate of the first point.
      ball_x2: X-coordinate of the second point.
      ball_y2: Y-coordinate of the second point.
      target_x: The target x-coordinate for which to predict the y-coordinate.
      lower_wall_y: The y-coordinate of the lower wall.
      upper_wall_y: The y-coordinate of the upper wall.

    Returns:
      The predicted y-coordinate at the target x-coordinate, or None if the
      ball doesn't cross the target x-coordinate within a single bounce.
    """
    lower_wall_y = 16
    upper_wall_y = 176
    target_x = 140

    # Function to calculate y-coordinate based on slope and intercept
    def calculate_y(x, slope, y_intercept):
        return slope * x + y_intercept

    # Calculate initial slope and y-intercept
    if ball_x1 == ball_x2:
        return None  # Ball doesn't move horizontally

    slope = (ball_y2 - ball_y1) / (ball_x2 - ball_x1)
    y_intercept = ball_y1 - (slope * ball_x1)

    # Check if the ball hits a wall within the given trajectory
    # (before reaching target_x)

    # --- Check for bounce off lower wall ---
    if ball_y1 > ball_y2:  # Ball is moving downwards
        bounce_x = (lower_wall_y - y_intercept) / slope
        if ball_x1 < bounce_x < target_x:
            # Ball bounces off lower wall
            # print("Bounce off lower wall")
            remaining_x = target_x - bounce_x
            res = calculate_y(remaining_x, -slope, lower_wall_y)  # Reflected trajectory
            if 16 <= res <= 176:
                return res
            else:
                # print('keep bouncing')
                bounce_x = (upper_wall_y - lower_wall_y) / (-slope) + bounce_x
                remaining_x = target_x - bounce_x
                res = calculate_y(remaining_x, slope, upper_wall_y)  # Reflected trajectory
                return res
    # --- Check for bounce off upper wall ---
    elif ball_y1 < ball_y2:  # Ball is moving upwards
        bounce_x = (upper_wall_y - y_intercept) / slope
        if ball_x1 < bounce_x < target_x:
            # Ball bounces off upper wall
            remaining_x = target_x - bounce_x
            res = calculate_y(remaining_x, -slope, upper_wall_y)  # Reflected trajectory
            if 16 <= res <= 176:
                return res
            else:
                bounce_x = (lower_wall_y - upper_wall_y) / (-slope) + bounce_x
                remaining_x = target_x - bounce_x
                res = calculate_y(remaining_x, slope, lower_wall_y)
                return res
    # --- No bounce, calculate y directly ---
    res = calculate_y(target_x, slope, y_intercept)
    return res


def find_intermediate_and_action_pong(response):

    response = response.lower()
    # Intermediate Thinking Results
    # Problem 1
    pattern_problem1 = re.compile(r"intermediate thinking results 1: (.*?)\]")
    match_problem1 = re.search(pattern_problem1, response)
    if match_problem1:
        intermediate_results1 = match_problem1.group(1).strip()
    else:
        intermediate_results1 = 'Format Error'

    # Problem 2
    pattern_problem2 = re.compile(r"intermediate thinking results 2: (\d+(\.\d+)?)")
    match_problem2 = re.search(pattern_problem2, response)
    if match_problem2:
        intermediate_results2 = float(match_problem2.group(1).strip())
    else:
        intermediate_results2 = -9999

    # Action
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
        action = 'move up'
    elif 'move down' in action_text.lower():
        action = 'move down'
    elif 'stay still' in action_text.lower():
        action = 'stay still'
    else:
        action = ''
        
    return [intermediate_results1, intermediate_results2], action