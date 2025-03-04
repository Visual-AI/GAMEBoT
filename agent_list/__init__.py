import random

from .Groq import Groq4Game
from .Kimi import Kimi
from .OpenAI import OpenAI, AzOpenAI
from .Vertex import Vertex
from .Claude import Claude
# from .Command_R import Command_R
from .Jamba import Jamba
from .LLaMA3_1 import LLaMA3_1
from .Mistral import Mistral
# from .Phi import Phi
from .Gemini import Gemini
from .Reka import Reka
import keys
from .DeepSeek_ByteDance import DeepSeekR1

import os
# proxy = 'http://127.0.0.1:7890'
#
# os.environ['http_proxy'] = proxy
# os.environ['HTTP_PROXY'] = proxy
# os.environ['https_proxy'] = proxy
# os.environ['HTTPS_PROXY'] = proxy
class RandomAgent:
    def __init__(self):
        self.is_random = True

    def get_response_text(self, prompt):
        return "random"


class InitAgent:
    def __init__(self, key_start=0):
        self.init_gemini_time = random
        self.init_groq_time = key_start

    def init_agent(self, agent_str, max_output_tokens=4096, temperature=0.0,
                   top_k=1, seed=42, project_id="llmsasagents", default_parameters=True,
                   n_retries=6, retry_wait=10):
        if agent_str == 'gemini-1.0-pro-latest' or agent_str == 'gemini-1.5-flash-001' or agent_str == 'gemini-exp-1206':
            agent = Gemini(model_name=agent_str,
                           api_key=keys.gemini_api_key_list[random.choice(range(0, len(keys.gemini_api_key_list)))])
        # -- Gemini via Vertex -- #
        elif agent_str.startswith('gemini'):
            # agent = Gemini(model_name=agent_str, api_key=keys.gemini_api_key_list[self.init_gemini_time])
            # self.init_gemini_time += 1
            agent = Vertex(agent_str,
                           temperature=temperature,
                           top_k=top_k,
                           max_output_tokens=8192,
                           project_id=project_id,
                           default_parameters=default_parameters,
                           n_retries=n_retries,
                           retry_wait=retry_wait)
        elif 'deepseek' in agent_str:
            agent = DeepSeekR1(keys.bytedance_key, max_output_tokens=8192)
        # -- Kimi -- #
        elif agent_str.startswith('kimi'):
            agent = Kimi(api_key=keys.kimi_api_key)

        # -- Command-R -- #
        elif 'command' in agent_str:
            agent = Command_R(agent_str,
                              temperature=temperature,
                              max_output_tokens=max_output_tokens,
                              default_parameters=default_parameters)
        elif 'jamba' in agent_str:
            agent = Jamba(agent_str,
                          temperature=temperature,
                          max_output_tokens=max_output_tokens,
                          project_id=project_id,
                          default_parameters=default_parameters,
                          n_retries=n_retries,
                          retry_wait=retry_wait)
        elif 'meta' in agent_str:
            agent = LLaMA3_1(agent_str,
                             temperature=temperature,
                             max_output_tokens=max_output_tokens,
                             project_id=project_id,
                             default_parameters=default_parameters,
                             n_retries=n_retries,
                             retry_wait=retry_wait)
        elif 'mistral' in agent_str:
            agent = Mistral(agent_str,
                            temperature=temperature,
                            max_output_tokens=max_output_tokens,
                            project_id=project_id,
                            seed=seed,
                            model_version="2407",
                            default_parameters=default_parameters,
                            n_retries=n_retries,
                            retry_wait=retry_wait)

        elif 'phi' in agent_str:
            agent = Phi(agent_str,
                        temperature=temperature,
                        max_output_tokens=max_output_tokens,
                        default_parameters=default_parameters,
                        n_retries=n_retries,
                        retry_wait=retry_wait)

        elif 'reka' in agent_str:
            agent = Reka(agent_str,
                         api_key=keys.reka_key,
                         temperature=temperature,
                         max_output_tokens=max_output_tokens,
                         seed=seed,
                         default_parameters=default_parameters,
                         n_retries=n_retries,
                         retry_wait=retry_wait)

        # -- GPT models via AzureOpenAI -- #
        elif agent_str.startswith('gpt'):
            azure_endpoint = ["https://baairl-eastus2.openai.azure.com/", \
                              "https://llambda-us.openai.azure.com"]
            if agent_str == 'gpt-4o' or agent_str == 'gpt-4o-mini':
                agent = AzOpenAI(model_name=agent_str,
                               api_key=keys.openai_key_lambda,
                               azure_endpoint=azure_endpoint[1],
                               temperature=temperature,
                               max_output_tokens=max_output_tokens,
                               seed=seed,
                               default_parameters=default_parameters)
            elif agent_str == 'gpt-4-1106' or agent_str == 'gpt-35-turbo':
                agent = AzOpenAI(model_name=agent_str,
                               api_key=keys.openai_key_baai,
                               azure_endpoint=azure_endpoint[0],
                               temperature=temperature,
                               max_output_tokens=max_output_tokens,
                               seed=seed,
                               default_parameters=default_parameters)
            else:
                raise ValueError(f"Unsupported model {agent_str}")
        # -- OpenAI models -- #
        elif agent_str.startswith('o1') or agent_str.startswith('o3'):
            agent = OpenAI(model_name=agent_str,
                           api_key=keys.openai_key,
                           temperature=temperature,
                           max_output_tokens=4096*3,
                           seed=seed,
                           default_parameters=default_parameters)
        # -- Claude models via Vertex -- #
        elif agent_str.startswith('claude'):
            agent = Claude(model_name=agent_str,
                           temperature=temperature,
                           top_k=top_k,
                           max_output_tokens=max_output_tokens,
                           project_id=project_id,
                           default_parameters=default_parameters,
                           n_retries=n_retries,
                           retry_wait=retry_wait)
        elif agent_str == 'random':
            agent = RandomAgent()
        else:
            agent = Groq4Game(model_name=agent_str,
                              api_key=keys.groq_api_key_list[random.choice(range(0, len(keys.groq_api_key_list)))])
            self.init_groq_time += 1
        return agent


if __name__ == '__main__':
    # Test run each model
    # Vertex
    agent = InitAgent().init_agent('gemini-1.5-pro-preview-0514')
    print(agent.get_response_text("What is the meaning of life?"))
    # Jamba
    agent = InitAgent().init_agent('jamba-1.5-large')
    print(agent.get_response_text("What is the meaning of life?"))
    # LLaMA3.1
    agent = InitAgent().init_agent('meta/llama3-405b-instruct-maas')
    print(agent.get_response_text("What is the meaning of life?"))
    # Mistral
    agent = InitAgent().init_agent('mistral-nemo')
    print(agent.get_response_text("What is the meaning of life?"))
    # Reka
    agent = InitAgent().init_agent('reka-flash')
    print(agent.get_response_text("What is the meaning of life?"))
    # Claude
    agent = InitAgent().init_agent('claude-3-5-sonnet@20240620')
    print(agent.get_response_text("What is the meaning of life?"))
