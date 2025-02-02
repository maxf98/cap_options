 """
task:
 put the cyan block on top of the white one 
""" 

 def find_object_by_color(color: str, objects: list[TaskObject]) -> TaskObject:
    """
    Find the first object in the list with the specified color.
    :param color: The color of the object to find.
    :param objects: A list of TaskObject instances.
    :return: The first TaskObject with the specified color.
    """
    for obj in objects:
        if obj.color == color:
            return obj
    return None
def execute_put_cyan_on_white():
    """
    Execute the task of putting the cyan block on top of the white block.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Find the cyan and white blocks
    cyan_block = find_object_by_color('cyan', objects)
    white_block = find_object_by_color('white', objects)
    if not cyan_block or not white_block:
        say("Could not find the required blocks.")
        return
    # Get the poses of the cyan and white blocks
    cyan_pose = get_object_pose(cyan_block)
    white_pose = get_object_pose(white_block)
    # Execute the pick-and-place operation
    put_first_on_second(cyan_pose, white_pose)
    say("Successfully placed the cyan block on top of the white block.")
# Execute the plan
execute_put_cyan_on_white()