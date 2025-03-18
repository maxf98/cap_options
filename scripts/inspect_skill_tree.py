import networkx as nx
import matplotlib.pyplot as plt

from agents.memory import MemoryManager


memory_manager = MemoryManager()

all_skills = memory_manager.skill_manager.all_skills

for skill in all_skills:
    print(len(memory_manager.skill_task_examples(skill)))


skills_with_deps = {}
for skill in all_skills:
    deps = memory_manager.skill_manager.get_skill_calls(skill.code, func_names=True)
    skills_with_deps[skill.name] = deps

G = nx.DiGraph()
for parent, children in skills_with_deps.items():
    for child in children:
        G.add_edge(parent, child)


core_primitives = [skill.name for skill in all_skills if skill.is_core_primitive]
node_colors = [
    "lightcoral" if node in core_primitives else "grey" for node in G.nodes()
]

plt.figure(figsize=(8, 6))
pos = nx.drawing.nx_agraph.graphviz_layout(G, prog="dot")  # Tree layout
nx.draw(
    G,
    pos,
    with_labels=True,
    arrows=True,
    node_color=node_colors,
    edge_color="gray",
    node_size=2000,
    font_size=10,
)
plt.show()
