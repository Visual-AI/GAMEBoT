from agent_list import InitAgent
from typing import List
import beartype as beartype
import pandas as pd


#@beartype
def run_inference_test(models_list: List[str], prompt: str, n_retries: int, retry_wait: int) -> pd.DataFrame:

    # Create test results dataframe
    test_results = pd.DataFrame(columns=['model', 'created_valid_agent?', 'created_invalid_agent?', 'valid_test_response', 'pass_valid_test?'])#, 'invalid_test_response', 'pass_invalid_test?'])

    # Test run each model - expecting valid response
    print("Testing models, expecting valid response")

    for model in models_list:
        test_results.loc[len(test_results)] = {'model': model, 'created_valid_agent?': False, 'created_invalid_agent?': False, 'valid_test_response': None, 'pass_valid_test?': False}#, 'invalid_test_response': None, 'pass_invalid_test?': False}
        try:
            test_results.loc[test_results['model'] == model, 'created_valid_agent?'] = False
            agent = InitAgent().init_agent(model, n_retries=n_retries, retry_wait=retry_wait)
            print(f'Successfully created agent for model: {model}')
            test_results.loc[test_results['model'] == model, 'created_valid_agent?'] = True
            model_output = agent.get_response_text(prompt)
            test_results.loc[test_results['model'] == model, 'valid_test_response'] = model_output
            if model_output == f'None - failed to generate content after {n_retries} tries':
                print(f'Failed to run inference test for model: {model}')
                test_results.loc[test_results['model'] == model, 'pass_valid_test?'] = False
            else:
                print(f'Successfully ran inference test for model: {model}')
                print(f'Model output: {model_output}')
                test_results.loc[test_results['model'] == model, 'pass_valid_test?'] = True
        except Exception as e:
            print(f'Failed to run inference test for model: {model} - {e}')
            test_results.loc[test_results['model'] == model, 'valid_test_response'] = f'Error: {e}'
            test_results.loc[test_results['model'] == model, 'pass_valid_test?'] = False

    """
    # Test run each model - expecting invalid response of the format: f'None - failed to generate content after {max_tries} tries'
    print("Testing models, expecting invalid response")
    for model in models_list:
        try:
            test_results.loc[test_results['model'] == model, 'created_invalid_agent?'] = False
            # perturb model_name to cause error
            agent = InitAgent().init_agent(f'{model}-invalid', n_retries=n_retries, retry_wait=retry_wait)
            print(f'Successfully created agent for model: {model}-invalid')
            test_results.loc[test_results['model'] == model, 'created_invalid_agent?'] = True
            model_output = agent.get_response_text(prompt)
            print(f'Successfully ran invalid inference test for model: {model}-invalid')
            print(f'Model output: {model_output}')
            test_results.loc[test_results['model'] == model, 'invalid_test_response'] = model_output
            test_results.loc[test_results['model'] == model, 'pass_invalid_test?'] = True
        except Exception as e:
            print(f'Failed to run invalid inference test for model: {model}-invalid - {e}')
            test_results.loc[test_results['model'] == model, 'invalid_test_response'] = f'Error: {e}'
            test_results.loc[test_results['model'] == model, 'pass_invalid_test?'] = False
    """
    return test_results


if __name__ == "__main__":

    agents = [
        "claude-3-haiku@20240307",
        "reka-core-20240501",
        "reka-flash-20240226",
        "reka-edge-20240208",
        "claude-3-sonnet@20240229",
        "claude-3-5-sonnet@20240620",
        "gemini-1.5-flash-preview-0514",
        "gemini-1.5-pro-preview-0514",
        "gemini-1.0-pro-002",
        "meta-llama3-405b-instruct-maas",
        "meta-llama3-70b-instruct-maas",
        "meta-llama3-8b-instruct-maas",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-1106",
        "jamba-1.5-mini",  # rate limit too low
        "jamba-1.5-large",  # rate limit too low
        "mistral-large",  # output tokens rate limit too low
        "mistral-nemo",  # output tokens rate limit too low
    ]

    max_retries = 5
    retry_wait_time = 0 # to quickly test the retry mechanism
    test_prompt = "What is two plus two? Only return the number. Answer: "
    test_results = run_inference_test(agents, test_prompt, max_retries, retry_wait_time)
    print(test_results)

