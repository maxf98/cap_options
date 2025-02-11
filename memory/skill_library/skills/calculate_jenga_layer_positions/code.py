def calculate_jenga_layer_positions(start_position: Point3D, block_size: tuple[float, float, float], gap: float) -> list[Point3D]:
    """
    Calculate the target positions for the 3 blocks to form a single Jenga layer.
    :param start_position: The starting position for the first block in the layer.
    :param block_size: The size of each block.
    :param gap: The gap to leave between blocks.
    :return: A list of target positions for the blocks.
    """
    positions = []
    shortest_side = min(block_size)  # Use the shortest side for spacing
    for i in range(3):
        x_offset = i * (shortest_side + gap)
        position = Point3D(start_position.x + x_offset, start_position.y, start_position.z)
        positions.append(position)
    return positions