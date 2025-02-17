import random

from .Groq import Groq4Game
from .Kimi import Kimi
from .OpenAI import OpenAI
from .Vertex import Vertex
from .Claude import Claude
from .Jamba import Jamba
from .LLaMA3_1 import LLaMA3_1
from .Mistral import Mistral
from .Gemini import Gemini
from .Reka import Reka
import keys
from .DeepSeek_ByteDance import DeepSeekR1

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
                   n_retries=3, retry_wait=8):
        # -- Gemini via Vertex -- #
        if agent_str.startswith('gemini'):
            agent = Vertex(agent_str,
                           temperature=temperature,
                           top_k=top_k,
                           max_output_tokens=max_output_tokens,
                           project_id=project_id,
                           default_parameters=default_parameters,
                           n_retries=n_retries,
                           retry_wait=retry_wait)
        elif 'deepseek' in agent_str:
            agent = DeepSeekR1(keys.bytedance_key)
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

        # -- GPT models via OpenAI -- #
        elif agent_str.startswith('gpt'):
            azure_endpoint = ["https://baairl-eastus2.openai.azure.com/", \
                              "https://llambda-us.openai.azure.com"]
            if agent_str == 'gpt-4o' or agent_str == 'gpt-4o-mini':
                agent = OpenAI(model_name=agent_str,
                               api_key=keys.openai_key_lambda,
                               azure_endpoint=azure_endpoint[1],
                               temperature=temperature,
                               max_output_tokens=max_output_tokens,
                               seed=seed,
                               default_parameters=default_parameters)
            elif agent_str == 'gpt-4-1106' or agent_str == 'gpt-35-turbo':
                agent = OpenAI(model_name=agent_str,
                               api_key=keys.openai_key_baai,
                               azure_endpoint=azure_endpoint[0],
                               temperature=temperature,
                               max_output_tokens=max_output_tokens,
                               seed=seed,
                               default_parameters=default_parameters)
            else:
                raise ValueError(f"Unsupported model {agent_str}")
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
