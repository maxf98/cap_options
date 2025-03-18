"""
no need to store all the intermediate code strings right?
but the feedback probably... the number of correction rounds
whether in the end it was successful or not...
which skills were ultimately used...
"""

import os
import uuid
import pickle
from datetime import datetime

from agents.model.environment_configuration import EnvironmentConfiguration
from agents.model.example import TaskExample
from dataclasses import dataclass


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

    def __init__(self, task, initial_config: EnvironmentConfiguration):
        self.id = uuid.uuid4()
        self.task = task
        self.initial_config = initial_config
        self.feedbacks = []
        self.timestamp = datetime.now().strftime("%m-%d-%H-%M-%S")
        self.example = None

    @property
    def is_success(self):
        return self.example is not None

    def add_feedback_round(self, feedback):
        self.feedbacks.append(feedback)

    def success(self, example: TaskExample) -> str:
        self.example = example

    def dump(self, dir):
        with open(f"{dir}/{self.id}.pkl", "wb") as file:
            pickle.dump(self, file)
