import os
import shutil

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm

import ast
import pickle
import inspect

from agents.experience import AttemptTrace, InteractionTrace

from prompts.skill import (
    skill_description_system_prompt,
    generate_skill_description_prompt,
)

import uuid


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)

ROOT_DIR = "/Users/maxfest/vscode/thesis/thesis/memory/skill_library/"
os.makedirs(ROOT_DIR, exist_ok=True)
SKILL_DIR = f"{ROOT_DIR}/skills"
EXAMPLES_DIR = "/Users/maxfest/vscode/thesis/thesis/memory//examples"
os.makedirs(EXAMPLES_DIR, exist_ok=True)
os.makedirs(f"{EXAMPLES_DIR}/examples", exist_ok=True)


class Skill:
    def __init__(
        self,
        name,
        docstring,
        code,
        trace_ids=[],
        is_core_primitive=False,
    ):
        self.name = name
        self.docstring = docstring
        self.code = code
        self.trace_ids = trace_ids
        self.is_core_primitive = is_core_primitive

    @property
    def save_dir(self):
        return f"{SKILL_DIR}/{self.name}"

    def __str__(self):
        return self.description
        # return self.code

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


class TaskExample:
    def __init__(self, task: str, code: str):
        self.id = uuid.uuid4()
        self.task = task
        self.code = code

    def save_dir(self):
        return f"{EXAMPLES_DIR}/{self.id}"

    def dump(self):
        os.makedirs(self.save_dir, exist_ok=True)
        with open(f"{self.save_dir}/code.py", "w") as file:
            file.write(f"# TASK:{self.task}\n\n{self.code}")
        with open(f"{self.save_dir}/example.pkl", "wb") as file:
            pickle.dump(self, file)

    def get_skill_headers(self):
        tree = ast.parse(self.code)
        func_defs = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        funcs = [ast.get_source_segment(self.code, func) for func in func_defs]
        return funcs

    def get_non_function_code(self):
        # Parse the code into an AST
        tree = ast.parse(self.code)
        # Extract non-function top-level code
        non_function_code_nodes = [
            node
            for node in tree.body
            if not isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            )
        ]
        # Convert AST nodes back to source code
        non_function_code = "\n".join(
            ast.unparse(node) for node in non_function_code_nodes
        )

        return non_function_code

    @staticmethod
    def retrieve_task_with_id(id) -> "TaskExample":
        with open(f"{EXAMPLES_DIR}/{id}/example.pkl", "rb") as file:
            example = pickle.load(file)

        return example


