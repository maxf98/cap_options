import os
import shutil

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from utils.llm_utils import query_llm
from utils.cap_utils import get_calls, get_defs

import ast
import pickle
import inspect

from agents.model import Skill, TaskExample, InteractionTrace, EnvironmentConfiguration

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)


class MemoryManager:
    def __init__(self, root_dir="/Users/maxfest/vscode/thesis/thesis/memory/trained"):
        os.makedirs(root_dir, exist_ok=True)
        self.skill_manager = SkillManager(root_dir)
        self.config_manager = ConfigManager(root_dir)
        self.example_manager = ExamplesManager(
            root_dir, config_manager=self.config_manager
        )

        self.EXPERIENCE_DIR = os.path.join(root_dir, "trajectories")
        os.makedirs(self.EXPERIENCE_DIR, exist_ok=True)

    def add_skill(self, skill: Skill):
        self.skill_manager.add_skill_to_library(skill)

    def add_example(self, example: TaskExample):
        self.example_manager.add_example_to_library(example)

    def retrieve_skills(self, query, num_results=5) -> list[Skill]:
        return self.skill_manager.retrieve_skills(query, num_results=num_results)

    def retrieve_examples(self, query, num_results=5) -> list[TaskExample]:
        return self.example_manager.retrieve_similar_examples(
            query, num_results=num_results
        )

    def retrieve_configs(self, query, num_results=5) -> list[EnvironmentConfiguration]:
        return self.config_manager.retrieve_configs(query, num_results=num_results)

    def skill_task_examples(self, skill: Skill) -> list[TaskExample]:
        return [
            self.example_manager.retrieve_task_with_id(id)
            for id in skill._task_examples
        ]

    def add_trace(self, trace: InteractionTrace):
        trace.dump(self.EXPERIENCE_DIR)

    def get_all_traces(self) -> list[InteractionTrace]:
        traces = []
        for pickle_file in os.listdir(self.EXPERIENCE_DIR):
            with open(f"{self.EXPERIENCE_DIR}/{pickle_file}", "rb") as file:
                trace = pickle.load(file)
                traces.append(trace)
        return traces


class SkillManager:

    def __init__(self, MEMORY_DIR):
        self.SKILL_LIBRARY_DIR = f"{MEMORY_DIR}/skill_library/"
        self.SKILL_DIR = f"{self.SKILL_LIBRARY_DIR}/skills"
        self.vector_db_dir = os.path.join(self.SKILL_LIBRARY_DIR, "vector_db")

        os.makedirs(self.vector_db_dir, exist_ok=True)
        os.makedirs(self.SKILL_LIBRARY_DIR, exist_ok=True)
        os.makedirs(self.SKILL_DIR, exist_ok=True)

        chroma_client = chromadb.PersistentClient(path=self.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="skill_library", embedding_function=openai_ef
        )

        if self.num_skills == 0:
            self.add_core_primitives_to_library()

        all_skills = os.listdir(self.SKILL_DIR)
        stored_skills = self.vector_db.get()["ids"]
        # check if there are any deleted skills, and if so, remove them from the vector db
        for skill_name in stored_skills:
            if skill_name not in all_skills:
                print(f"deleting {skill_name}")
                self.vector_db.delete(ids=[skill_name])

        # check if there are any skills which have not been added to the vector db and if so add them (to enable manual adding of skills)
        for skill_name in all_skills:
            if skill_name not in stored_skills:
                with open(f"{self.SKILL_DIR}/{skill_name}/code.py", "r") as file:
                    code = file.read()
                skill = Skill.parse_function_string(code)
                self.add_skill_to_library(skill)

    @staticmethod
    def delete_skill_library(dir):
        try:
            shutil.rmtree(dir)
        except Exception as e:
            print(f"an error occurred {e}")

    def add_core_primitives_to_library(self):
        # only for retrieval purposes... functions are still actually called from core_primitives module
        from utils import core_primitives

        functions = inspect.getmembers(core_primitives, inspect.isfunction)
        for name, func in functions:
            if name not in core_primitives.__all__:
                continue

            path = f"{self.SKILL_DIR}/{name}"
            # delete if primitive was previously stored already...
            if name in os.listdir(self.SKILL_DIR):
                print("was in there already")
                self.vector_db.delete(ids=[name])
                shutil.rmtree(path)
            skill = Skill(
                name=name,
                code=inspect.getsource(func),
                is_core_primitive=True,
            )
            self.add_skill_to_library(skill)

    @property
    def all_skills(self) -> list[Skill]:
        all_keys = self.vector_db.get()["ids"]
        skills = [self.retrieve_skill_with_name(name) for name in all_keys]
        return skills

    @property
    def num_skills(self):
        return self.vector_db.count()

    def save_dir(self, skill_name):
        return f"{self.SKILL_DIR}/{skill_name}"

    def retrieve_skill_with_name(self, name) -> "Skill":
        # with open(f"{SKILL_DIR}/{name}/code.py", "r") as file:
        #     skill_code = file.read()
        with open(f"{self.SKILL_DIR}/{name}/skill.pkl", "rb") as file:
            skill = pickle.load(file)
        with open(f"{self.SKILL_DIR}/{name}/code.py", "r") as file:
            skill.code = file.read()

        return skill

    def delete_skill(self, name: str):
        if name in os.listdir(self.SKILL_DIR):
            print(f"deleting {name}")
            skill_dir = os.path.join(self.SKILL_DIR, name)
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

        skill.dump(self.save_dir(skill.name))

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
        skills = [self.retrieve_skill_with_name(name) for name in names]
        # filter out None values and return
        return [skill for skill in skills if skill is not None]

    def get_all_skill_embeddings(self):
        results = self.vector_db.get(
            include=["embeddings"],
            where={
                "is_core_primitive": False
            },  # we don't want to cluster/rewrite core primitives - they are simply given...
        )

        return (results["ids"], results["embeddings"])

    def resolve_dependencies(self, code_str):
        """
        collects the entire dependency tree needed to run the code string
        """

        dependencies = []
        skill_dependencies = []
        new_dependencies = list(get_calls(code_str))

        all_skills = os.listdir(self.SKILL_DIR)

        while len(new_dependencies) > 0:
            skill_name = new_dependencies.pop(0)
            if skill_name not in dependencies and skill_name in all_skills:
                skill = self.retrieve_skill_with_name(skill_name)
                if not skill.is_core_primitive:
                    dependencies.append(skill.name)
                    skill_dependencies.append(skill)
                deps = list(get_calls(skill.code))
                new_dependencies.extend(deps)

        print(dependencies)
        return skill_dependencies

    def outside_calls(self, code_str):
        calls = self.get_skill_calls(code_str)
        defs = get_defs(code_str)
        calls_not_in_defs = [call for call in calls if call not in defs]
        return calls_not_in_defs

    def get_skill_calls(self, code_str, func_names: bool = False):
        calls = get_calls(code_str)
        skills = self.all_skills
        skill_names = [skill.name for skill in skills]
        skill_calls = [call for call in calls if call in skill_names]
        if func_names:
            return skill_calls
        called_skills = [self.retrieve_skill_with_name(name) for name in skill_calls]
        return called_skills


