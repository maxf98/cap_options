def calculate_adjacent_position_with_rotation(base_block: TaskObject, adjacent_block_size: tuple[float, float, float], gap: float) -> Point3D:
    """
    Calculate the position for a block to be placed adjacent to another block with a small gap, considering rotation.
    :param base_block: The block next to which the new block will be placed.
    :param adjacent_block_size: The size of the block to be placed.
    :param gap: The gap to leave between the blocks.
    :return: The target position for the adjacent block.
    """
    base_pose = get_object_pose(base_block)
    # Calculate the offset in the x-direction based on the size of the base block
    offset_x = base_block.size[0] / 2 + gap + adjacent_block_size[0] / 2
    offset_vector = np.array([offset_x, 0, 0])
    # Apply the rotation of the base block to the offset vector
    rotated_offset = base_pose.rotation.apply(offset_vector)
    # Calculate the new position by adding the rotated offset to the base position
    new_position = base_pose.position.np_vec + rotated_offset
    return Point3D.from_xyz(new_position)