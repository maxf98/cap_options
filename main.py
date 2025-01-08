from environments.environment import Environment
from tasks.many_blocks import ManyBlocksTask

import time

import pybullet as p

from config.cfg_tabletop import cfg_tabletop

from cap import lmp
from utils.llm_utils import read_py


BASE_PROMPT = read_py("prompts/main_prompt.txt")


def get_code_globals():
    from utils import core_primitives, core_types
    import numpy as np
    import itertools
    vars = { name: getattr(core_primitives, name) for name in core_primitives.__all__ }
    vars.update({name: getattr(core_types, name) for name in core_types.__all__ }) 
    vars.update({ 'np': np, 'itertools': itertools})
    return vars


def main():
    env = Environment(
        "/Users/maxfest/vscode/thesis/ravens/environments/assets",
        disp=True,
        shared_memory=False,
        hz=480,
        record_cfg={
            "save_video": False,
            "save_video_path": "${data_dir}/${task}-cap/videos/",
            "add_text": True,
            "add_task_text": True,
            "fps": 20,
            "video_height": 640,
            "video_width": 720
        }
    )

    env.set_task(ManyBlocksTask())
    env.reset()

    messages = [{"role": "system", "content": BASE_PROMPT}]
    while True:
        user_input = input('\n\n\n' + "I'm ready to take instruction." + '\n' + 'Input your instruction:')
        messages.append({"role": "user", "content": user_input})

        try:
            code_response = lmp(messages, env)
            messages.append({"role": "assistant", "content": code_response})

        except Exception as e:
            print("Error: ")
            print(e)




if __name__ == "__main__":
    main()