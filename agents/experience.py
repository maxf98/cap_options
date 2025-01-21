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

import pickle
from enum import Enum


class ExperienceTrace:
    def __init__(self, env_task):
        self.env_task = env_task
        self.messages = []
        self.is_success = False
    
    def addAttempt(code_attempt, feedback):
        

    

