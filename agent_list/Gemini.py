import pathlib
import textwrap

import google.generativeai as genai
import os
# from IPython.display import display
# from IPython.display import Markdown

# from PIL import Image
import time
import keys
import random

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# model = genai.GenerativeModel('gemini-pro-vision')
# model = genai.GenerativeModel('gemini-1.0-pro-vision-latest')


# model = genai.GenerativeModel('gemini-1.5-pro-latest')


# model = genai.GenerativeModel('gemini-1.0-pro', generation_config={'max_output_tokens': 1000})
# print(model._generation_config)
# response = model.generate_content(
#     ['告诉我一个像庆余年一样的好看的电视剧'])
# print(response.text)

class Gemini:
    def __init__(self, model_name, api_key):
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name
                                           # generation_config={'temperature': 0.1}

                                           # generation_config={'max_output_tokens': 1000, 'temperature': 1}
                                           )
        self.chat = self.model.start_chat(history=[])

    def get_response(self, prompt, img):
        response = self.model.generate_content([prompt, img])
        # response.resolve()
        return response

    def get_response_text(self, prompt):
        for i in range(10):
            try:
                response = self.model.generate_content([prompt],request_options={"timeout": 120})
                break
            except Exception as e:
                random_num = random.randint(0, len(keys.gemini_api_key_list)-1)
                genai.configure(api_key=keys.gemini_api_key_list[random_num])
                self.model = genai.GenerativeModel(self.model_name)
                print('!!! An error occur during access Gemini API, try for the {} time, use key from {}. '.format(i+1, random_num), e)
                time.sleep(10 * (i + 1))
        try:
            try:
                return response.text
            except:
                return ' '.join([part.text for part in response.candidates[0].content.parts])
        except:
            return ''

    def chat_mm(self, prompt, img):
        response = self.chat.send_message([img, prompt])
        return response

    def chat_text(self, prompt):
        response = self.chat.send_message([prompt])
        try:
            return response.text
        except:
            return ' '.join([part.text for part in response.candidates[0].content.parts])


# question = '''
# 	You are an expert in the Atari Pong game. Your task is to control the right paddle to defeat the left opponent. Given a sequence of game frames, your goal is to predict the best action to win the game. The available actions are defined as follows: 0 - Stay Still; 1 - Move Up; 2 - Move Down.
#
# 	I will give you the extra following information:
# 	Ball Position: The X and Y coordinates of the ball on the screen.
# 	Your Paddle Position: The Y-coordinate range of the right paddle. The X-coordinate of the right paddle is always 139.
# 	Opponent's Paddle Position: The Y-coordinate range of the left paddle. The X-coordinate of the left paddle is always 21.
# 	Y-coordinate of Lower Wall: 16Ï
# 	Y-coordinate of Upper Wall: 176
#
# 	Here is an example.
#
# 	Input:
#
# 	Frame 42
# 	{'ball_x': 71, 'ball_y': 136, 'player_x': 139, 'player_y': [62, 78], 'enemy_x': 21, 'enemy_y': [111, 127], 'upper_bound': 176, 'lower_bound': 16}
# 	Frame 43
# 	{'ball_x': 75, 'ball_y': 144, 'player_x': 139, 'player_y': [59, 75], 'enemy_x': 21, 'enemy_y': [117, 133], 'upper_bound': 176, 'lower_bound': 16}
# 	Frame 44
# 	{'ball_x': 79, 'ball_y': 152, 'player_x': 139, 'player_y': [62, 78], 'enemy_x': 21, 'enemy_y': [125, 141], 'upper_bound': 176, 'lower_bound': 16}
#
# 	Output:
#
# 	[Observation]
# 	The coordinate of the ball is (79, 152) right now. The ball_x is increasing (79 > 75 > 71), suggesting that the ball is going right. The ball_y is increasing (152 > 144 > 136), suggesting the ball is going up.
#
# 	[Thought]
# 	The trace of the ball can be calculated. Let the trace line be y = mx + b, we know (x1, y1) is (79, 152) and (x2, y2) is (75, 144), thus m = (y2 - y1) / (x2 - x1) = (144 - 152) / (75 - 79) = 2, and b = y1 - mx1 = 152 - 2 * 79  = -6, so y  = 2x - 6.
#
# 	When x is equal to player_x, 139, y = 2 * 139 - 6 = 272 > 176, showing that the ball will reach the upper bound before reaching the right paddle. For y  = 2x - 6, when y = 176, x = (176 + 6) / 2 = 91. After rebounding the ball, the direction of m will be changed, so m will be -2. For y = -2x + b, replace with (91, 176), we can get b = y + 2x = 176 + 2*91 = 358.
#
# 	Finally, for the new trace y = -2x + 358, when x is equal to player_x, 139, y = -2 * 139 + 358 = 80. So when reaching the position of the right paddle, ball_y is 80.
#
# 	The prediction of ball_y is larger than the range of player_y, so the action should be 1 - Move Up.
#
# 	[Action] 1 - Move Up
#
# 	Input:
# 	Frame 45
# 	{'ball_x': 83, 'ball_y': 160, 'player_x': 139, 'player_y': [65, 81], 'enemy_x': 21, 'enemy_y': [131, 147], 'upper_bound': 176, 'lower_bound': 16}
#
# 	Output:
#
# '''

#
# def test_response():
#     response = model.generate_content(
#         [question])
#     print(response.text)
if __name__ == '__main__':
    genai.configure(api_key=keys.gemini_api_key_list[0])
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m)
    # proxy = 'http://127.0.0.1:7890'
    #
    # os.environ['http_proxy'] = proxy
    # os.environ['HTTP_PROXY'] = proxy
    # os.environ['https_proxy'] = proxy
    # os.environ['HTTPS_PROXY'] = proxy
    model = Gemini('gemini-exp-1206', keys.gemini_api_key_list[0])
    print(model.get_response_text('Tell me a good movie that is fun but enlight us to think about life'))