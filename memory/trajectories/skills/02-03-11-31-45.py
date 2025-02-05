 """
task:
 stack the red block on top of the blue block 
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
def stack_red_on_blue():
    """
    Stack the red block on top of the blue block in the workspace.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Find the red and blue blocks
    red_block = find_object_by_color('red', objects)
    blue_block = find_object_by_color('blue', objects)
    if not red_block or not blue_block:
        say("Could not find both red and blue blocks.")
        return
    # Get the poses of the red and blue blocks
    red_pose = get_object_pose(red_block)
    blue_pose = get_object_pose(blue_block)
    # Execute the pick-and-place operation
    put_first_on_second(red_pose, blue_pose)
    say("Stacked the red block on top of the blue block.")
# Execute the plan
stack_red_on_blue()