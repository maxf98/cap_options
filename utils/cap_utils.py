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


class FunctionParser(ast.NodeTransformer):
    def __init__(self, fs, f_assigns):
        super().__init__()
        self._fs = fs
        self._f_assigns = f_assigns

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name):
            f_sig = ast.unparse(node).strip()
            f_name = ast.unparse(node.func).strip()
            self._fs[f_name] = f_sig
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Call):
            assign_str = ast.unparse(node).strip()
            f_name = ast.unparse(node.value.func).strip()
            self._f_assigns[f_name] = assign_str
        return node


def code_exec_with_bug_fix(code_str, code_env, max_num_attempts=1):
    # fix bugs in llm-generated code... with llm
    # max_num_attempts must be >= 1 (otherwise it just never gets run, >1 to fix bugs)
    attempts = 0
    messages = [
        {
            "role": "system",
            "content": "you write python code to control a robotic arm. You receive pieces of code that contain an error, as well as the error traceback, and you are supposed to fix it.",
        }
    ]
    while attempts < max_num_attempts:
        try:
            exec(code_str, code_env)
        except:
            traceback.print_exc()
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


def merge_dicts(dicts):
    return {k: v for d in dicts for k, v in d.items()}


def var_exists(name, all_vars):
    try:
        eval(name, all_vars)
    except:
        exists = False
    else:
        exists = True
    return exists
