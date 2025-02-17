def place_block_next_to(block_1: TaskObject, block_2: TaskObject, side_vector: np.array = np.array([1, 0, 0]), gap: float = 0.008):
    """
    Places one block next to another block on a specified side, leaving a given gap between them.
    :param block_1: The first block (TaskObject).
    :param block_2: The second block (TaskObject) to be placed next to the first.
    :param side_vector: A numpy array representing the direction (side) in which to place the second block. Default is the positive x-direction.
    :param gap: The gap to leave between the blocks. Default is 0.008.
    """
    # Retrieve the poses for both blocks
    pose_1 = get_object_pose(block_1)
    pose_2 = get_object_pose(block_2)
    # Calculate the total required distance, including gap
    block_size = block_1.size[0]  # Assuming the blocks are cubic and we use the x-size
    distance = block_size + gap
    # Calculate the target position using the utility function
    target_position = get_point_at_distance_and_rotation_from_point(
        pose_1.position, pose_1.rotation, distance, side_vector
    )
    # Create the target pose for placement
    target_pose = Pose(position=target_position, rotation=pose_1.rotation)
    # Move block 2 next to block 1
    put_first_on_second(pose_2, target_pose)
    say(f"Placed block {block_2.description} next to block {block_1.description} on the specified side.")