## what is code-as-policies fundamentally?
##  just generate python code to control the robot - so we need the basic API, we need the CAP interaction,
# and eventually we can add hierarchical function generation, although I think it might not be necessary
# we're using GPT-4o, so images are a given, that should depend on the prompt
import os
from time import sleep

from utils.cap_utils import exec_safe, print_code, get_code_globals
from utils import core_primitives, core_types
from utils.llm_utils import query_llm, parse_code_response
from agents.skill import add_new_skill

from PIL import Image
import base64
import io

import pydantic
from typing import Optional
import traceback

import openai
import numpy as np
import itertools
import ast

from prompts.base_prompt import (
    skill_extraction_prompt,
    main_planner_prompt,
    parse_completion_prompt,
    explain_failure_prompt,
    system_prompt,
    bug_fix_prompt,
)


def planner_lmp(messages, task, env):
    messages.append({"role": "user", "content": main_planner_prompt})
    messages.append({"role": "user", "content": task})

    response = query_llm(messages)
    code_str = parse_code_response(response)

    # new_fs = create_new_fs_from_code(code_str, gvars)
    # lvars = new_fs
    code_exec_with_bug_fix(code_str, env)
    return code_str


# --------------------------------------------------------------------------


def check_completion_lmp(task, task_attempt, image, env):
    # two step prompt: if completion check returns true, we just take it at its word
    # if false, we attach the code, and the image, and ask the llm to explain what didn't work
    # then we pass that as context for replanning
    messages = []

    messages.append({"role": "user", "content": parse_completion_prompt(task)})
    response = query_llm(messages)
    code_str = parse_code_response(response)
    gvars = get_code_globals()
    gvars.update({"env": env})

    exec(code_str, gvars)

    code_task_success = gvars["task_success"]

    return code_task_success
    # if code_task_success:
    #     return

    # b64img = encode_image(image)
    # messages.append({"role": "user", "content": [
    #             {"type": "text", "text": explain_failure_prompt(task, task_attempt, code_str)},
    #             {"type": "image_url", "image_url":
    #                 {"url": f"data:image/jpeg;base64,{b64img}", "detail": "low"}}]})

    # response = query_llm(messages)

    # return response


# ---------------------------------------------------------------------


def is_single_function_block(code_str):
    tree = ast.parse(code_str)
    return len(tree.body) == 1 and isinstance(tree.body[0], ast.FunctionDef)


def extract_skill_lmp(messages):
    # task success => define function that wraps the code result and generate a function description
    # take the last message, generate an appropriate function name, encapsulate into a function, and conform to Skill BaseModel
    messages.append({"role": "user", "content": skill_extraction_prompt})
    response = query_llm(messages)
    code_str = parse_code_response(response)
    print_code(code_str)

    if is_single_function_block(code_str):
        namespace = {}
        exec(code_str, get_code_globals(), namespace)
        for item in namespace.values():
            if callable(item) and getattr(item, "__code__", None):
                print(item)
                add_new_skill(item.__name__, code_str)
    else:
        print("should try again then... function extraction was unsuccessful")
        return
    # extract from conversation history
    return


if __name__ == "__main__":
    print("ello")

    from environments.environment import Environment

    env = Environment(
        "/Users/maxfest/vscode/thesis/ravens/environments/assets",
        disp=False,
        shared_memory=False,
        hz=480,
        record_cfg={
            "save_video": False,
            "save_video_path": "${data_dir}/${task}-cap/videos/",
            "add_text": True,
            "add_task_text": True,
            "fps": 20,
            "video_height": 640,
            "video_width": 720,
        },
    )
    from tasks.many_blocks import ManyBlocksTask

    env.set_task(ManyBlocksTask())
    env.reset()
    import time

    time.sleep(1)

    img = env.render()
    b64img = encode_image(img)

    from matplotlib import pyplot as plt

    # plt.imshow(img)
    # plt.show()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "tell me what's in this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64img}",
                        "detail": "low",
                    },
                },
            ],
        }
    ]
    response = query_llm(messages)
    print(response)