class SkillManager:
    vector_db_dir = os.path.join(ROOT_DIR, "vector_db")
    example_vector_db_dir = os.path.join(EXAMPLES_DIR, "vector_db")

    def __init__(self):
        os.makedirs(self.vector_db_dir, exist_ok=True)

        chroma_client = chromadb.PersistentClient(path=SkillManager.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="skill_library", embedding_function=openai_ef
        )

        examples_chroma_client = chromadb.PersistentClient(
            path=SkillManager.example_vector_db_dir
        )
        self.examples_vector_db = examples_chroma_client.get_or_create_collection(
            name="examples", embedding_function=openai_ef
        )

    @staticmethod
    def delete_skill_library():
        try:
            shutil.rmtree(SKILL_DIR)
            shutil.rmtree(SkillManager.vector_db_dir)
        except Exception as e:
            print(f"an error occurred {e}")

    def add_core_primitives_to_library(self):
        os.makedirs(SKILL_DIR, exist_ok=True)

        # only for retrieval purposes... functions are still actually called from core_primitives module
        from utils import core_primitives

        functions = inspect.getmembers(core_primitives, inspect.isfunction)
        for name, func in functions:
            if name not in core_primitives.__all__:
                continue

            path = f"{SKILL_DIR}/{name}"
            # delete if primitive was previously stored already...
            trace_ids = []
            if name in os.listdir(SKILL_DIR):
                print("was in there already")
                trace_ids = Skill.retrieve_skill_with_name(name).trace_ids
                self.vector_db.delete(ids=[name])
                shutil.rmtree(path)
            skill = Skill(
                name=name,
                docstring=inspect.getdoc(func),
                code=inspect.getsource(func),
                is_core_primitive=True,
                trace_ids=trace_ids,
            )
            self.add_skill_to_library(skill)

    @property
    def all_skills(self) -> list[Skill]:
        all_keys = self.vector_db.get()["ids"]
        skills = [Skill.retrieve_skill_with_name(name) for name in all_keys]
        return skills

    @property
    def num_skills(self):
        return self.vector_db.count()

    def add_skills_from_trace(self, trace: InteractionTrace):
        """extract skills from a (successful) attempt trace"""
        if trace.successful_attempt is None:
            return
        attempt = trace.successful_attempt

        tree = ast.parse(attempt.code_string)
        nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        for node in nodes:
            skill_str = ast.get_source_segment(attempt.code_string, node)
            skill = Skill.parse_function_string(skill_str)

            skill.trace_ids.append(attempt.id)  # kind of pointless, because incomplete
            self.add_skill_to_library(skill)

        # ---------------------------------------------------------------------------
        # --> should also store separately for few-shot examples...
        task_example = TaskExample(trace.task, attempt.code_string)
        self.write_example(task_example)

    def add_example_to_library(self, example: TaskExample):
        self.examples_vector_db.add(
            documents=[example.task],
            ids=[example.id],
            metadatas=[{"task": example.task}],
        )

    def delete_skill(self, name: str):
        if name in os.listdir(SKILL_DIR):
            print(f"deleting {name}")
            skill_dir = os.path.join(SKILL_DIR, name)
            shutil.rmtree(skill_dir)
            self.vector_db.delete(ids=[name])

    def add_skill_to_library(self, skill: Skill):
        # need to check if a function with this name has been generated before...
        if skill.name in os.listdir(SKILL_DIR):
            i = 1
            while os.path.join(SKILL_DIR, f"{skill.name}V{i}") in os.listdir(SKILL_DIR):
                i += 1
            new_name = f"{skill.name}V{i}"
            skill.code.replace(skill.name, new_name)
            skill.name = new_name

        self.vector_db.add(
            documents=[skill.docstring],
            ids=[skill.name],
            metadatas=[{"is_core_primitive": skill.is_core_primitive}],
        )
        skill.dump()

    def generate_description(self, task, skill_code):
        """if we want to generate a description rather than using the docstring"""
        print(f"\033[33mGenerating skill description...\033[0m")

        messages = [
            {"role": "system", "content": skill_description_system_prompt},
            {
                "role": "user",
                "content": generate_skill_description_prompt(skill_code, task),
            },
        ]

        description = query_llm(messages, model="gpt-4o")

        print(description)

        return description

    def retrieve_few_shot_examples(self, task):
        RETRIEVAL_TOP_K = 5
        num_results = min(RETRIEVAL_TOP_K, self.vector_db.count())

        results = self.examples_vector_db.query(
            query_texts=[task], n_results=num_results
        )

        examples = [
            (metadata["task"], metadata["code"]) for metadata in results["metadatas"][0]
        ]

        return examples

    def retrieve_skills(self, query, only_core_primitives=False) -> list[Skill]:
        """simplest retrieval tactic: query is a task"""
        RETRIEVAL_TOP_K = 5

        num_results = min(RETRIEVAL_TOP_K, self.vector_db.count())

        if only_core_primitives:
            results = self.vector_db.query(
                query_texts=[query],
                n_results=num_results,
                where={"is_core_primitive": True},
            )
        else:
            results = self.vector_db.query(query_texts=[query], n_results=num_results)

        names = results["ids"][0]
        # get skill objects matching with the retrieved docs
        return [Skill.retrieve_skill_with_name(name) for name in names]

    def get_all_skill_embeddings(self):
        results = self.vector_db.get(
            include=["embeddings"],
            where={
                "is_core_primitive": False
            },  # we don't want to cluster/rewrite core primitives - they are simply given...
        )

        return (results["ids"], results["embeddings"])


code = """
def mult(a, b):
    print(a, b)
    hello(42)
    return a*b
    """

if __name__ == "__main__":
    skill_manager = SkillManager()
    # res = skill_manager.all_skills
    # print(res)
