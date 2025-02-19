import os


# MEMORY

MEMORY_DIR = "/Users/maxfest/vscode/thesis/thesis/memory/"
SKILL_LIBRARY_DIR = "/Users/maxfest/vscode/thesis/thesis/memory/skill_library/"
SKILL_DIR = f"{SKILL_LIBRARY_DIR}/skills"
EXAMPLE_LIBRARY_DIR = f"{MEMORY_DIR}/example_library"
EXAMPLE_DIR = f"{EXAMPLE_LIBRARY_DIR}/examples"
os.makedirs(SKILL_LIBRARY_DIR, exist_ok=True)
os.makedirs(SKILL_DIR, exist_ok=True)
os.makedirs(EXAMPLE_LIBRARY_DIR, exist_ok=True)
os.makedirs(EXAMPLE_DIR, exist_ok=True)
