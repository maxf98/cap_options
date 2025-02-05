"""
Store experience traces
Must include: initial environment setup - in this setting: the Task
All LLM interactions - i.e. sequence of user prompts and responses
success/failure - this could also be automated with reward functions, but human interaction will be necessary anyway
summary of interaction (for retrieval)

this can be used for few-shot examples
and for experience distillation by generating skills

and for retrieval of few-shot examples
"""

import os
import uuid
import pickle
from datetime import datetime

from tasks.task import EnvironmentConfiguration


EXPERIENCE_DIR = "memory/trajectories"
os.makedirs(EXPERIENCE_DIR, exist_ok=True)

class AttemptTrace:
    initial_config: EnvironmentConfiguration
    code_string: str
    final_config: EnvironmentConfiguration
    feedback: str = None
    id: int = None

    @property
    def is_success(self):
        return self.feedback == "success"

    @property
    def gave_feedback(self):
        return self.feedback not in ["success", "give-up", "try-again"]
    
    @staticmethod
    def get_attempt_trace(id):
        trace_id = id[:-1]
        path = f"{EXPERIENCE_DIR}/{trace_id}.pkl"
        if os.path.isfile(path):
            with open(path, "rb") as file:
                trace = pickle.load(file)
                return trace.attempts[id[-1]]


class InteractionTrace:
    """
    point is that - even when we iteratively solve a task by providing the agent with clues, we reset the environment state inbetween
    this is because the agent does not have a good way to perceive the environment at the moment

    we store the traces for skill distillation -
    the functions generated throughout the first stage of skill collection will likely not be general enough
    storing configs allows us to -test- the distilled skills, by rewriting the code to use them
    that's also when we get the few-shot examples

    this is more for future uses, e.g. checking the number of corrections required to get what you want
    """

    """
    TODO: fix the whole business with the ids... just feels off
    """

    def __init__(self, task):
        self.id = uuid.uuid4()
        self.task = task
        self.attempts: list[AttemptTrace] = []
        self.timestamp = datetime.now().strftime("%m-%d-%H-%M-%S")

    @property
    def successful_attempt(self) -> AttemptTrace | None:
        return next((a for a in self.attempts if a.is_success), None)
    
    def add_attempt(self, attempt: AttemptTrace):
        attempt.id = str(self.id) + str(self.attempts.count)
        self.attempts.append(attempt)

    def dump(self):
        with open(f"{EXPERIENCE_DIR}/{self.id}.pkl", "wb") as file:
            pickle.dump(self, file)


# should we also store few-shot examples?


# handle feedback in different ways - e.g. extract insights
# if attempt.gave_feedback:
#     messages = [
#         {"role": "system", "content": extract_insights_system_prompt},
#         {
#             "role": "user",
#             "content": extract_insights_prompt(
#                 self.cur_interaction.task, attempt.code_string, attempt.feedback
#             ),
#         },
#     ]

#     class ExtractedInsights(BaseModel):
#         produced_insight: bool
#         insight: str

#     response = query_llm_structured(messages, ExtractedInsights)

#     if response.produced_insight:
#         with open("memory/insights.txt", "a") as file:
#             file.write(f"{response.insight}\n")


if __name__ == "__main__":
    id = uuid.uuid4()
    print(str(id) + 2)