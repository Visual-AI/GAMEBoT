def get_real_position_pong(labels):
    # print(labels)
    real_position = {}
    ball_x_offset = -48
    ball_y_offset = -12
    player_y_offset = 2
    enemy_y_offset = 1
    paddle_length = 16
    total_height = 210
    real_position['ball_x'] = labels['ball_x'] + ball_x_offset
    real_position['ball_y'] = total_height-(labels['ball_y'] + ball_y_offset)
    real_position['player_x'] = 140
    real_position['player_y'] = [total_height-(labels['player_y'] + player_y_offset),
                                 total_height-(labels['player_y'] + player_y_offset)+paddle_length]
    real_position['enemy_x'] = 20
    real_position['enemy_y'] = [total_height-(labels['enemy_y'] + enemy_y_offset), total_height-(labels['enemy_y'] + enemy_y_offset)+paddle_length]
    real_position['upper_bound'] = 176
    real_position['lower_bound'] = 16
    return real_position


def get_real_position_pong_flipped(labels):
    # print(labels)
    real_position = {}
    ball_x_offset = -48
    ball_y_offset = -12
    player_y_offset = 2
    enemy_y_offset = 1
    paddle_length = 16
    total_height = 210
    real_position['ball_x'] = 160-(labels['ball_x'] + ball_x_offset)
    real_position['ball_y'] = total_height-(labels['ball_y'] + ball_y_offset)
    real_position['player_x'] = 140
    real_position['player_y'] = [total_height-(labels['enemy_y'] + enemy_y_offset), total_height-(labels['enemy_y'] + enemy_y_offset)+paddle_length]
    real_position['enemy_y'] = [total_height-(labels['player_y'] + player_y_offset),
                                 total_height-(labels['player_y'] + player_y_offset)+paddle_length]
    real_position['enemy_x'] = 20
    real_position['upper_bound'] = 176
    real_position['lower_bound'] = 16
    return real_position

