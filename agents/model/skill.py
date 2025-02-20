import os, pickle, ast
from agents.experience import AttemptTrace, InteractionTrace

from config import SKILL_DIR


class Skill:
    def __init__(
        self,
        name,
        docstring,
        code,
        task_examples=[],
        is_core_primitive=False,
    ):
        self.name = name
        self.docstring = docstring
        self.code = code
        self.task_examples = task_examples
        self.is_core_primitive = is_core_primitive

    @property
    def save_dir(self):
        return f"{SKILL_DIR}/{self.name}"

    def __str__(self):
        # return self.description
        return self.code if not self.is_core_primitive else self.description

    @property
    def description(self):
        return f"{self.function_signature}\n{self.docstring}"

    def dump(self):
        """store the skill in some readable way so we can inspect it..."""
        os.makedirs(self.save_dir, exist_ok=True)
        with open(f"{self.save_dir}/code.py", "w") as file:
            file.write(self.code)
        with open(f"{self.save_dir}/skill.pkl", "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def retrieve_skill_with_name(name) -> "Skill":
        # with open(f"{SKILL_DIR}/{name}/code.py", "r") as file:
        #     skill_code = file.read()
        with open(f"{SKILL_DIR}/{name}/skill.pkl", "rb") as file:
            skill = pickle.load(file)

        return skill

    @staticmethod
    def parse_function_string(code_string: str) -> "Skill":
        # we assume that the string only contains a single function
        # generates a partially initialised skill without a description
        tree = ast.parse(code_string)
        func_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        if len(func_defs) != 1:
            print(
                f"not exactly one ({len(func_defs)} - {func_defs}) function defined in code string:\n{code_string}"
            )

        func = func_defs[0]
        func_name = func.name
        func_source = ast.get_source_segment(code_string, func)
        doc_string = ast.get_docstring(func)

        return Skill(func_name, doc_string, func_source)

    @property
    def traces(self):
        return [AttemptTrace.get_attempt_trace(id) for id in self.trace_ids]

    @property
    def function_signature(self):
        lines = self.code.splitlines()
        signature = ""

        for line in lines:
            line = line.strip()
            if line.startswith("def "):  # Start capturing from function definition
                signature += line
            elif signature:  # If already capturing, continue appending
                signature += " " + line.strip()
            if '"""' in line:  # Stop once the docstring starts
                break

        return signature.split('"""', 1)[0]  # Return everything up to the colon
