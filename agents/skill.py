import os
import shutil

from PIL import Image
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm, query_llm_structured
from dataclasses import dataclass
import uuid

import pydantic
import ast

from agents.experience import AttemptTrace


from prompts.base_prompt import (
    skill_description_system_prompt,
    generate_skill_description_prompt,
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)

ROOT_DIR = "/Users/maxfest/vscode/thesis/thesis/memory/skill_library/"


@dataclass
class Skill:
    id = uuid.uuid4()
    name: str
    docstring: str
    code: str
    calls: list[str]  # these need to be names of other functions
    # initially this will likely only be the id of the initial trace
    # as we perform skill distillation, the length of this list should increase
    trace_ids: list[uuid.uuid4] = []

    def __str__(self):
        return f"--- {self.name}: {self.description} ---"

    def dump(self):
        """store the skill in some readable way so we can inspect it..."""
        pass


class SkillManager:
    def __init__(self, ckpt_dir=ROOT_DIR):
        self.ckpt_dir = ckpt_dir

        self.skill_dir = os.path.join(ckpt_dir, "skills")
        self.vector_db_dir = os.path.join(ckpt_dir, "vector_db")

        os.makedirs(self.skill_dir, exist_ok=True)
        os.makedirs(self.vector_db_dir, exist_ok=True)

        self.retrieval_top_k = 3

        chroma_client = chromadb.PersistentClient(path=self.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="skill_library", embedding_function=openai_ef
        )

    @staticmethod
    def delete_skill_library(dir):
        try:
            shutil.rmtree(os.path.join(dir, "skills"))
            shutil.rmtree(os.path.join(dir, "vector_db"))
        except Exception as e:
            print(f"an error occurred {e}")

    @property
    def skills(self) -> list[Skill]:
        # TODO: actually print out all the programs available to the agent here...
        # this should only print action-related skills... - verification code?
        # should also retrieve core primitives...
        all_keys = [metadata["name"] for metadata in self.vector_db.get()["metadatas"]]
        skills = [Skill.retrieve_skill_with_name(name) for name in all_keys]
        return skills

    @property
    def num_skills(self):
        return self.vector_db.count()

    def add_skills(self, attempt: AttemptTrace):
        skills = SkillManager.extract_functions(attempt.code_string)

        # generate a description for each skill...
        # we will see once we actually try running the clustering algorithm
        # embedding directly might be better anyway...

        for skill in skills:
            skill.trace_ids.append(attempt.id)
            id = f"{skill.name}-{attempt.id}"
            self.vector_db.add(
                documents=[skill.code],
                ids=[id],
                metadatas=[{"function_name": skill.name, "attempt_id": attempt.id}],
            )

            with open(f"{self.skill_dir}/{id}.py", "w") as file:
                file.write(skill.code)

    def add_skill_to_library(self, skill: Skill):
        # skill_name, skill_description = self.generate_skill_name_and_description(
        #     task, skill_code
        # )

        # if skill_name in self.skills:
        #     print(f"\033[33mSkill {skill_name} already exists. Rewriting!\033[0m")
        #     self.vector_db.delete(ids=[skill_name])
        #     i = 2
        #     while f"{skill_name}V{i}.py" in os.listdir(
        #         os.path.join(self.ckpt_dir, "skills")
        #     ):
        #         i += 1
        #     dumped_skill_name = f"{skill_name}V{i}"
        # else:
        #     dumped_skill_name = skill_name

        self.vector_db.add(
            documents=[skill.code],
            ids=[skill.id],
            metadatas=[{"name": skill.name, "description": skill.description}],
        )
        skill.dump()

    # def generate_skill_name_and_description(self, task, skill_code):
    #     print(f"\033[33mGenerating skill description...\033[0m")

    #     messages = [
    #         {"role": "system", "content": skill_description_system_prompt},
    #         {
    #             "role": "user",
    #             "content": generate_skill_description_prompt(skill_code, task),
    #         },
    #     ]

    #     class GenerateSkillNameAndDescriptionReturn(pydantic.BaseModel):
    #         name: str
    #         description: str

    #     response = query_llm_structured(messages, GenerateSkillNameAndDescriptionReturn)
    #     return response.name, response.description

    def retrieve_skills(self, query):
        num_results = min(self.retrieval_top_k, self.vector_db.count())
        results = self.vector_db.query(query_texts=[query], n_results=num_results)

        # get skill code and description matching with the retrieved docs
        return [
            Skill.retrieve_skill_with_name(metadata[0]["name"])
            for metadata in results["metadatas"]
        ]

    @staticmethod
    def extract_functions(code_string) -> list[Skill]:
        # Parse the code string into an AST
        tree = ast.parse(code_string)

        # Extract all function definitions
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

        # Convert the AST nodes back to code strings
        extracted_functions = []
        for func in functions:
            # Use ast.get_source_segment to extract the function source code
            func_name = func.name
            func_source = ast.get_source_segment(code_string, func)
            doc_string = ast.get_docstring(func)
            calls = SkillManager.find_called_functions(func)
            extracted_functions.append(Skill(func_name, doc_string, func_source, calls))

        return extracted_functions

    @staticmethod
    def find_called_functions(node):
        called_functions = []

        # Traverse the AST for Call nodes
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                # Extract the function name
                if isinstance(n.func, ast.Name):
                    called_functions.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    called_functions.append(n.func.attr)

        return called_functions


code = """
def mult(a, b):
    print(a, b)
    hello(42)
    return a*b
    """
if __name__ == "__main__":
    # print(extract_functions(code))
    print(find_called_functions(ast.parse(code)))


if __name__ == "__main__":
    skill_manager = SkillManager()

    print(skill_manager.skills)
    print(skill_manager.num_skills)
    print(skill_manager.vector_db.get())

    for skill in skill_manager.skills:
        print(skill)

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
