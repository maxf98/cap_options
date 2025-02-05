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
from enum import Enum
from datetime import datetime

from utils.cap_utils import extract_functions
from utils.llm_utils import query_llm_structured
from utils import core_primitives
from tasks.task import EnvironmentConfiguration

from prompts.base_prompt import extract_insights_system_prompt, extract_insights_prompt

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from pydantic import BaseModel

from dataclasses import dataclass


EXPERIENCE_DIR = "memory/trajectories"
TRACES_DIR = os.path.join(EXPERIENCE_DIR, "traces")
SKILLS_DIR = os.path.join(EXPERIENCE_DIR, "skills")
# make sure the directories exist...
os.makedirs(TRACES_DIR, exist_ok=True)
os.makedirs(SKILLS_DIR, exist_ok=True)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)


@dataclass
class AttemptTrace:
    initial_config: EnvironmentConfiguration
    code_string: str
    final_config: EnvironmentConfiguration
    feedback: str = None
    id = uuid.uuid4()

    @property
    def is_success(self):
        return self.feedback == "success"

    @property
    def gave_feedback(self):
        return self.feedback not in ["success", "give-up", "try-again"]


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

    def __init__(self, task):
        self.id = uuid.uuid4()
        self.task = task
        self.attempts: list[AttemptTrace] = []
        self.timestamp = datetime.now().strftime("%m-%d-%H-%M-%S")

    @property
    def successful_attempt(self) -> AttemptTrace | None:
        return next((a for a in self.attempts if a.is_success), None)

    def dump(self):
        with open(f"{TRACES_DIR}/{self.timestamp}.pkl", "wb") as file:
            pickle.dump(self, file)


class ExperienceManager:
    """
    handles interpretation and manipulation of experience traces to turn them into skills or insights
    insights may be viewed as general conditions on the robot behaviour
    """

    def __init__(self, skill_manager):
        self.skill_manager = skill_manager

    def start_interaction(self, task):
        self.cur_interaction = InteractionTrace(task)

    def add_attempt(self, attempt: AttemptTrace):
        self.cur_interaction.attempts.append(attempt)

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

    def wrap_up(self):
        """store the trace, in case we want to use it later on
        commit the preliminary skills to memory... or just commit them right away?
        from successful traces?
        need to keep mapping from skill to successful trace...
        """
        trace = self.cur_interaction

        if trace.successful_attempt:
            self.skill_manager.add_skills(attempt)
            attempt = trace.successful_attempt
            skills = extract_functions(attempt.code_string)

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

                with open(f"{SKILLS_DIR}/{id}.py", "w") as file:
                    file.write(skill.code)

        trace.dump()  # in case we want to reuse later (for example to extract insights, common feedback, ...)

        # should we also store few-shot examples?
