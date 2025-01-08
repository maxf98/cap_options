import os
import re

ROOT_DIR = "/Users/maxfest/vscode/thesis/thesis/skill_library/"
SKILL_ROOT_DIR = os.path.join(ROOT_DIR, "skills")
CORE_PRIMITIVE_ROOT_DIR = os.path.join(ROOT_DIR, "primitives")


def add_new_skill(name, code, description, is_primitive=False):
    # Determine the full path for the skill directory
    ROOT_DIR = CORE_PRIMITIVE_ROOT_DIR if is_primitive else SKILL_ROOT_DIR
    skill_dir = os.path.join(ROOT_DIR, name)

    # Create the directory
    os.makedirs(skill_dir)

    # Create and write to {name}.py
    with open(os.path.join(skill_dir, f"{name}.py"), "w") as file:
        file.write(code)

    # Create and write to description.py
    with open(os.path.join(skill_dir, "description.py"), "w") as file:
        file.write(f"\"\"\"{description}\"\"\"")

    # Create and write to usage_examples.py
    usage_examples_dir = os.path.join(skill_dir, "usage_examples")
    os.makedirs(usage_examples_dir, exist_ok=True)

    # Create and write to insights.py
    with open(os.path.join(skill_dir, "insights.py"), "w") as file:
        file.write(f"insights = []")

    print(f"Skill '{name}' has been added under '{skill_dir}' with all necessary files.")


def count_files(directory):
    return len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])


def add_code_to_usage_examples(code_block):
    """
    extracts function calls from a code_block, then finds corresponding functions in the skill library and adds them to usage_examples
    for later use as few-shot examples -> function should only be called for successful examples
    """
    # Step 1: Extract all function names from the code block
    keywords = {'if', 'while', 'for', 'def', 'class', 'with', 'print', 'len', 'int', 'str', 'float', 'list', 'dict', 'set'}
    all_calls = re.findall(r'(?<!def\s)(?<!if\s)(?<!while\s)(?<!for\s)([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code_block)
    function_names = [call for call in all_calls if call not in keywords]
    
    if not function_names:
        raise ValueError("No function names found in the provided code block.")

    # Step 2: Search for directories matching function names
    matching_directories = []
    for function_name in function_names:
        for root_dir in [SKILL_ROOT_DIR, CORE_PRIMITIVE_ROOT_DIR]:
            for root, dirs, _ in os.walk(root_dir):
                if function_name in dirs:
                    matching_directories.append(os.path.join(root, function_name))

    if not matching_directories:
        # handle this otherwise somehow...
        raise FileNotFoundError("No matching directories found for the extracted function names.")

    # Step 3: Create usage_examples.py in each matching directory
    for directory in matching_directories:
        usage_examples_dir = os.path.join(directory, "usage_examples")
        
        # Ensure the usage_examples directory exists
        os.makedirs(usage_examples_dir, exist_ok=True)

        # Create a Python file for the code block
        num_existing_examples = count_files(os.path.join(directory, "usage_examples"))
        file_name = f"example_{num_existing_examples}.txt"  # Use the first function name for file naming
        file_path = os.path.join(usage_examples_dir, file_name)

        # Write the code block into the file
        with open(file_path, "w") as file:
            file.write(code_block)

        print(f"Code block added to '{file_path}'")


def add_insight(name, insight, root_dir="."):
    # Determine the skill directory
    skill_dir = os.path.join(root_dir, name)
    
    # Check if the skill directory exists
    if not os.path.exists(skill_dir):
        raise FileNotFoundError(f"Skill directory '{skill_dir}' not found.")
    
    # Path to the insights.py file
    insights_file = os.path.join(skill_dir, "insights.py")
    
    # Check if the insights.py file exists
    if not os.path.exists(insights_file):
        raise FileNotFoundError(f"Insights file '{insights_file}' not found in '{skill_dir}'.")
    
    # Read the current insights from the file
    try:
        with open(insights_file, "r") as file:
            content = file.read()
            # Extract current insights if they exist
            if "insights = " in content:
                exec(content, globals())
                current_insights = globals().get("insights", [])
            else:
                current_insights = []
    except Exception as e:
        raise ValueError(f"Failed to read from '{insights_file}': {e}")
    
    # Add the new insight if it's not already present
    if insight not in current_insights:
        current_insights.append(insight)
        # Write updated insights back to the file
        with open(insights_file, "w") as file:
            file.write(f"insights = {current_insights}")
        print(f"Insight added: {insight}")
    else:
        print(f"Insight already exists: {insight}")


if __name__ == "__main__":
    add_new_skill(
        name="hello",
        code="def hello():\n    print('This is hello function.')",
        description="This is an example skill for demonstration purposes.",
        is_primitive=False
    )


    add_code_to_usage_examples("example_skill()\nhello()")