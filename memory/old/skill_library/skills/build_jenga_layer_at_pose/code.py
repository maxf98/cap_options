def build_jenga_layer_at_pose(blocks: list[TaskObject], layer_pose: Pose, gap: float = 0.008):
    """
    Constructs a single layer of a Jenga tower centered at a given pose using three blocks.
    :param blocks: List of TaskObjects to use for the layer.
    :param layer_pose: The Pose where the center block of the layer should be positioned.
    :param gap: The gap to maintain between adjacent blocks.
    """
    # Ensure there are enough blocks
    if len(blocks) < 3:
        say("Not enough blocks to build a Jenga layer.")
        return
    # Use the central position and rotation from the layer_pose
    center_position = layer_pose.position
    standard_rotation = layer_pose.rotation
    # Identify the length of a block
    block_length = blocks[0].size[1]
    # Place the central block at the given position
    central_block_pose = Pose(position=center_position, rotation=standard_rotation)
    put_first_on_second(get_object_pose(blocks[0]), central_block_pose)
    # Calculate the position for the block to the left of the central block
    left_block_position = get_point_at_distance_and_rotation_from_point(
        point=center_position,
        rotation=standard_rotation,
        distance=-(block_length + gap),  # Place to the left
        direction=np.array([0, 1, 0])  # Assuming axis is along the y-axis
    )
    left_block_pose = Pose(position=left_block_position, rotation=standard_rotation)
    put_first_on_second(get_object_pose(blocks[1]), left_block_pose)
    # Calculate the position for the block to the right of the central block
    right_block_position = get_point_at_distance_and_rotation_from_point(
        point=center_position,
        rotation=standard_rotation,
        distance=(block_length + gap),  # Place to the right
        direction=np.array([0, 1, 0])  # Assuming axis is along the y-axis
    )
    right_block_pose = Pose(position=right_block_position, rotation=standard_rotation)
    put_first_on_second(get_object_pose(blocks[2]), right_block_pose)
    say("Jenga layer constructed at the specified pose.")