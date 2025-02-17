# import pyspiel
import numpy as np
import re
import random


class Negotiate:
    def __init__(self) -> None:
        self.step = 0
        self.history = ['Negotiate begins\n']
        self.final_proposal = []
        self.game_over = False
        self.setting = ""
        self.setting_p1 = ""
        self.setting_p2 = ""
        self.reward1 = 0
        self.reward2 = 0
        self.pool_values = []
        self.p1_values = []
        self.p2_values = []

    def game_info_str(self, role='Game'):
        if role == 'Game':
            return self.setting + ''.join(self.history)
        elif role == 'Player1':
            return self.setting_p1 + ''.join(self.history)
        elif role == 'Player2':
            return self.setting_p2 + ''.join(self.history)

        return None

    def check_intermediate_results(self, intermediate_results, actions):
        """ return correct number of results and total number of results"""

        acc = 0
        total = 0
        # check the first of the intermediate results
        if self.step != 0:
            total += 1
            if self.get_player_type() == "Player1":
                # calculate the total values for P1 in the final proposal
                value = self.p1_values[0] * self.final_proposal[0] + self.p1_values[1] * self.final_proposal[1] + \
                        self.p1_values[2] * self.final_proposal[2]
                if intermediate_results[0] == value:
                    acc += 1
            elif self.get_player_type() == "Player2":
                # calculate the total values for P2 in the final proposal
                value = self.p2_values[0] * self.final_proposal[3] + self.p2_values[1] * self.final_proposal[4] + \
                        self.p2_values[2] * self.final_proposal[5]
                if intermediate_results[0] == value:
                    acc += 1

        if actions == [-1, -1, -1, -1, -1, -1]:
            return acc, total
        else:
            total += 1
            # check the second of the intermediate results
            if self.get_player_type() == "Player1":
                # calculate the total values for P1 in the actions
                value = self.p1_values[0] * actions[0] + self.p1_values[1] * actions[1] + self.p1_values[2] * actions[2]
                if intermediate_results[1] == value:
                    acc += 1
            elif self.get_player_type() == "Player2":
                # calculate the total values for P2 in the actions
                value = self.p2_values[0] * actions[3] + self.p2_values[1] * actions[4] + self.p2_values[2] * actions[5]
                if intermediate_results[1] == value:
                    acc += 1
            return acc, total

    def new_game_state(self):
        # generate a random number between 1 and 10
        number = random.randint(8, 12)

        all_number = []
        for i in range(1, number - 2):
            for j in range(1, number - 2 - i):
                k = number - i - j
                all_number.append([i, j, k])

        pool_values = random.choice(all_number)

        value_results = []
        for i in range(100):
            for j in range(100):
                for k in range(100):
                    if i * pool_values[0] + j * pool_values[1] + k * pool_values[2] == 30:
                        value_results.append([i, j, k])

        values = random.choices(value_results, k=2)
        print(len(value_results) * len(all_number))
        self.setting = f'Pool:    {pool_values}\nP1 values: {values[0]}\nP2 values: {values[1]}\n'
        self.setting_p1 = f'Pool:    {pool_values}\nP1 values: {values[0]}\n'
        self.setting_p2 = f'Pool:    {pool_values}\nP2 values: {values[1]}\n'
        self.pool_values = pool_values
        self.p1_values = values[0]
        self.p2_values = values[1]

        re_generate = False
        for i in range(3):
            if self.p1_values[i] == 0 and self.p2_values[i] == 0:
                re_generate = True
                break
        if re_generate:
            return self.new_game_state()

        return pool_values, values[0], values[1]

    def get_player_type(self):
        if self.step % 2 == 0:
            return 'Player1'
        else:
            return 'Player2'

    def is_over(self):
        return self.game_over

    def apply_action(self, proposal):
        if self.is_over():
            print('Game is over')
            return
        if self.step > 8:
            # 20% chance of ending the game
            if random.random() < 0.2:
                self.game_over = True
                self.history.append('Game ended without agreement, each with 0 point\n')
                return
        if proposal == [-1, -1, -1, -1, -1, -1]:
            self.game_over = True
            if self.step == 0:
                self.reward1 = 0
                self.reward2 = 15
            else:
                # agree, calculate the rewards according to the final proposal
                self.reward1 = self.p1_values[0] * self.final_proposal[0] + self.p1_values[1] * self.final_proposal[1] + \
                               self.p1_values[2] * self.final_proposal[2]
                self.reward2 = self.p2_values[0] * self.final_proposal[3] + self.p2_values[1] * self.final_proposal[4] + \
                               self.p2_values[2] * self.final_proposal[5]
            self.history.append(
                'Agreement reached\nRewards: P1 ' + str(self.reward1) + ', P2 ' + str(self.reward2) + '\n')
            return

        if len(proposal) != 6 or proposal[0] + proposal[3] != self.pool_values[0] or proposal[1] + proposal[4] != \
                self.pool_values[1] or \
                proposal[2] + proposal[5] != self.pool_values[2]:
            self.game_over = True
            print('Invalid proposal', proposal)
            if self.get_player_type() == 'Player1':
                self.reward1 = -10
                self.reward2 = 0
                self.history.append(
                    f'Player1 invalid action. {proposal}\nRewards: P1 ' + str(self.reward1) + ', P2 ' + str(
                        self.reward2) + '\n')
            else:
                self.reward1 = 0
                self.reward2 = -10
                self.history.append(
                    f'Player2 invalid action. {proposal}\nRewards: P1 ' + str(self.reward1) + ', P2 ' + str(
                        self.reward2) + '\n')
            return

        self.final_proposal = proposal
        self.history.append(
            f'Round {self.step + 1} {self.get_player_type()} proposes: P1 {proposal[:3]}, P2 {proposal[3:]}\n')
        self.step = self.step + 1

    def get_algorithm_move(self):
        """Determine the next move in the Negotiate game based on game state and history."""

        def calculate_value(proposal, is_player1):
            if is_player1:
                return sum(v * p for v, p in zip(self.p1_values, proposal[:3]))
            return sum(v * p for v, p in zip(self.p2_values, proposal[3:]))

        def get_item_preferences():
            """Return items sorted by value per unit"""
            items = [(i, my_values[i] / self.pool_values[i]) for i in range(3)]
            return sorted(items, key=lambda x: x[1], reverse=True)

        is_player1 = self.get_player_type() == "Player1"
        my_values = self.p1_values if is_player1 else self.p2_values

        # First move strategy
        if self.step == 0:
            proposal = [0] * 6
            items = get_item_preferences()

            if is_player1:
                for idx, _ in items:
                    proposal[idx] = self.pool_values[idx]
                proposal[items[-1][0]] = int(0.5 * self.pool_values[items[-1][0]])
                # Fill remaining
                for i in range(3):
                    proposal[i + 3] = self.pool_values[i] - proposal[i]
            else:
                for idx, _ in items:
                    proposal[idx + 3] = int(0.9 * self.pool_values[idx])
                for i in range(3):
                    proposal[i] = self.pool_values[i] - proposal[i + 3]

            # Verify the proposal meets our minimum value requirement
            initial_value = calculate_value(proposal, is_player1)
            if initial_value < 22:  # High initial threshold
                # Adjust to take more of high-value items
                if is_player1:
                    proposal[items[0][0]] = self.pool_values[items[0][0]]
                    proposal[items[0][0] + 3] = 0
                else:
                    proposal[items[0][0] + 3] = self.pool_values[items[0][0]]
                    proposal[items[0][0]] = 0
            return proposal

        last_proposal = self.final_proposal
        current_value = calculate_value(last_proposal, is_player1)

        # Dynamic target value for accepting opponent's proposal
        base_target = 22
        round_penalty = min(4, self.step)
        accept_target_value = max(19, base_target - round_penalty)
        print(current_value)
        if self.step > 8:
            accept_target_value = 15
        # Accept if value meets dynamic target
        if current_value >= accept_target_value:
            return [-1] * 6

        # Dynamic minimum value for our proposals
        min_proposal_value = min(24, 26 - self.step)  # Starts at 24, decreases with rounds but never below 20

        # Make new proposal with concession strategy
        new_proposal = [0] * 6
        items = get_item_preferences()

        # Calculate concession rate based on round number
        concession_rate = min(0.50,
                              0.05 + (self.step * 0.05))  # Starts at 0.05, increases by 0.02 each round, caps at 0.30

        # Try up to 3 times to generate a proposal meeting our minimum value
        for attempt in range(10):
            if is_player1:
                remaining_items = self.pool_values.copy()
                for idx, value_per_unit in items:
                    if value_per_unit > 0:
                        # Take amount decreases with concession rate, but increases with each failed attempt
                        take_percentage = 0.95 - concession_rate + (attempt * 0.1)
                        take_amount = int(self.pool_values[idx] * min(1.0, take_percentage))
                        new_proposal[idx] = min(take_amount, remaining_items[idx])
                        remaining_items[idx] -= new_proposal[idx]

                # Give remaining to opponent
                for i in range(3):
                    new_proposal[i + 3] = self.pool_values[i] - new_proposal[i]
            else:
                remaining_items = self.pool_values.copy()
                for idx, value_per_unit in items:
                    if value_per_unit > 0:
                        take_percentage = 0.95 - concession_rate + (attempt * 0.1)
                        take_amount = int(self.pool_values[idx] * min(1.0, take_percentage))
                        new_proposal[idx + 3] = min(take_amount, remaining_items[idx])
                        remaining_items[idx] -= new_proposal[idx + 3]

                # Give remaining to opponent
                for i in range(3):
                    new_proposal[i] = self.pool_values[i] - new_proposal[i + 3]

            new_value = calculate_value(new_proposal, is_player1)
            if new_value >= min_proposal_value:
                print('attempt sucess')
                break

        return new_proposal


if __name__ == '__main__':
    game = Negotiate()
    pool_values, p0_values, p1_values = game.new_game_state()
    while (not game.is_over()):
        game.apply_action(game.get_algorithm_move())
    # game.apply_action([0, 0, 0, pool_values[0], pool_values[1], pool_values[2]])
    # game.apply_action([1, 3, 1, 0, 1, 0])
    # reward = game.apply_action([-1, -1, -1, -1, -1, -1])
    print(game.game_info_str())
    # print(reward)
