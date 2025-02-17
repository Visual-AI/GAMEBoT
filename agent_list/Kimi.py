from openai import OpenAI
import keys
import time
class Kimi:
    def __init__(self, api_key):

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1",
        )
    def get_response_text(self, prompt):
        for i in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {"role": "system",
                         "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                break
            except Exception as e:
                print('!!! An error occur during access Kimi API, try again', e)
                time.sleep(10 * (i + 1))
        try:
            return response.choices[0].message.content
        except:
            return ''


if __name__ == '__main__':
    kimi = Kimi(keys.kimi_api_key)
    print(kimi.get_response_text('tell me a beautiful love story intelligently'))