import os
import shutil

from PIL import Image
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm, query_llm_structured

import pydantic


from prompts.base_prompt import (
    skill_description_system_prompt,
    generate_skill_description_prompt,
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)

ROOT_DIR = "/Users/maxfest/vscode/thesis/thesis/memory/skill_library/"


class Skill:
    def __init__(
        self, name, description, skill_code, eval_code, success_image, folder_name=None
    ):
        self.name = name
        self.description = description
        self.skill_code = skill_code
        self.eval_code = eval_code
        self.success_image = success_image

        self.skill_dir = (
            f"{ROOT_DIR}/skills/{name if folder_name is None else folder_name}"
        )
        os.makedirs(self.skill_dir, exist_ok=True)

    def dump(self):
        # we choose a readable storage method
        with open(f"{self.skill_dir}/description.txt", "w") as file:
            file.write(self.description)
        with open(f"{self.skill_dir}/skill_code.py", "w") as file:
            file.write(self.skill_code)
        with open(f"{self.skill_dir}/eval_code.py", "w") as file:
            file.write(self.eval_code)

        img = Image.fromarray(self.success_image)
        img.save(f"{self.skill_dir}/success_image.jpg")

    def __str__(self):
        return f"--- {self.name}: {self.description} ---"

    @classmethod
    def retrieve_skill_with_name(cls, name):
        dir = f"{ROOT_DIR}/skills/{name}"
        with open(f"{dir}/description.txt", "r") as file:
            description = file.read()
        with open(f"{dir}/skill_code.py", "r") as file:
            skill_code = file.read()
        with open(f"{dir}/eval_code.py", "r") as file:
            eval_code = file.read()

        success_image = Image.open(f"{dir}/success_image.jpg")

        return Skill(name, description, skill_code, eval_code, success_image)


class SkillManager:
    def __init__(self, ckpt_dir=ROOT_DIR, reset=True):
        self.ckpt_dir = ckpt_dir
        if reset:
            SkillManager.delete_skill_library(self.ckpt_dir)

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

    def add_skill_to_library(self, task, skill_code, eval_code, success_image):
        skill_name, skill_description = self.generate_skill_name_and_description(
            task, skill_code
        )

        if skill_name in self.skills:
            print(f"\033[33mSkill {skill_name} already exists. Rewriting!\033[0m")
            self.vector_db.delete(ids=[skill_name])
            i = 2
            while f"{skill_name}V{i}.py" in os.listdir(
                os.path.join(self.ckpt_dir, "skills")
            ):
                i += 1
            dumped_skill_name = f"{skill_name}V{i}"
        else:
            dumped_skill_name = skill_name

        self.vector_db.add(
            documents=[skill_description],
            ids=[skill_name],
            metadatas=[{"name": dumped_skill_name}],
        )

        skill = Skill(
            skill_name,
            skill_description,
            skill_code,
            eval_code,
            success_image,
            folder_name=dumped_skill_name,
        )
        skill.dump()

    def parse_skill_name(code):
        return ""

    def generate_skill_name_and_description(self, task, skill_code):
        print(f"\033[33mGenerating skill description...\033[0m")

        messages = [
            {"role": "system", "content": skill_description_system_prompt},
            {
                "role": "user",
                "content": generate_skill_description_prompt(skill_code, task),
            },
        ]

        class GenerateSkillNameAndDescriptionReturn(pydantic.BaseModel):
            name: str
            description: str

        response = query_llm_structured(messages, GenerateSkillNameAndDescriptionReturn)
        return response.name, response.description

    def retrieve_skills(self, query):
        num_results = min(self.retrieval_top_k, self.vector_db.count())
        results = self.vector_db.query(query_texts=[query], n_results=num_results)

        # get skill code and description matching with the retrieved docs
        return [
            Skill.retrieve_skill_with_name(metadata[0]["name"])
            for metadata in results["metadatas"]
        ]


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
