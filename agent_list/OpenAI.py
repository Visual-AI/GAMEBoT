import os
# import requests
import json
import time
# get the subscription ID from the environment
from openai import AzureOpenAI
import openai


class AzOpenAI:

    def __init__(self, model_name, api_key, azure_endpoint, temperature=0, max_output_tokens=1000, seed=42,
                 default_parameters=True):
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
                        # top_k=self.config['top_k'], ## could set via top_p (e.g., low)
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


class OpenAI:

    def __init__(self, model_name, api_key, temperature=0, max_output_tokens=4096, seed=42, default_parameters=True):
        openai.api_key = api_key
        self.model_name = model_name
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            # "top_k": top_k, ## could set via top_p (e.g., low)
            "seed": seed
        }
        self.default_parameters = default_parameters

    def get_response_text(self, prompt, reasoning_effort="high"):

        # Send request
        for i in range(10):

            try:
                if self.default_parameters:
                    if self.model_name.startswith('o3'):
                        response = openai.chat.completions.create(
                            model=self.model_name,  # Specify the o3-mini model
                            messages=[
                                {"role": "user", "content": prompt},
                            ],
                            extra_body={"reasoning_effort": reasoning_effort},
                            # max_completion_tokens=self.config['max_output_tokens'],
                        )
                    else:
                        response = openai.chat.completions.create(
                            model=self.model_name,  # Specify the o3-mini model
                            messages=[
                                {"role": "user", "content": prompt},
                            ],
                            # max_completion_tokens=self.config['max_output_tokens'],
                        )
                        print(response)
                    return response.choices[0].message.content
                else:
                    response = openai.chat.completions.create(
                        model=self.model_name,  # model = "deployment_name".
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                        temperature=self.config['temperature'],
                        # top_k=self.config['top_k'], ## could set via top_p (e.g., low)
                        max_completion_tokens=self.config['max_output_tokens'],
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

    # openai.api_key = keys.openai_key
    # models = openai.models.list()
    #
    # print("Available OpenAI Models:")
    # for model in models.data:
    #     print(f"- {model.id}")

    agent = OpenAI('o1-preview', keys.openai_key)
    prompt = '''
You are an expert player of the game Connect Four.

**Game Rules**
1. The game is played on a 6x7 grid by two players, X and O.
2. X typically plays first, then players alternate turns to drop their pieces.
3. The pieces can only be dropped at the lowest available space within the column.
4. The first player to connect four of their pieces in a row wins the game.
5. The connection can be horizontal, vertical, or diagonal.

**Input**
You will receive a state matrix representing the current game board:
* Empty space: _
* Player 1's piece: X
* Player 2's piece: O
The coordinates are zero-based indexing. For example, "(0,4):X" represents Player 1 has a piece on Row 0, Column 4. Row 0 is the lowest and Row 5 is the highest.

**Output**
Provide your chosen move. Your performance will be assessed on both the intermediate thinking results and the final decision. Follow the thinking process:

1. **Observations**
Based on the current game state, provide the following observations:
    * Where are your pieces located?
    * Where are your opponent's pieces located?
    * Check for all horizontal, vertical, or diagonal lines: are there any potential winning moves to form 4 in a row for you or your opponent? 
    Output all of the winning moves for you in the format "[Intermediate Thinking Results 1: (X,X), (X,X), ...]". If none, output "[Intermediate Thinking Results 1: None]". 
    Output all of the winning moves for your opponent in the format "[Intermediate Thinking Results 2: (X,X), (X,X), ...]". If none, output "[Intermediate Thinking Results 2: None]". 
    For example, assume you are X player and would like to check for one of the valid move (3,2),
        Current Game Board: 
        (5,0):_ (5,1):_ (5,2):_ (5,3):O (5,4):_ (5,5):_ (5,6):_ 
        (4,0):_ (4,1):_ (4,2):_ (4,3):X (4,4):_ (4,5):_ (4,6):_ 
        (3,0):_ (3,1):O (3,2):_ (3,3):O (3,4):O (3,5):X (3,6):_ 
        (2,0):_ (2,1):O (2,2):X (2,3):X (2,4):X (2,5):O (2,6):_ 
        (1,0):X (1,1):X (1,2):X (1,3):O (1,4):X (1,5):O (1,6):_ 
        (0,0):X (0,1):O (0,2):X (0,3):X (0,4):O (0,5):O (0,6):_ 

        For (3,2), Check for X:

        - Horizontal: check to left: (3,1):O, not X, stop; check to right: (3,3):O, not X, stop. Zero X in total.
        - Vertical: check to down: (2,2):X, (1,2):X, (0,2):X. 3 X in total. A winning move for X.
        - Diagonal 1: check to top left: (4,1):_, not X, stop; check to down right: (2,3):X, (1,4):X, (0,5):O, stop. 2 X in total, not enough.
        - Diagonal 2: check to top right: (4,3):X, (5,4):_; check to down left: (2,1):O. 1 X, not enough.

        Check for O:
        - Horizontal: check to left: (3,1):O, (3,0):_; check to right: (3,3):O, (3,4):O. 3 O in total. A winning move for O.
        - Vertical: check to down: (2,2):X. 0 O in total.
        - Diagonal 1: check to top left: (4,1):_, not O, stop; check to down right: (2,3):X. 0 O.
        - Diagonal 2: check to top right: (4,3):X; check to down left: (2,1):O, (1,0):X, 1 O, not enough.

    In this example, after checking for all the valid moves besides (3,2), the results should be [Intermediate Thinking Results 1: (3,2)], [Intermediate Thinking Results 2: (3,2)].

2. **Strategic Analysis**
From your previous observations, if you have a winning move after checking, directly choose it. Otherwise if your opponent have a winning move, block it. If these are not the case, choose the best move based on the following strategy:
    * Look for opportunities to create multiple winning lines (for) simultaneously. If you have two discs in a row horizontally and two discs in a row diagonally, placing your next disc in the right position could lead to a win in multiple ways. For example, you have discs at [(0,1), (1,2), (2,2), (2,1)], then place your next disc at (2,3) would connect two lines: [(0,1), (1,2), (2,3)] and [(2,1), (2,2), (2,3)]
    * If your opponent has two consecutive discs in a row horizontally, block them from getting a third disc in that row. For example, if your opponent has discs at [(0,1), (0,2)], then place your next disc at (0,3) or (0,0) to block them.
    * Consider the center column as a strategic starting point. Placing your disc in the center column can give you more opportunities to create winning lines in different directions. Make the most of your opening moves by playing in the central columns.
    * Plan Ahead: Think one or two moves ahead. Try to anticipate where your opponent might be aiming to connect their discs and plan your strategy accordingly. For example, if your opponent has a winning move on (3,3), while (2,3) is not your winning move, you should not take (2,3) as your move, avoiding (3,3) to be a valid move for your opponent.
    * Try to get your 3 discs in a row with open spaces on either end.

3. **Conclusion**
In this section, based on your previous analysis, clearly state your decision for the position to place your next disc and give explanation.

4. **Chosen Move**
    * In this section, only output the chosen move. Do not include any other words.
    * The format is: "Chosen Move: (a,b)", where a is the row number (0-5), and b is the column number (0-6) where you want to place your disc.


Current Game Board: 
(5,0):_ (5,1):_ (5,2):_ (5,3):_ (5,4):_ (5,5):_ (5,6):_ 
(4,0):_ (4,1):_ (4,2):_ (4,3):_ (4,4):_ (4,5):_ (4,6):_ 
(3,0):_ (3,1):_ (3,2):_ (3,3):_ (3,4):_ (3,5):_ (3,6):_ 
(2,0):_ (2,1):_ (2,2):_ (2,3):_ (2,4):X (2,5):_ (2,6):_ 
(1,0):_ (1,1):_ (1,2):O (1,3):_ (1,4):X (1,5):_ (1,6):_ 
(0,0):_ (0,1):O (0,2):O (0,3):X (0,4):X (0,5):X (0,6):O 

Current valid moves for player O: ['(0,0)', '(1,1)', '(2,2)', '(1,3)', '(3,4)', '(1,5)', '(1,6)']
You are player O, please choose the best move considering the current board state.
    '''
    res = agent.get_response_text(prompt)
    print(res)