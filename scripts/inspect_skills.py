import chromadb
from agents.skill import Skill, SkillManager
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

import mplcursors


skill_manager = SkillManager()
ids, embeddings = skill_manager.get_all_skill_embeddings()

tsne = TSNE(n_components=2, perplexity=2, random_state=42)
tsne_embeddings = tsne.fit_transform(embeddings)

# # Step 3: Plot results
# plt.figure(figsize=(8, 6))
# plt.scatter(embeddings_tsne[:, 0], embeddings_tsne[:, 1], s=5, alpha=0.7)
# plt.title("t-SNE Visualization of Text Embeddings")
# plt.show()

pca = PCA(n_components=5)
pca_embeddings = pca.fit_transform(embeddings)

# -----------------------------------------------
# plot elbow curve
# wcss = []  # Within-cluster sum of squares
# for k in range(1, 20):
#     kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
#     kmeans.fit(pca_embeddings)
#     wcss.append(kmeans.inertia_)

# plt.plot(range(1, 20), wcss, marker="o")
# plt.xlabel("Number of Clusters (k)")
# plt.ylabel("WCSS")
# plt.title("Elbow Method for Optimal k")
# plt.show()
# --------------------------------------------------

kmeans = KMeans(n_clusters=8, random_state=42, n_init=10)
labels = kmeans.fit_predict(pca_embeddings)


sc = plt.scatter(
    tsne_embeddings[:, 0], tsne_embeddings[:, 1], c=labels, cmap="viridis", alpha=0.6
)


cursor = mplcursors.cursor(sc, hover=True)
cursor.connect("add", lambda sel: sel.annotation.set_text(f"{ids[sel.index]}"))

plt.title("K-Means Clustering")
plt.legend()
plt.show()
