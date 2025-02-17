from agents.skill import Skill, SkillManager
from agents.experience import InteractionTrace

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

from utils.llm_utils import query_llm, extract_code

import mplcursors
from collections import defaultdict

from prompts.distillation import distill_prompt, distill_system_prompt


class RevisionAgent:
    """performs clustering of skills, then rewriting and testing on user-validated interaction sequences"""

    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager

    def visualise_skill_space_tsne(self):
        """present lower-dimensional representation of skill space"""
        ids, embeddings = self.skill_manager.get_all_skill_embeddings()
        tsne = TSNE(n_components=2, perplexity=2, random_state=42)
        tsne_embeddings = tsne.fit_transform(embeddings)
        sc = plt.scatter(
            tsne_embeddings[:, 0],
            tsne_embeddings[:, 1],
            alpha=0.6,
        )

        cursor = mplcursors.cursor(sc, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(f"{ids[sel.index]}"))

        plt.show()

    def cluster_embeddings(self, num_clusters, visualise=True):
        ids, embeddings = self.skill_manager.get_all_skill_embeddings()

        # use TSNE for low-dimensional visualisation
        tsne = TSNE(n_components=2, perplexity=2, random_state=42)
        tsne_embeddings = tsne.fit_transform(embeddings)

        # use PCA to simplify the actual clustering process
        # TODO: check these parameters...
        pca = PCA(n_components=5)
        pca_embeddings = pca.fit_transform(embeddings)

        # perform clustering
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pca_embeddings)

        if visualise:
            sc = plt.scatter(
                tsne_embeddings[:, 0],
                tsne_embeddings[:, 1],
                c=labels,
                cmap="viridis",
                alpha=0.6,
            )

            cursor = mplcursors.cursor(sc, hover=True)
            cursor.connect(
                "add", lambda sel: sel.annotation.set_text(f"{ids[sel.index]}")
            )

            plt.title("K-Means Clustering")
            plt.legend()
            plt.show()

        labelled_ids = list(zip(ids, labels))

        def bucketify_by_category(pairs):
            buckets = defaultdict(list)
            for key, category in pairs:
                buckets[category].append(key)  # Group by second value
            return dict(buckets)  # Convert back to a normal dict if needed

        bucketed_ids = list(bucketify_by_category(labelled_ids).values())

        print(bucketed_ids)
        return bucketed_ids

    def distill(self):
        """clusters the skills, tries to rewrite and condense them, then tests them
        should also retrieve knowledge from user feedbacks... but we'll get to that
        """
        clustered_skill_ids = self.cluster_embeddings(10, visualise=False)
        for skill_cluster in clustered_skill_ids:
            skills = [
                Skill.retrieve_skill_with_name(skill_name)
                for skill_name in skill_cluster
            ]
            self.process_cluster(skills)

    def distill_user_corrections(self):
        traces = InteractionTrace.get_all_traces()
        feedbacks = [
            attempt.feedback
            for trace in traces
            for attempt in trace.attempts
            if attempt.gave_feedback
        ]
        print(feedbacks)

    def process_cluster(self, skills: list[Skill]):
        """a cluster is a list of similar skills
        these will contain some redundancy, some over-specificity, and can likely be cleaned up a little bit
        by considering them together, we should be able to extract some generalisable knowledge
        we should also be able to generate some new skills
        1) pass the skill cluster - get proposition of function rewrite
        2) for each instance of this function being used, replace the calls with the rewritten function
        3) test the rewritten functions on the existing traces... in order to pass, must produce EXACTLY THE SAME environment config
        4) propagate changes to all calls
        """
        messages = [{"role": "system", "content": distill_system_prompt}]
        messages.append({"role": "user", "content": distill_prompt(skills)})
        response = query_llm(messages)
        print(response)

    def extract_insights_from_traces(self):
        """we should also be able to extract insights from user correction rounds
        these should again be stored as functions, and fed into the API
        e.g. common mistake: object.position - object has no attribute position"""


if __name__ == "__main__":
    skill_manager = SkillManager()
    distill_agent = RevisionAgent(skill_manager)
    # distil_agent.visualise_skill_space_tsne()
    # distil_agent.cluster_embeddings(num_clusters=10)
    distill_agent.distill()
