from prompts.base_prompt import (
    parse_completion_prompt,
    critic_system_prompt,
    explain_failure_prompt,
)
from utils.llm_utils import query_llm, parse_code_response
from utils.cap_utils import encode_image, code_exec_with_bug_fix


class Critic:
    def __init__(self, mode="auto"):
        self.mode = mode

    def set_env_and_task(self, code_env, task):
        self.task = task
        self.code_env = code_env

    def human_check_task_success(self):
        # ask the human to evaluate whether the task was achieved successfully
        confirmed = False
        success = False
        critique = ""
        while not confirmed:
            success = input("Success? (y/n)")
            success = success.lower() == "y"
            critique = input("Enter your critique:")
            print(f"Success: {success}\nCritique: {critique}")
            confirmed = input("Confirm? (y/n)") in ["y", ""]
        return success, critique

    def ai_check_task_success(self, task_attempt, image) -> tuple[bool, str, str]:
        """
        make a return type here...
        maybe change the pipeline a little here...
        first image check => if possibly successful, write code => if unsuccessful, give feedback
        """
        messages = [{"role": "system", "content": critic_system_prompt}]

        b64img = encode_image(image)

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": parse_completion_prompt(self.task, task_attempt),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64img}"},
                    },
                ],
            }
        )
        response = query_llm(messages)
        code_str = parse_code_response(response)

        exec(code_str, self.code_env)

        code_task_success = self.code_env["task_success"]

        if not code_task_success:
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": explain_failure_prompt})

            feedback = query_llm(messages)
            return False, feedback, code_str

        return code_task_success, None, code_str

    def check_task_success(self):
        if self.mode == "manual":
            self._human_check_task_success()
        elif self.mode == "auto":
            self._ai_check_task_success()
