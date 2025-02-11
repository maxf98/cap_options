from agents.skill import Skill, SkillManager
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from utils.llm_utils import query_llm

import mplcursors


class DistillAgent:
    """performs clustering of skills, then rewriting and testing on user-validated interaction sequences"""

    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager

    def perform_clustering(self):
        """performs clustering of skills"""
        all_embeddings = self.skill_manager.get_all_skill_embeddings()

    def process_cluster(self, skills: list[Skill]):
        """a cluster"""
        pass

    def replace_trace