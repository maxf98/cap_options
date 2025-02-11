import ast
import re

import traceback

from PIL import Image
import io
import base64
import os

from utils import core_primitives, core_types
import numpy as np
import itertools

from prompts.base_prompt import bug_fix_prompt
from utils.llm_utils import query_llm, parse_code_response, extract_code

from agents.skill import Skill, SkillManager


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
            dependency_resolved_code_str = prepend_code_string_with_dependencies(
                code_str
            )
            exec(dependency_resolved_code_str, gvars)
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


def prepend_code_string_with_dependencies(code_str):
    dependencies = resolve_dependencies(code_str)
    new_code_str = code_str
    for skill in dependencies:
        new_code_str = skill.code + "\n\n" + new_code_str

    return new_code_str


def resolve_dependencies(code_str):
    """code that calls existing functions will not run unless we somehow import them into the code environment...
    a simple way to do it would just be to resolve the entire call tree and add it before the code string to be execd...
    """

    dependencies = []
    new_dependencies = list(get_calls(code_str).keys())

    all_skills = os.listdir("memory/skill_library/skills")

    while len(new_dependencies) > 0:
        skill_name = new_dependencies.pop(0)
        if skill_name not in dependencies and skill_name in all_skills:
            skill = Skill.retrieve_skill_with_name(skill_name)
            if not skill.is_core_primitive:
                dependencies.append(skill)
            deps = list(get_calls(skill.code).keys())
            new_dependencies.extend(deps)

    print("dependencies: ", [skill.name for skill in dependencies])

    return dependencies


# def get_calls(code_str, uniquing):
#     fs, f_assigns = {}, {}
#     f_parser = FunctionParser(fs, f_assigns)
#     f_parser.visit(ast.parse(code_str))
#     for f_name, f_assign in f_assigns.items():
#         if f_name in fs:
#             fs[f_name] = f_assign

#     return fs


def get_defs(code_str):
    tree = ast.parse(code_str)
    defs = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    return defs


def get_calls(code_str, unique=True):
    tree = ast.parse(code_str)
    visitor = FunctionCallVisitor()
    visitor.visit(tree)
    calls = list(set(visitor.calls)) if unique else visitor.calls
    return calls


def get_skill_calls(code_str):
    calls = get_calls(code_str)
    skill_manager = SkillManager()
    skills = skill_manager.all_skills
    skill_names = [skill.name for skill in skills]
    return [call for call in calls if call in skill_names]


# class FunctionParser(ast.NodeTransformer):
#     def __init__(self, fs, f_assigns):
#         super().__init__()
#         self._fs = fs
#         self._f_assigns = f_assigns

#     def visit_Call(self, node):
#         self.generic_visit(node)
#         if isinstance(node.func, ast.Name):
#             f_sig = ast.unparse(node).strip()
#             f_name = ast.unparse(node.func).strip()
#             self._fs[f_name] = f_sig
#         return node

#     def visit_Assign(self, node):
#         self.generic_visit(node)
#         if isinstance(node.value, ast.Call):
#             assign_str = ast.unparse(node).strip()
#             f_name = ast.unparse(node.value.func).strip()
#             self._f_assigns[f_name] = assign_str
#         return node


class FunctionCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        # Extract function name if it's a direct function call (not a method or attribute)
        if isinstance(node.func, ast.Name):
            self.calls.append(node.func.id)
        elif isinstance(
            node.func, ast.Attribute
        ):  # Handles method calls like obj.method()
            self.calls.append(node.func.attr)
        self.generic_visit(node)  # Continue visiting child nodes


code = """
def build_cube(a):
    x = 5

def sample_func(a, b, c):
    build_cube(a)
    move_end_effector_to(a, b)
    get_bbox(a)

"""

if __name__ == "__main__":
    # deps = resolve_dependencies(code)
    # print([dep.name for dep in deps])
    # print(prepend_code_string_with_dependencies(code))
    print(get_defs(code), get_calls(code), get_skill_calls(code))
