# __init__.py

import os
import importlib

# Get the directory containing __init__.py
package_dir = os.path.dirname(__file__)
imported_functions = {} 

for root_dir in [os.path.join(package_dir, "skills"), os.path.join(package_dir, "primitives")]:
    print(root_dir)
    for skill in os.listdir(root_dir):
        skill_path = os.path.join(root_dir, skill)
        print(skill_path)
        if os.path.isdir(skill_path) and os.path.exists(os.path.join(skill_path, f"{skill}.py")):
            print(f"{skill}.py")
            # Import the module and get its function
            module = importlib.import_module(f"primitives.{skill}.{skill}", package=__package__)
            # Get all objects from the module
            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                if callable(obj) and not obj_name.startswith('_'):
                    imported_functions[obj_name] = obj

globals().update(imported_functions)

print("Imported functions:")
for name, obj in imported_functions.items():
    if callable(obj) and not name.startswith('_'):
        print(f"- {name}: {obj}")

globals()["hello"]