class ConfigManager:
    """stores configs or part configs for retrieval"""

    def __init__(self, MEMORY_DIR):
        self.CONFIG_LIBRARY_DIR = f"{MEMORY_DIR}/config_library"
        self.vector_db_dir = os.path.join(self.CONFIG_LIBRARY_DIR, "vector_db")
        self.configs_dir = os.path.join(self.CONFIG_LIBRARY_DIR, "configs")
        os.makedirs(self.configs_dir, exist_ok=True)
        os.makedirs(self.vector_db_dir, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=self.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="configs", embedding_function=openai_ef
        )

    def store_final_config(self, task_example: TaskExample):
        """store in vector db for retrieval and write to config list"""
        description = self.generate_final_config_description(task_example.task)
        config = task_example.final_config
        config.description = description

        self.vector_db.upsert(
            documents=[description],
            ids=[str(config.id)],
        )

        with open(f"{self.CONFIG_LIBRARY_DIR}/configs.txt", "a") as file:
            file.write(f"{description}\n")

        config.dump(f"{self.configs_dir}/{config.id}.pkl")

    def retrieve_configs(
        self, config_prompt, num_results=5
    ) -> list[EnvironmentConfiguration]:
        num_results = min(num_results, self.vector_db.count())
        if num_results == 0:
            return []

        results = self.vector_db.query(
            query_texts=[config_prompt],
            n_results=num_results,
        )
        ids = results["ids"][0]
        configs = [self.retrieve_config_with_id(id) for id in ids]
        return [config for config in configs if config is not None]

    def generate_final_config_description(self, task):
        """e.g. build a jenga tower"""
        # from prompts.config import generate_config_description

        # messages = [{"role": "user", "content": generate_config_description(task)}]
        # description = query_llm(messages)
        # THIS DIDN'T WORK AT ALL - just ask the user...
        description = input("give a description of the config to be stored...")
        return description

    def retrieve_config_with_id(self, id) -> EnvironmentConfiguration:
        if f"{id}.pkl" not in os.listdir(self.configs_dir):
            return None

        with open(f"{self.configs_dir}/{id}.pkl", "rb") as file:
            config = pickle.load(file)

        return config


