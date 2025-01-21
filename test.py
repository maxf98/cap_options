import chromadb


# client = chromadb.PersistentClient(path=".")
# collection = client.get_or_create_collection(name="test")
# collection.add(
#     documents=[
#         "This is a document about pineapple",
#         "This is a document about oranges",
#     ],
#     ids=["id1", "id2"],
# )

# results = collection.query(
#     query_texts=[
#         "This is a query document about hawaii"
#     ],  # Chroma will embed this for you
#     n_results=5,  # how many results to return
# )
# print(results)


from agents.skill import SkillManager
import inspect


def hello():
    print("whatsup")


skill_manager = SkillManager(ckpt_dir=".")

skill_manager.add_skill_to_library("hello", inspect.getsource(hello), "say hello")

print(skill_manager.all_skills)
