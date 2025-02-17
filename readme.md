<div align="center">
  <img src="coolerbot_nobg.png" alt="GAMEBoT Logo">
</div>

Official repository for [Beyond Outcomes: Transparent Assessment of LLM Reasoning in Games](https://arxiv.org/abs/2412.13602).

## Project Page

[Visit My Project Website](https://visual-ai.github.io/gamebot/)


## Evaluated Models
- gpt-4o-2024-05-13
- gpt-4o-mini-2024-07-18
- gpt-4-1106
- gemini-1.5-pro-preview-0514
- gemini-1.5-flash-preview-0514
- gemini-1.0-pro-002
- claude-3-haiku@20240307
- claude-3-sonnet@20240229
- claude-3-5-sonnet@20240620
- meta/LLaMA3-\{8,7,405\}b-instruct-maas
- reka-flash-20240904
- reka-core-20240415
- jamba-1.5-large
- jamba-1.5-mini
- mistral-nemo-2407

### New models to evaluate
#### implemented
- gemini-2.0-flash-exp
- gemini-2.0-flash-thinking-exp-1219
- claude-3-5-sonnet-v2@20241022
- claude-3-5-haiku@20241022
- meta/llama-3.2-90b-vision-instruct-maas
- deepseek-r1

#### not yet implemented
- o1-2024-12-17
- o1-mini-2024-09-12

## Example of Usage
1. Install the needed packages from the requirements.txt file
```
sh setup_env.sh && pip install -r requirements.txt
```
2. Setup the keys for the API or implement your own interface to call LLM in agent_list: add your model to InitAgent() in ``agent_list/__init__.py``
3. Run the game
```
python run_games_and_check/othello.py gpt-4o gemini-1.5-pro-preview-0514 --cycles 20
```

## Citing
If you find this work useful, please cite our paper:
```bibtex
@article{lin2024beyond,
  title={Beyond Outcomes: Transparent Assessment of LLM Reasoning in Games},
  author={Lin Wenye and Roberts Jonathan and Yang Yunhan and Albanie Samuel and Lu Zongqing and Han Kai},
  journal={arXiv preprint arXiv:2412.13602},
  year={2024}
}
```