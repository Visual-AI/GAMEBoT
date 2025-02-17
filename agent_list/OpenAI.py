import os
# import requests
import json
import time
# get the subscription ID from the environment
from openai import AzureOpenAI


class OpenAI:

    def __init__(self, model_name, api_key, azure_endpoint, temperature=0, max_output_tokens=1000, seed=42, default_parameters=True):
        self.model_name = model_name
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-05-01-preview"
        )
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            # "top_k": top_k, ## could set via top_p (e.g., low)
            "seed": seed
        }
        self.default_parameters = default_parameters

    def get_response_text(self, prompt):

        # Send request
        for i in range(10):

            try:
                if self.default_parameters:
                    response = self.client.chat.completions.create(
                        model=self.model_name,  # model = "deployment_name".
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=self.config['max_output_tokens'],
                        seed=self.config['seed']
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model_name,  # model = "deployment_name".
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                        temperature=self.config['temperature'],
                        #top_k=self.config['top_k'], ## could set via top_p (e.g., low)
                        max_tokens=self.config['max_output_tokens'],
                        seed=self.config['seed']
                    )
                response = response.choices[0].message.content
                return response

            except Exception as e:
                print(f"Request failed for OpenAI: {e}")
                time.sleep(10 * (i + 1))
                continue
        print("Failed to generate content - returning None")
        return f'None - failed to generate content after 10 tries'


