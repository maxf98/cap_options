import ast
import re

import traceback

from PIL import Image
import io
import base64

from utils import core_primitives, core_types
import numpy as np
import itertools

from prompts.base_prompt import bug_fix_prompt
from utils.llm_utils import query_llm, parse_code_response, extract_code


def get_global_vars(env):
    # need to set the current environment as global variable for core primitives
    core_primitives.env = env

    vars = {name: getattr(core_primitives, name) for name in core_primitives.__all__}
    vars.update({name: getattr(core_types, name) for name in core_types.__all__})
    vars.update({"np": np, "itertools": itertools})
    return vars


def code_exec_with_bug_fix(code_str, env, max_num_attempts=1):
    # fix bugs in llm-generated code... with llm
    # max_num_attempts must be >= 1 (otherwise it just never gets run, >1 to fix bugs)
    attempts = 1
    messages = [
        {
            "role": "system",
            "content": "you write python code to control a robotic arm. You receive pieces of code that contain an error, as well as the error traceback, and you are supposed to fix it.",
        }
    ]
    while True:
        try:
            gvars = get_global_vars(env)
            exec(code_str, gvars)
        except:
            traceback.print_exc()
            if attempts < max_num_attempts:
                messages.extend(
                    [
                        {"role": "assistant", "content": code_str},
                        {
                            "role": "user",
                            "content": bug_fix_prompt(code_str, traceback.format_exc()),
                        },
                    ]
                )
                response = query_llm(messages)
                print("attempting to fix bugs")
                code_str = parse_code_response(response)
                attempts += 1
            else:
                return
        else:
            return
