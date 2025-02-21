from tasks.task import Task, GeneratedTask
from agents.model.environment_configuration import EnvironmentConfiguration
from environments.environment import Environment
from prompts.task_gen_prompt import task_setup_system_prompt
from utils.llm_utils import query_llm, parse_code_response


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

    def __init__(self):
        self.current_task = Task()
        self.setup_environment()
        self.reset()

    def setup_environment(self):
        env = Environment(
            "environments/assets",
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
        return config

    def get_current_config(self) -> EnvironmentConfiguration:
        return self.env.task.get_current_configuration(self.env)

    def initialise_task(self, task_str: str, task_setup_prompt: str):
        task = GeneratedTask()
        task.set_lang_goal(task_str)
        setup_code = self.generate_task_setup_code(task_setup_prompt)
        task.set_task_setup_code(setup_code)

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

    env = Environment(
        "/Users/maxfest/vscode/thesis/ravens/environments/assets",
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

    task = GeneratedTask()
    task.set_lang_goal("hello")
    task.set_task_setup_code(code)

    env.set_task(task)
    env.reset()

    time.sleep(2)
