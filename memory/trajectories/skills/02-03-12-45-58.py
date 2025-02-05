 """
task:
 place one blue block on each side of the red block, so that the edges align perfectly 
""" 

 def find_blocks_by_color(color: str, objects: list[TaskObject], count: int) -> list[TaskObject]:
    """
    Find a specified number of blocks with the given color in the list of objects.
    :param color: The color of the blocks to find.
    :param objects: The list of TaskObjects to search through.
    :param count: The number of blocks to find.
    :return: A list of TaskObjects with the specified color.
    """
    found_blocks = [obj for obj in objects if obj.color == color]
    return found_blocks[:count]
def calculate_side_poses(center_pose: Pose, block_size: tuple[float, float, float]) -> list[Pose]:
    """
    Calculate the poses for placing blocks on all four sides of a center block.
    :param center_pose: The Pose of the center block.
    :param block_size: The size of the block as a tuple (width, depth, height).
    :return: A list containing the Poses for the four sides.
    """
    width, depth, _ = block_size
    rotation_matrix = center_pose.rotation.as_matrix()
    # Calculate offsets based on the rotation of the center block
    left_offset = rotation_matrix @ np.array([-width, 0, 0])
    right_offset = rotation_matrix @ np.array([width, 0, 0])
    front_offset = rotation_matrix @ np.array([0, depth, 0])
    back_offset = rotation_matrix @ np.array([0, -depth, 0])
    left_pose = Pose(
        position=Point3D.from_xyz(center_pose.position.np_vec + left_offset),
        rotation=center_pose.rotation
    )
    right_pose = Pose(
        position=Point3D.from_xyz(center_pose.position.np_vec + right_offset),
        rotation=center_pose.rotation
    )
    front_pose = Pose(
        position=Point3D.from_xyz(center_pose.position.np_vec + front_offset),
        rotation=center_pose.rotation
    )
    back_pose = Pose(
        position=Point3D.from_xyz(center_pose.position.np_vec + back_offset),
        rotation=center_pose.rotation
    )
    return [left_pose, right_pose, front_pose, back_pose]
def place_blue_blocks_around_red_block():
    """
    Place one blue block on each side of the red block, aligning the edges perfectly.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Find the red block
    red_blocks = find_blocks_by_color('red', objects, 1)
    if not red_blocks:
        say("No red block found in the environment.")
        return
    red_block = red_blocks[0]
    # Find four blue blocks
    blue_blocks = find_blocks_by_color('blue', objects, 4)
    if len(blue_blocks) < 4:
        say("Not enough blue blocks found in the environment.")
        return
    # Get the pose of the red block
    red_block_pose = get_object_pose(red_block)
    # Calculate the side poses for the blue blocks
    side_poses = calculate_side_poses(red_block_pose, red_block.size)
    # Place each blue block on the corresponding side of the red block
    for blue_block, side_pose in zip(blue_blocks, side_poses):
        put_first_on_second(get_object_pose(blue_block), side_pose)
    say("Blue blocks have been placed on each side of the red block.")
# Execute the plan
place_blue_blocks_around_red_block()