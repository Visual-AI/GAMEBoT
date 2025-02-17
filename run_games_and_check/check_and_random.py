import numpy as np
import random
from itertools import combinations
import re


# Texas
def check_intermediate_texas(intermediate_results, private, public):
    acc_list = [0, 0]
    total_list = [0, 0]
    format_error = 0

    intermediate_results1, intermediate_results2 = intermediate_results
    intermediate1_gts = {'AA':84.9, 'KK':82.1, 'QQ':79.6, 'JJ':77.1, 'TT':74.7, '99':71.7, '88':68.7, '77':65.7, '66':62.7, '55':59.6,
                        '44':56.3, '33':52.9, '22':49.3, 'AKs':66.2, 'AKo':64.5, 'AK':64.9, 'AQ':64.0, 'AJ':63.0, 'AT':62.0, 'A9':60.0,
                        'A8':58.9, 'A7':57.7, 'A6':56.4, 'A5':56.3, 'A4':55.3, 'A3':54.5, 'A2':53.6, 'KQs':62.4, 'KQo':60.5, 'KQ':60.9,
                        'KJ':59.9, 'KT':59.0, 'K9':57.0, 'K8':55.0, 'K7':54.0, 'K6':52.9, 'K5':51.9, 'K4':50.9, 'K3':50.3, 'K2':49.1, 
                        'QJs':59.1, 'QJo':57.0, 'QJ':57.4, 'QT':56.5, 'Q9':54.5, 'Q8':52.6, 'Q7':50.5, 'Q6':49.7, 'Q5':48.6, 'Q4':47.7, 
                        'Q3':46.8, 'Q2':45.9, 'JTs':56.2, 'JTo':53.8, 'JT':54.4, 'J9':52.3, 'J8':50.4, 'J7':48.4, 'J6':46.4, 'J5':45.6, 
                        'J4':44.6, 'J3':43.8, 'J2':42.8, 'T9s':52.4, 'T9o':49.8, 'T9':50.5, 'T8':48.5, 'T7':46.5, 'T6':44.6, 'T5':42.6, 
                        'T4':41.8, 'T3':40.9, 'T2':40.1, '98s':48.9, '98o':46.1, '98':46.8, '97':44.8, '96':42.9, '95':40.9, '94':38.9, 
                        '93':38.3, '92':37.4, '87s':45.7, '87o':42.7, '87':43.4, '86':41.5, '85':39.6, '84':37.5, '83':35.6, '82':35.0, 
                        '76s':42.9, '76o':39.7, '76':40.4, '75':38.5, '74':36.5, '73':34.6, '72':32.6, '72o':31.7, '65s':40.3, '65o':37.0,
                        '65':37.8, '64':35.9, '63':34.0, '62':32.0, '54s':38.5, '54o':35.1, '54':36.0, '53':34.0, '52':32.1, '43s':35.7,
                        '43o':32.1, '43':33.0, '42':31.1, '32s':33.1, '32o':29.3, '32':30.2}
    intermediate1_gts = {k: float(v) for k, v in intermediate1_gts.items()}
    rank_order = "23456789TJQKA"
    private_cards = private.split(', ')
    private_card1, private_card2 = private_cards
    private_suit1, private_rank1 = private_card1.split(' ')[0], private_card1.split(' ')[1]
    private_suit2, private_rank2 = private_card2.split(' ')[0], private_card2.split(' ')[1]
    if private_rank1 == '10':
        private_rank1 = 'T'
    if private_rank2 == '10':
        private_rank2 = 'T'

    if len(public) == 0:  # inter 1
        if intermediate_results1 == -9999:
            format_error += 1
            total_list[0] += 1
            return acc_list, total_list, format_error
        if rank_order.index(private_rank1) > rank_order.index(private_rank2):
            high_rank, low_rank = private_rank1, private_rank2
        else:
            high_rank, low_rank = private_rank2, private_rank1
        if private_suit1 == private_suit2:
            suited = 's'
        else:
            suited = 'o'
        private_shape_0 = high_rank + low_rank + suited
        flag = False
        if private_shape_0 in intermediate1_gts.keys():
            inter1_gt_0 = intermediate1_gts[private_shape_0]
            if intermediate_results1 - inter1_gt_0 < 0.1:
                flag = True
            # print(intermediate_results1, inter1_gt_0)
        private_shape_1 = high_rank + low_rank
        if private_shape_1 in intermediate1_gts.keys():
            inter1_gt_1 = intermediate1_gts[private_shape_1]
            if intermediate_results1 - inter1_gt_1 < 0.1:
                flag = True
            # print(intermediate_results1, inter1_gt_1)
        total_list[0] += 1
        if flag:
            acc_list[0] += 1
    
    else:  # inter 2
        if intermediate_results2 == -9999:
            format_error += 1
            total_list[1] += 1
            return acc_list, total_list, format_error
        # print(private, public)
        private_cards = private.split(', ')
        public_cards = public.split(', ')
        private_hand = [(card.split()[0], card.split()[1]) for card in private_cards]
        public_hand = [(card.split()[0], card.split()[1]) for card in public_cards]
        # Generate combinations with 3, 4, or 5 public cards
        best_rank = 10  # Start with the worst possible rank
        for combination in combinations(private_hand + public_hand, 5):  # 2 private + r public cards
            rank = evaluate_hand(combination)
            if rank < best_rank:
                best_rank = rank
        # print(intermediate_results2, best_rank, private, public)
        intermediate_results2 = int(intermediate_results2)
        total_list[1] += 1
        if best_rank == intermediate_results2:
            acc_list[1] += 1

    return acc_list, total_list, format_error


