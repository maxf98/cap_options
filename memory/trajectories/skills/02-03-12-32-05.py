 """
task:
 place the blue block next to the red block, so that the edges align perfectly 
""" 

 def find_object_by_color(color: str, objects: list[TaskObject]) -> TaskObject:
    """
    Find the first object in the list with the specified color.
    :param color: The color of the object to find.
    :param objects: A list of TaskObject instances.
    :return: The TaskObject with the specified color.
    """
    for obj in objects:
        if obj.color == color:
            return obj
    return None
def calculate_adjacent_pose(reference_pose: Pose, reference_size: tuple[float, float, float], target_size: tuple[float, float, float]) -> Pose:
    """
    Calculate the pose for placing an object adjacent to another object, aligning their edges.
    :param reference_pose: The pose of the reference object.
    :param reference_size: The size of the reference object (width, depth, height).
    :param target_size: The size of the target object (width, depth, height).
    :return: The calculated Pose for the target object.
    """
    # Calculate the offset based on the rotation of the reference object
    offset_x = (reference_size[0] + target_size[0]) / 2
    offset_y = 0
    # Rotate the offset according to the reference object's rotation
    rotation_matrix = reference_pose.rotation.as_matrix()
    offset_vector = np.array([offset_x, offset_y, 0])
    rotated_offset = rotation_matrix @ offset_vector
    # Calculate the new position for the target object
    new_position = Point3D(
        reference_pose.position.x + rotated_offset[0],
        reference_pose.position.y + rotated_offset[1],
        reference_pose.position.z
    )
    return Pose(new_position, reference_pose.rotation)
def place_blue_block_next_to_red_block():
    """
    Place the blue block next to the red block, aligning their edges perfectly.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Find the blue and red blocks
    blue_block = find_object_by_color('blue', objects)
    red_block = find_object_by_color('red', objects)
    if not blue_block or not red_block:
        say("Could not find both blue and red blocks.")
        return
    # Get the poses and sizes of the blocks
    blue_pose = get_object_pose(blue_block)
    red_pose = get_object_pose(red_block)
    blue_size = blue_block.size
    red_size = red_block.size
    # Calculate the new pose for the blue block
    new_blue_pose = calculate_adjacent_pose(red_pose, red_size, blue_size)
    # Move the blue block next to the red block
    put_first_on_second(blue_pose, new_blue_pose)
    say("Placed the blue block next to the red block, aligning their edges.")
# Execute the plan
place_blue_block_next_to_red_block()