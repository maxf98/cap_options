def calculate_target_positions_with_gaps(start_position: Point3D, block_size: tuple[float, float, float], gap: float) -> list[Point3D]:
    """
    Calculate the target positions for the 8 blocks to form a 2x2x2 cube with gaps.
    :param start_position: The starting position for the cube.
    :param block_size: The size of each block.
    :param gap: The gap to leave between blocks.
    :return: A list of target positions for the blocks.
    """
    positions = []
    for x in range(2):
        for y in range(2):
            for z in range(2):
                position = Point3D(
                    start_position.x + x * (block_size[0] + gap),
                    start_position.y + y * (block_size[1] + gap),
                    start_position.z + z * (block_size[2] + gap)
                )
                positions.append(position)
    return positions