import os
import shutil

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm

import ast
import pickle
import inspect

from agents.experience import AttemptTrace, InteractionTrace
from agents.model.skill import Skill

from prompts.skill import (
    skill_description_system_prompt,
    generate_skill_description_prompt,
)

from config import (
    SKILL_LIBRARY_DIR,
    EXAMPLE_LIBRARY_DIR,
    MEMORY_DIR,
    SKILL_DIR,
    EXAMPLE_DIR,
)

import uuid


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)


class SkillManager:
    vector_db_dir = os.path.join(SKILL_LIBRARY_DIR, "vector_db")
    example_vector_db_dir = os.path.join(EXAMPLE_LIBRARY_DIR, "vector_db")

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
            shutil.rmtree(SKILL_LIBRARY_DIR)
            shutil.rmtree(SkillManager.vector_db_dir)
        except Exception as e:
            print(f"an error occurred {e}")

    def add_core_primitives_to_library(self):
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

    def retrieve_skills(
        self, query, only_core_primitives=False, num_results=5
    ) -> list[Skill]:
        """simplest retrieval tactic: query is a task"""

        num_results = min(num_results, self.vector_db.count())

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
