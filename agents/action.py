from utils.llm_utils import query_llm, parse_code_response
from utils.cap_utils import code_exec_with_bug_fix
from prompts.base_prompt import actor_system_prompt, generate_action_plan_prompt


class Actor:
    """
    responsible for handling the main action loop
    i.e. integrating and potentially keeping track of new environment information
    actually not completely sure what this class should contain right now...
    """

    def __init__(self):
        self.messages = [{"role": "system", "content": actor_system_prompt}]

    def set_env_and_task(self, env, task):
        self.task = task
        self.env = env
        self.messages.append(
            {"role": "user", "content": generate_action_plan_prompt(task)}
        )

    def attempt_task(self, feedback=None):
        """where all the actual interaction logic should go...
        Possible augmentations: chain-of-thought prompting, structured outputs, generalise to learn skills...
        feedback: str
            if task was previously attempted (unsuccessfully), add feedback from last round
        """

        # TODO: update prompt to use chain of thought... i.e. use more output tokens for same task

        if feedback:
            self.messages.append({"role": "user", "content": feedback})

        response = query_llm(self.messages)
        code_str = parse_code_response(response)

        code_exec_with_bug_fix(code_str, self.env)

        self.messages.append({"role": "assistant", "content": response})
        return code_str
