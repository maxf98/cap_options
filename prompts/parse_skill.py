from prompts.prompt_utils import get_core_types_text


generate_function_header_system_prompt = f"""
We are working in the context of controlling a robotic arm with python code. 
The user proposes a certain skill they would like the robot to learn.
To enable this, you are supposed to translate this skill into a python function, 
i.e. choose a clear, descriptive name for the function, choose appropriate arguments, and write a clear, descriptive docstring.

For example:
USER: "place one block on top of the other"
RESPONSE:
def place_block_on_other_block(block: TaskObject, otherBlock: TaskObject):
    \"\"\" Places one block on top of the other block  \"\"\"
    pass
    
Do not try to implement the function yet, that happens later.
    
You should adhere to the following types:
{get_core_types_text()}
"""
# Could just try implementing the function body....


def refine_function_header_prompt(function_header, refinement):
    return f"""
    Revise the following python function header according to the user instructions:
    {function_header}
    Refinement prompt:
    {refinement}
    """
