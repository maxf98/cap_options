import os
import shutil

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm

import ast
import pickle
import inspect

from agents.model.skill import Skill
from agents.model.example import TaskExample

from prompts.skill import (
    skill_description_system_prompt,
    generate_skill_description_prompt,
)

from agents.model.config import (
    SKILL_LIBRARY_DIR,
    EXAMPLE_LIBRARY_DIR,
    SKILL_DIR,
    CONFIG_LIBRARY_DIR
)


openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)


class SkillManager:
    vector_db_dir = os.path.join(SKILL_LIBRARY_DIR, "vector_db")

    def __init__(self):
        os.makedirs(self.vector_db_dir, exist_ok=True)

        chroma_client = chromadb.PersistentClient(path=self.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="skill_library", embedding_function=openai_ef
        )

    @staticmethod
    def delete_skill_library():
        try:
            shutil.rmtree(SKILL_LIBRARY_DIR)
        except Exception as e:
            print(f"an error occurred {e}")

    def add_core_primitives_to_library(self):
        # only for retrieval purposes... functions are still actually called from core_primitives module
        from utils import core_primitives
        os.makedirs(SKILL_LIBRARY_DIR, exist_ok=True)
        os.makedirs(SKILL_DIR, exist_ok=True)

        functions = inspect.getmembers(core_primitives, inspect.isfunction)
        for name, func in functions:
            if name not in core_primitives.__all__:
                continue

            path = f"{SKILL_DIR}/{name}"
            # delete if primitive was previously stored already...
            trace_ids = []
            if name in os.listdir(SKILL_DIR):
                print("was in there already")
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
        all_keys = self.vector_db.get()["ids"]
        skills = [Skill.retrieve_skill_with_name(name) for name in all_keys]
        return skills

    @property
    def num_skills(self):
        return self.vector_db.count()

    # def add_skills_from_trace(self, trace: InteractionTrace):
    #     """extract skills from a (successful) attempt trace"""
    #     if trace.successful_attempt is None:
    #         return
    #     attempt = trace.successful_attempt

    #     tree = ast.parse(attempt.code_string)
    #     nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    #     for node in nodes:
    #         skill_str = ast.get_source_segment(attempt.code_string, node)
    #         skill = Skill.parse_function_string(skill_str)

    #         skill.trace_ids.append(attempt.id)  # kind of pointless, because incomplete
    #         self.add_skill_to_library(skill)

    def delete_skill(self, name: str):
        if name in os.listdir(SKILL_DIR):
            print(f"deleting {name}")
            skill_dir = os.path.join(SKILL_DIR, name)
            shutil.rmtree(skill_dir)
            self.vector_db.delete(ids=[name])

    def add_skill_to_library(self, skill: Skill):
        # need to check if a function with this name has been generated before...
        # technically we are preventing this from happening... this is probably unnecessary
        self.vector_db.upsert(
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


class ExamplesManager:
    vector_db_dir = os.path.join(EXAMPLE_LIBRARY_DIR, "vector_db")

    def __init__(self):
        os.makedirs(self.vector_db_dir, exist_ok=True)
        chroma_client = chromadb.PersistentClient(
            path=self.vector_db_dir
        )
        self.vector_db = chroma_client.get_or_create_collection(
            name="examples", embedding_function=openai_ef
        )

    def add_example_to_library(self, example: TaskExample):
        self.vector_db.add(documents=[example.task], ids=[str(example.id)])
        example.dump()

    def retrieve_similar_examples(self, task, num_results=5) -> TaskExample:
        num_results = min(num_results, self.vector_db.count())
        results = self.vector_db.query(
            query_texts=[task],
            n_results=num_results,
        )
        ids = results["ids"][0]
        task_examples = [TaskExample.retrieve_task_with_id(id) for id in ids]
        return task_examples
    

class ConfigManager:
    """stores configs or part configs for retrieval"""
    vector_db_dir = os.path.join(CONFIG_LIBRARY_DIR, "vector_db")

    def __init__(self):
        os.makedirs(self.vector_db_dir, exist_ok=True)
        chroma_client = chromadb.PersistentClient(
            path=self.vector_db_dir
        )
        self.vector_db = chroma_client.get_or_create_collection(
            name="configs", embedding_function=openai_ef
        )

        os.makedirs(os.path.join(CONFIG_LIBRARY_DIR, "configs.txt"))

    def store_config(self, config, description):
        """store in vector db for retrieval and write to config list"""
        pass

    def retrieve_configs(self, query):
        pass



class InsightsManager:
    """stores general behaviour guidelines... leave todo for now"""
    def __init__(self):
        pass


code = """
def mult(a, b):
    print(a, b)
    hello(42)
    return a*b
    """

if __name__ == "__main__":
    skill_manager = SkillManager()

    example_manager = ExamplesManager()
    example_manager.add_example_to_library(TaskExample("hello", "", None, None))
    # res = skill_manager.all_skills
    # print(res)
