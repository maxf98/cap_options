## what is code-as-policies fundamentally?
##  just generate python code to control the robot - so we need the basic API, we need the CAP interaction, 
# and eventually we can add hierarchical function generation, although I think it might not be necessary
# we're using GPT-4o, so images are a given, that should depend on the prompt
import os
import ast 
from time import sleep
import copy

from utils.cap_utils import merge_dicts, extract_code, exec_safe, var_exists, FunctionParser, print_code
from utils import core_primitives, core_types
import utils.general_utils as utils
from utils.llm_utils import query_llm, parse_code_response

import openai
import numpy as np
import itertools
from collections import defaultdict
import pickle

import openai

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

TEMPERATURE = 1
MODEL = "gpt-4o"
MAX_TOKENS = 3000


FGEN_PROMPT = open(f"prompts/fgen.txt").read()


def get_code_globals():
    vars = { name: getattr(core_primitives, name) for name in core_primitives.__all__ }
    vars.update({name: getattr(core_types, name) for name in core_types.__all__ }) 
    vars.update({ 'np': np, 'itertools': itertools})
    return vars


def lmp(messages, env):
    response = query_llm(messages)
    code_str = parse_code_response(response)
    gvars = get_code_globals()
    gvars.update({"env": env})

    new_fs = create_new_fs_from_code(code_str, gvars)
    lvars = new_fs
    
    exec_safe(code_str, gvars, lvars)

    return code_str
# ---------------------------------------------------------------------

def fgen_lmp(f_name, f_sig, new_fs, f_description=None):
    messages = [{"role": "system", "content": FGEN_PROMPT}, {"role": "user", "content": f"write the function code for {f_name} with signature {f_sig}"}]
    response = query_llm(messages)
    f_src = parse_code_response(response)

    gvars = merge_dicts([gvars, lvars, new_fs])
    lvars = {}

    exec_safe(f_src, gvars, lvars)

    f = lvars[f_name]

    return f, f_src


def create_new_fs_from_code(code_str, gvars):
    if '```' in code_str:
        code_str = extract_code(code_str)

    fs, f_assigns = {}, {}
    f_parser = FunctionParser(fs, f_assigns)
    f_parser.visit(ast.parse(code_str))
    for f_name, f_assign in f_assigns.items():
        if f_name in fs:
            fs[f_name] = f_assign

    new_fs = {}
    srcs = {}
    for f_name, f_sig in fs.items():
        all_vars = merge_dicts([gvars, new_fs])
        if not var_exists(f_name, all_vars):
            f, f_src = fgen_lmp(
                f_name,
                f_sig,
                new_fs
            )

            # recursively define child_fs in the function body if needed
            f_def_body = ast.unparse(ast.parse(f_src).body[0].body)
            child_fs, child_f_srcs = create_new_fs_from_code(
                f_def_body, all_vars
            )

            if len(child_fs) > 0:
                new_fs.update(child_fs)
                srcs.update(child_f_srcs)

                # redefine parent f so newly created child_fs are in scope
                gvars = merge_dicts(
                    [gvars, new_fs]
                )
                lvars = {}

                exec_safe(f_src, gvars, lvars)

                f = lvars[f_name]

            new_fs[f_name], srcs[f_name] = f, f_src

    return new_fs, srcs