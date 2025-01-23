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
import pickle
from enum import Enum
from datetime import datetime

EXPERIENCE_DIR = "memory/trajectories"

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
)


class ExperienceTrace:
    """
    point is that - even when we iteratively solve a task by providing the agent with clues, we reset the environment state inbetween
    this is because the agent does not have a good way to perceive the environment at the moment

    how do we handle the skills?
    do we already store them separately?
    does it matter?
    """

    def __init__(self, env_config, task):
        self.env_config = env_config
        self.task = task
        self.attempts = []
        self.is_success = False

    def was_success(self, final_config):
        self.is_success = True
        self.final_config = final_config

        self.dump()

    def add_attempt_round(self, code_attempt, feedback):
        self.messages.append((code_attempt, feedback))

    def commit_to_memory(self):
        """extract skills from successful attempts, and add to preliminary skill database"""
        return

    def dump(self):
        timestamp = datetime.now().strftime("%m-%d-%H-%M-%S")
        with open(f"{EXPERIENCE_DIR}/{timestamp}.pkl", "wb") as file:
            pickle.dump(self, file)


class ExperienceManager:
    """
    handles interpretation and manipulation of experience traces to turn them into skills...
    """
