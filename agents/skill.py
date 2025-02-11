import os
import shutil

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm

import ast
import pickle
import inspect

from agents.experience import AttemptTrace


from prompts.base_prompt import (
    skill_description_system_prompt,
    generate_skill_description_prompt,
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)

ROOT_DIR = "/Users/maxfest/vscode/thesis/thesis/memory/skill_library/"
SKILL_DIR = f"{ROOT_DIR}/skills"


class Skill:
    def __init__(self, name, docstring, code, trace_ids=[], is_core_primitive=False):
        self.name = name
        self.docstring = docstring
        self.code = code
        self.trace_ids = trace_ids
        self.is_core_primitive = is_core_primitive

    @property
    def save_dir(self):
        return f"{SKILL_DIR}/{self.name}"

    def __str__(self):
        # return f"{self.code.splitlines()[0]}\n{self.docstring}"
        return self.code

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


class SkillManager:
    vector_db_dir = os.path.join(ROOT_DIR, "vector_db")

    def __init__(self):
        os.makedirs(self.vector_db_dir, exist_ok=True)

        chroma_client = chromadb.PersistentClient(path=SkillManager.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="skill_library", embedding_function=openai_ef
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
            # delete if primitive was previously stored already... get traces? for now whatever...
            if path in os.listdir(SKILL_DIR):
                self.vector_db.delete(ids=[name])
                shutil.rmtree(path)

            skill = Skill(
                name=name,
                docstring=inspect.getdoc(func),
                code=inspect.getsource(func),
                is_core_primitive=True,
            )
            self.add_skill_to_library(skill)

    @property
    def all_skills(self) -> list[Skill]:
        all_keys = [metadata["name"] for metadata in self.vector_db.get()["metadatas"]]
        skills = [Skill.retrieve_skill_with_name(name) for name in all_keys]
        return skills

    @property
    def num_skills(self):
        return self.vector_db.count()

    def add_skills(self, attempt: AttemptTrace):
        """extract skills from a (successful) attempt trace"""
        tree = ast.parse(attempt.code_string)
        nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        for node in nodes:
            skill_str = ast.get_source_segment(attempt.code_string, node)
            skill = Skill.parse_function_string(skill_str)
            skill.trace_ids.append(attempt.id)
            self.add_skill_to_library(skill)

    def add_skill_to_library(self, skill: Skill):
        # need to check if a function with this name has been generated before...
        if os.path.join(SKILL_DIR, skill.name) in os.listdir(SKILL_DIR):
            i = 1
            while os.path.join(SKILL_DIR, f"{skill.name}V{i}") in os.listdir(SKILL_DIR):
                i += 1
            new_name = f"{skill.name}V{i}"
            skill.code.replace(skill.name, new_name)
            skill.name = new_name

        # for now we just encode the docstring, assuming that it is descriptive enough...
        self.vector_db.add(
            documents=[skill.docstring],
            ids=[skill.name],
            metadatas=[
                {"name": skill.name, "is_core_primitive": skill.is_core_primitive}
            ],
        )
        skill.dump()

    def generate_description(self, task, skill_code):
        print(f"\033[33mGenerating skill description...\033[0m")

        messages = [
            {"role": "system", "content": skill_description_system_prompt},
            {
                "role": "user",
                "content": generate_skill_description_prompt(skill_code, task),
            },
        ]

        description = query_llm(messages)
        return description

    def retrieve_skills(self, query):
        """simplest retrieval tactic: query is a task"""
        RETRIEVAL_TOP_K = 100

        num_results = min(RETRIEVAL_TOP_K, self.vector_db.count())
        results = self.vector_db.query(
            query_texts=[query],
            n_results=num_results,
            # where={"is_core_primitive": True},
        )

        names = [metadata["name"] for metadata in results["metadatas"][0]]
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
    # SkillManager.delete_skill_library()
    # skill_manager = SkillManager()
    # skill_manager.add_core_primitives_to_library()
    pass
    # skill_manager = SkillManager()
    # print(skill_manager.get_all_skill_embeddings())
    # skills = skill_manager.retrieve_skills("build a cube")
    # print([skill.name for skill in skill_manager.all_skills])

    # print(skill_manager.skills)
    # print(skill_manager.num_skills)
    # print(skill_manager.vector_db.get())

    # for skill in skill_manager.skills:
    #     print(skill)

    # skill = Skill(
    #     "hello",
    #     "a hello function",
    #     "def hello()",
    #     "def eval_hello()",
    #     Image.new(mode="RGB", size=(640, 480)),
    # )
    # skill.dump()

    # ret_skill = Skill.retrieve_skill_with_name("hello")
    # print(ret_skill.eval_code)
