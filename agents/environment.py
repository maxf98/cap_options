from tasks.task import Task, GeneratedTask
from agents.model import EnvironmentConfiguration, TaskExample
from environments.environment import Environment
from agents.memory import MemoryManager
from prompts.task_gen_prompt import task_setup_system_prompt
from utils.llm_utils import query_llm, parse_code_response

from tasks.tasks.place_blocks import Place2Blocks


class EnvironmentAgent:
    """
    responsible for aiding in environment setup
    like the actor, should get better and better at setting the environment to a specific configuration
    tailored to the creator - it learns a specific language, i.e. a mapping from NL to env-config
    (through API + retrieval - including past configs)

    for now just a two-pass attempt
    first: retrieve previous configs
    if none chosen, generate new from string
    """

    def __init__(self, memory_manager: MemoryManager):
        self.current_task = Task()
        self.setup_environment()
        self.reset()
        self.memory_manager = memory_manager

    def parse_task_dummy(self):
        self.current_task = Place2Blocks()

    def parse_task(self):
        task_str = input("give the task to be solved:\n")
        task = self.parse_env_setup()
        task.set_lang_goal(task_str)
        self.current_task = task

    def parse_env_setup(self, allow_existing_configs: bool = False):
        env_setup_prompt = input(
            "how should the environment be set up? ('keep' for same setup)\n"
        )

        if env_setup_prompt == "keep":
            return self.current_task
        elif env_setup_prompt == "none":
            task = Task()
            return task

        if allow_existing_configs:
            existing_configs = self.memory_manager.retrieve_configs(
                env_setup_prompt, num_results=10
            )
            print(
                f"existing configs\n {'\n'.join([config.description for config in existing_configs])}"
            )
            use_existing_config = input(
                "use existing config? (provide index of config or none if don't want to use) \n"
            )

            if use_existing_config != "none":
                config = existing_configs[int(use_existing_config)]
                task = GeneratedTask()
                task.set_config(config)

                modify_config = input("modify the config? (prompt or none)")

                if modify_config != "none":
                    setup_code = self.generate_task_setup_code(modify_config)
                    task.set_task_setup_code(setup_code)

                return task

        task = GeneratedTask()
        setup_code = self.generate_task_setup_code(env_setup_prompt)
        print(setup_code)
        task.set_task_setup_code(setup_code)
        return task

    def setup_environment(self):
        env = Environment(
            "/Users/maxfest/vscode/thesis/thesis/environments/assets",
            disp=True,
            shared_memory=False,
            hz=480,
            record_cfg={
                "save_video": False,
                "save_video_path": "${data_dir}/${task}-cap/videos/",
                "add_text": True,
                "add_task_text": True,
                "fps": 20,
                "video_height": 640,
                "video_width": 720,
            },
        )

        self.env = env

    def reset(self):
        self.env.set_task(self.current_task)
        self.env.reset()
        config = self.get_current_config()
        self.config_stack = [config]
        return config

    def pop_config(self) -> EnvironmentConfiguration:
        # resets to last config so agent can try again from there
        config = self.configs[-1]
        self.set_to_task_and_config(self.current_task.lang_goal, config)

    def get_current_config(self) -> EnvironmentConfiguration:
        return self.env.task.get_current_configuration(self.env)

    def set_to_task_and_config(self, task: str, config: EnvironmentConfiguration):
        reset_task = Task()
        reset_task.config = config
        reset_task.lang_goal = task
        self.current_task = reset_task
        self.reset()

    def restore_task_from_example(self, task: TaskExample):
        self.current_task = task

    def set_task(self, task: Task):
        self.current_task = task

    def generate_task_setup_code(self, task_setup_prompt: str):
        messages = [
            {"role": "system", "content": task_setup_system_prompt},
            {"role": "user", "content": task_setup_prompt},
        ]

        response = query_llm(messages)
        code = parse_code_response(response)
        return code


code = """
self.add_block(env, "green")
self.add_block(env, "blue")
"""


if __name__ == "__main__":
    import time

    env_agent = EnvironmentAgent(MemoryManager())

    env_agent.parse_task()

    env_agent.reset()

    time.sleep(5)
