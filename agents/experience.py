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
from utils.task_primitives import EnvironmentConfiguration

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

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

    @property
    def is_success(self):
        return self.feedback == "success"

class InteractionTrace:
    """
    point is that - even when we iteratively solve a task by providing the agent with clues, we reset the environment state inbetween
    this is because the agent does not have a good way to perceive the environment at the moment

    we store the traces for skill distillation - 
    the functions generated throughout the first stage of skill collection will likely not be general enough
    storing configs allows us to -test- the distilled skills, by rewriting the code to use them
    that's also when we get the few-shot examples
    """

    def __init__(self, task):
        self.id = uuid.uuid4()
        self.task = task
        self.attempts: list[AttemptTrace] = []
        self.timestamp = datetime.now().strftime("%m-%d-%H-%M-%S")
        self.is_success = False

    def add_attempt(self, attempt: AttemptTrace):
        self.attempts.append(attempt)
        self.is_success = attempt.is_success

    @property
    def successful_attempt(self) -> AttemptTrace | None:
        return next((a for a in self.attempts if a.is_success), None)

    def dump(self):
        with open(f"{TRACES_DIR}/{self.timestamp}.pkl", "wb") as file:
            pickle.dump(self, file)
        
        if self.successful_attempt:
            with open(f"{SKILLS_DIR}/{self.timestamp}.py", "w") as file:
                file.write(f' """\ntask:\n {self.task} \n""" \n\n ')
                file.write(self.successful_attempt.code_string)


# class ExperienceManager:
#     """
#     handles interpretation and manipulation of experience traces to turn them into skills...
#     """

#     def __init__(self):
#         self.traces_dir = os.path.join(EXPERIENCE_DIR, "traces")
#         self.skill_dir = os.path.join(EXPERIENCE_DIR, "skills")
#         self.vector_db_dir = os.path.join(EXPERIENCE_DIR, "vector_db")

#         os.makedirs(self.traces_dir, exist_ok=True)
#         os.makedirs(self.skill_dir, exist_ok=True)
#         os.makedirs(self.vector_db_dir, exist_ok=True)

#         chroma_client = chromadb.PersistentClient(path=self.vector_db_dir)
#         self.vector_db = chroma_client.get_or_create_collection(
#             name="experiences", embedding_function=openai_ef
#         )
    
#     def add_experience_trace(self, trace: InteractionTrace):
#         """store the trace, in case we want to use it later on
#         commit the preliminary skills to memory... or just commit them right away?
#         from successful traces?
#         need to keep mapping from skill to successful trace...
#         """

#         if trace.successful_attempt:
#             skills = extract_functions(trace.successful_attempt.code_string)
#             # generate a description for each skill... or just embed them directly... i think embed directly, might get too expensive
#             # we will see once we actually try running the clustering algorithm

#             for (name, skill) in skills:
#                 print(skill)
#                 id = f"{name}-{trace.id}"
#                 self.vector_db.add(
#                     documents=[skill],
#                     ids=[id],
#                     metadatas=[{"success": trace.is_success, "function_name": name, "trace_id": str(trace.id)}],
#                 )

#                 with open(f"{self.skill_dir}/{name}-{str(trace.id)}.py", "w") as file:
#                     file.write(skill)
#                 self.skill_dir
        
#         trace.dump()  # in case we want to reuse later (for example to extract insights, common feedback, ...)
    
#         # should we also store few-shot examples?