class ExamplesManager:

    def __init__(self, MEMORY_DIR, config_manager: ConfigManager):
        self.EXAMPLE_LIBRARY_DIR = f"{MEMORY_DIR}/example_library"
        self.EXAMPLE_DIR = f"{self.EXAMPLE_LIBRARY_DIR}/examples"
        self.vector_db_dir = os.path.join(self.EXAMPLE_LIBRARY_DIR, "vector_db")

        os.makedirs(self.vector_db_dir, exist_ok=True)
        os.makedirs(self.EXAMPLE_LIBRARY_DIR, exist_ok=True)
        os.makedirs(self.EXAMPLE_DIR, exist_ok=True)
        chroma_client = chromadb.PersistentClient(path=self.vector_db_dir)
        self.vector_db = chroma_client.get_or_create_collection(
            name="examples", embedding_function=openai_ef
        )

        self.config_manager = config_manager

    def add_unstored_examples_to_library(self):
        """if we manually added few-shot examples (as code pieces in to_be_added), call this function to add them to the skill library"""
        add_dir = f"{self.EXAMPLE_LIBRARY_DIR}/add"
        examples = os.listdir(add_dir)
        for example in examples:
            task_example = TaskExample.parse_code_file(f"{add_dir}/example")
            self.add_example_to_library(task_example)

    @property
    def all_examples(self) -> list[TaskExample]:
        ids = self.vector_db.get()["ids"]
        examples = [self.retrieve_task_with_id(id) for id in ids]
        return examples

    def add_example_to_library(self, example: TaskExample):
        # description = self.config_manager.store_final_config(example)
        task_example_description = f"{example.task}"
        self.vector_db.upsert(
            documents=[task_example_description], ids=[str(example.id)]
        )
        example.dump(self.save_dir(example.id))

    def retrieve_similar_examples(self, task, num_results=5) -> TaskExample:
        num_results = min(num_results, self.vector_db.count())
        if num_results == 0:
            return []

        results = self.vector_db.query(
            query_texts=[task],
            n_results=num_results,
        )
        ids = results["ids"][0]
        task_examples = [self.retrieve_task_with_id(id) for id in ids]
        return [example for example in task_examples if example is not None]

    def delete_example(self, example: TaskExample):
        if str(example.id) in os.listdir(self.EXAMPLE_DIR):
            print(f"deleting {example.task}")
            example_dir = os.path.join(self.EXAMPLE_DIR, str(example.id))
            shutil.rmtree(example_dir)
            self.vector_db.delete(ids=[str(example.id)])

    def delete_examples_wo_file(self):
        ids = self.vector_db.get()["ids"]
        for id in ids:
            if self.retrieve_task_with_id(id) is None:
                print("deleting")
                self.vector_db.delete([id])

    def save_dir(self, example_id):
        return f"{self.EXAMPLE_DIR}/{example_id}"

    def retrieve_task_with_id(self, id) -> "TaskExample":
        if id not in os.listdir(self.EXAMPLE_DIR):
            return None

        with open(f"{self.EXAMPLE_DIR}/{id}/example.pkl", "rb") as file:
            example = pickle.load(file)

        return example


code = """
blocks = get_blocks_by_color()
workspace_middle = parse_location_description('middle')
block_size = get_object_size(blocks[0])
base_pose = Pose(Point3D(workspace_middle.x - (block_size[0] * 1.5 + 0.005) / 2, workspace_middle.y, block_size[2] / 2), Rotation.identity())
build_jenga_tower(blocks, base_pose)
"""


if __name__ == "__main__":
    memory_dir = "/Users/maxfest/vscode/thesis/thesis/memory/trained"
    memory_manager = MemoryManager()

    # memory_manager.skill_manager.vector_db.delete(ids=["pick_up_special_object"])

    # memory_manager.skill_manager.vector_db.delete(ids=["get_object_size"])
    # skill = memory_manager.skill_manager.retrieve_skill_with_name("get_object_size")
    # print(skill.code)
    # memory_manager.skill_manager.add_skill_to_library(skill)

    # print(
    #     Skill.print_skills(
    #         memory_manager.retrieve_skills("get pixels to build letter", num_results=10)
    #     )
    # )

    # examples = memory_manager.retrieve_examples("build a jenga tower")
    # print(examples)

    # task_example = examples[0]
    # config_manager = ConfigManager(memory_dir)
    # config_manager.store_final_config(task_example)

    # configs = config_manager.retrieve_configs("build a jenga tower")
    # print(configs)
    # from environments.environment import Environment
    # from tasks.task import Task

    # env = Environment(
    #     "environments/assets",
    #     disp=True,
    #     shared_memory=False,
    #     hz=480,
    #     record_cfg={
    #         "save_video": False,
    #         "save_video_path": "${data_dir}/${task}-cap/videos/",
    #         "add_text": True,
    #         "add_task_text": True,
    #         "fps": 20,
    #         "video_height": 640,
    #         "video_width": 720,
    #     },
    # )

    # task = Task()
    # task.config = configs[0]
    # env.set_task(task)
    # env.reset()

    # print("\n".join([example.task for example in examples]))

    # skill = memory_manager.skill_manager.retrieve_skill_with_name(
    #     "arrange_blocks_in_circle"
    # )
    # print(memory_manager.skill_task_examples(skill))
    # skill_manager.delete_skill("get_objects_in_area")
    # skill_manager.add_core_primitives_to_library()
    # skills = skill_manager.all_skills
    # print(skills)

    # example_manager = ExamplesManager()
    # examples = example_manager.all_examples
    # print(examples)
    # example_manager.add_example_to_library(TaskExample("hello", "", None, None))
    # res = skill_manager.all_skills
    # print(res)