if __name__ == '__main__':
    import keys

    client = AzureOpenAI(
        azure_endpoint="https://llambda-us.openai.azure.com",
        api_key=keys.openai_key_lambda,
        api_version="2024-05-01-preview"
    )
    prompt = '''
    You are an expert poker player playing Texas Hold'em.

**Game Rules**
1. Texas Hold'em is a popular poker game played with two private cards and five community cards.
2. Both players start with 100 chips to bet, and the player with the most chips at the end of the game wins. If your chips drop to 0, you lose the game.
3. The game consists of four betting rounds: pre-flop, flop, turn, and river. At flop, turn, and river round, three, one, and one community cards are revealed, respectively.
4. At each round, players can choose to Fold, Check and Call, Raise Half Pot, Raise Full Pot, All in.
    - Fold: Discard your hand, forfeiting any potential winning of the pot and not committing any more chips.
    - Check and Call: If no bet has been made, a player can choose to 'Check', which means they do not wish to make a bet, and play passes to the next player. When a player chooses to 'Call', they are committing an amount of chips equal to the previous player's bet or raise to match it.
    - Raise Half Pot: Increase the bet to half of the current pot size.
    - Raise Full Pot: Increase the bet to the current pot size.
    - All in: Bet all of your remaining chips.
5. The player with the best five-card hand wins the pot.
6. The hands are ranked from highest to lowest: Royal Flush, Straight Flush, Four of a Kind, Full House, Flush, Straight, Three of a Kind, Two Pair, One Pair, High Card.
    Rank 1 - Royal Flush: A, K, Q, J, 10 all of the same suit.
    Rank 2 - Straight Flush: Five consecutive cards of the same suit. Higher top card wins.
    Rank 3 - Four of a Kind: Four cards of the same rank. Higher rank wins; if same, compare fifth card.
    Rank 4 - Full House: Three cards of one rank and two cards of another rank. Higher three-card rank wins; if same, compare the two-card rank.
    Rank 5 - Flush: Five non-consecutive cards of the same suit. Compare the highest card, then the second-highest, and so on.
    Rank 6 - Straight: Five consecutive cards of different suits. Higher top card wins.
    Rank 7 - Three of a Kind: Three cards of the same rank. Higher rank wins.
    Rank 8 - Two Pair: Two cards of one rank and two cards of another rank. Compare the higher pair first, then the lower pair, and then the fifth card.
    Rank 9 - One Pair: Two cards of the same rank. Compare the pair first, then the highest non-paired card, then the second highest, and so on.
    Rank 10 - High Card: If no hand can be formed, the highest card wins. If the highest cards are the same, compare the second highest, and so on. Cards are ranked from A, K, ... to 3, 2, where A is the highest.

**Input**
You will receive the following inputs:
* Your two private cards.
* The revealed community cards.
* Your chips in the pot.
* Your opponent's chips in the pot.

**Output**
Provide your chosen action strictly following the step-by-step process:

1. **Strategic Analysis**
Based on your two private cards and the revealed community cards, evaluate your winning probability.
* At pre-flop: the winning probabilities of given private hand are listed as below,
[AA:84.9%, KK:82.1%, QQ:79.6%, JJ:77.1%, TT:74.7%, 99:71.7%, 88:68.7%, 77:65.7%, 66:62.7%, 55:59.6%, 44:56.3%, 33:52.9%, 22:49.3%, AKs:66.2%, AKo:64.5%, AK  64.9%, AQ:64.0%, AJ:63.0%, AT:62.0%, A9:60.0%, A8:58.9%, A7:57.7%, A6:56.4%, A5:56.3%, A4:55.3%, A3:54.5%, A2:53.6%, KQs:62.4%, KQo:60.5%, KQ:60.9%, KJ:59.9%, KT:59.0%, K9:57.0%, K8:55.0%, K7:54.0%, K6:52.9%, K5:51.9%, K4:50.9%, K3:50%:3, K2:49.1%, QJs:59.1%, QJo:57.0%, QJ:57.4%, QT:56.5%, Q9:54.5%, Q8:52.6%, Q7:50.5%, Q6:49.7%, Q5:48.6%, Q4:47.7%, Q3:46.8%, Q2:45.9%, JTs:56.2%, JTo:53.8%, JT:54.4%, J9:52.3%, J8:50.4%, J7:48.4%, J6:46.4%, J5:45.6%, J4:44.6%, J3:43.8%, J2:42.8%, T9s:52.4%, T9o:49.8%, T9:50.5%, T8:48.5%, T7:46.5%, T6:44.6%, T5:42.6%, T4:41.8%, T3:40.9%, T2:40.1%, 98s:48.9%, 98o:46.1%, 98:46.8%, 97:44.8%, 96:42.9%, 95:40.9%, 94:38.9%, 93:38.3%, 92:37.4%, 87s:45.7%, 87o:42.7%, 87:43.4%, 86:41.5%, 85:39.6%, 84:37.5%, 83:35.6%, 82:35.0%, 76s:42.9%, 76o:39.7%, 76:40.4%, 75:38.5%, 74:36.5%, 73:34.6%, 72:32.6%, 72o:31.7%, 65s:40.3%, 65o:37.0%, 65:37.8%, 64:35.9%, 63:34.0%, 62:32.0%, 54s:38.5%, 54o:35.1%, 54:36.0%, 53:34.0%, 52:32.1%, 43s:35.7%, 43o:32.1%, 43:33.0%, 42:31.1%, 32s:33.1%, 32o:29.3%, 32:30.2%]
where XXo means unsuited two cards, and XXs represents two suited cards. T means 10.
Judge which is your private hand and output the corresponding winning probability. If the winning probability is larger than 55%, you can consider to raise or all in. If the winning probability is less than 45%, you can consider to fold. If the winning probability is between 45% and 55%, you can consider to check and call.
* At flop, turn, and river round, first output your best five-card hand and your hand ranking according to the game rules. If your hand ranks equal or higher than Rank 8 - Two Pair, you can consider to raise or all in. If you are rank 10, and your highest private card is lower than K, you can consider to fold. Otherwise, you can consider to check and call.

Consider the following factors to determine your next action:
    * Your current hand ranking and the probability of improving it.
    * The community cards and potential winning combinations.
    * Your opponents' possible hands and betting patterns.
    * The pot odds and implied odds.
    * Your position at the table and the betting round.
    * The stack sizes of you and your opponents.

2. **Conclusion**
Based on your previous analysis, clearly state your decision and reason.

3. **Chosen Action**
    * Only output the chosen action. Do not include any other words.
    * The format is: "Fold", "Check and Call", "Raise Half Pot", "Raise Full Pot", "All in".

    '''
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # model = "deployment_name".
        messages=[
            # {"role": "system", "content": "You are a helpful assistant."},
            # {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
            # {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
            {"role": "user", "content": prompt},
        ]
    )
    response = response.choices[0].message.content
    print(response)