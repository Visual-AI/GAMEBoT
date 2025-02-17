import re


def check_intermediate_results(intermediate_results, actions, values, final_proposal, pool):
    """ return correct number of results and total number of results"""
    # Pool: [3, 4, 5]
    # P1 values: [3, 4, 1]
    # final proposal: the final proposal proposed by other player, if none, then []
    # actions: the proposal proposed by the player in this response
    # intermediate_results: [result 1->int, result 2->int], the intermediate results of the player in this response
    # return acc1, total1, acc2, total2, valid_action, invalid_action, action_format_error, action_total

    acc1, acc2, total1, total2, format_error = 0, 0, 0, 0, 0
    valid_action, invalid_action, action_format_error, action_total = 0, 0, 0, 1
    # check the first of the intermediate results
    if len(final_proposal) != 0:
        total1 = 1
        value = values[0] * final_proposal[0] + values[1] * final_proposal[1] + \
                values[2] * final_proposal[2]
        if intermediate_results[0] == value:
            acc1 = 1

        elif intermediate_results[0] == -9999:
            format_error += 1

    if actions == [-1, -1, -1, -1, -1, -1]:
        valid_action = 1
        return [acc1, acc2], [total1, total2], format_error, valid_action, invalid_action, action_format_error, action_total
    else:
        total2 = 1
        #check action_format_error
        if len(actions) != 6:
            action_format_error = 1
        # check invalid action
        elif actions[0] + actions[3] != pool[0] or actions[1] + actions[4] != pool[1] or actions[2] + actions[5] != pool[2]:
            invalid_action = 1
        else:
            valid_action = 1
            # calculate the total values in the actions
            value = values[0] * actions[0] + values[1] * actions[1] + values[2] * actions[2]
            if intermediate_results[1] == value:
                acc2 = 1
        if intermediate_results[1] == -9999:
            format_error += 1
        return [acc1, acc2], [total1, total2], format_error, valid_action, invalid_action, action_format_error, action_total


def find_intermediate_bargain(response):
    # Problem 1: in the opponent's latest proposal, the total value of the items for you and provide the result in the format [Intermediate Thinking Results 1: XXX].
    # Problem 2: When making a new proposal, Output the total value of the items for you in the new proposal in the format [Intermediate Thinking Results 2: XXX].
    response = response.lower()

    # Intermediate Thinking Results
    # Problem 1
    pattern_problem1 = r"intermediate thinking results 1: (\d+)"
    match_problem1 = re.search(pattern_problem1, response)
    if match_problem1:
        try:
            intermediate_results1 = int(match_problem1.group(1))
        except:
            intermediate_results1 = -9999
    else:
        intermediate_results1 = -9999

    # Problem 2
    pattern_problem2 = r"intermediate thinking results 2: (\d+)"
    match_problem2 = re.search(pattern_problem2, response)
    if match_problem2:
        try:
            intermediate_results2 = int(match_problem2.group(1))
        except:
            intermediate_results2 = -9999
    else:
        intermediate_results2 = -9999
    return intermediate_results1, intermediate_results2