def evaluate_hand(hand):
    # print(hand)
    card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    values = [card[1] for card in hand]
    suits = [card[0] for card in hand]
    value_counts = {v: values.count(v) for v in values}
    # print(value_counts)
    suit_counts = {s: suits.count(s) for s in suits}
    
    numeric_values = sorted([card_values[v] for v in values], reverse=True)
    # print(numeric_values)
    
    flush = any(count >= 5 for count in suit_counts.values())
    
    straight = False
    for i in range(len(numeric_values) - 4):
        if all(numeric_values[i] - j == numeric_values[i + j] for j in range(5)):
            straight = True
            break
    
    if flush and straight:
        return 2  # Straight Flush
    elif flush:
        return 5  # Flush
    elif straight:
        return 6  # Straight
    
    counts = sorted(value_counts.values(), reverse=True)
    if counts[0] == 4:
        return 3  # Four of a Kind
    elif counts[0] == 3 and counts[1] >= 2:
        return 4  # Full House
    elif counts[0] == 3:
        return 7  # Three of a Kind
    elif counts[0] == 2 and counts[1] == 2:
        return 8  # Two Pair
    elif counts[0] == 2:
        return 9  # One Pair
    
    return 10  # High Card


def find_intermediate_texas(response):
    # Problem 1: Judge which is your private hand and output the corresponding winning probability in the format [Intermediate Thinking Results 1: XXX].
    # Problem 2: At flop, turn, and river round, first analyse your best five-card hand and output your hand ranking according to the game rules in the format [Intermediate Thinking Results 2: XXX].
    response = response.lower()

    # Intermediate Thinking Results
    # Problem 1
    pattern_problem1 = r"intermediate thinking results 1: (\d+(\.\d+)?)%"
    match_problem1 = re.search(pattern_problem1, response)
    if match_problem1:
        intermediate_results1 = float(match_problem1.group(1))
    else:
        intermediate_results1 = -9999

    # Problem 2
    pattern_problem2 = r"intermediate thinking results 2: (\d+)"
    match_problem2 = re.search(pattern_problem2, response)
    if match_problem2:
        intermediate_results2 = int(match_problem2.group(1))
    else:
        intermediate_results2 = -9999
    return intermediate_results1, intermediate_results2
            
    
def random_texas(mask):
    available = [idx for idx, action in enumerate(mask) if action == 1]
    action = random.choice(available)
    intermediate_results = [-1, -1]
    
    return intermediate_results, action


# Connect4
def random_connect4(indices_of_ones):
    action = random.choice(indices_of_ones)
    intermediate_results = [-1, -1]
    
    return intermediate_results, action


