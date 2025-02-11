def place_blocks_in_line(gap: float = 0.005):
    """
    Place all blocks in the environment in a line with a specified gap between them.
    :param gap: The gap to leave between the blocks.
    """
    # Retrieve all blocks in the environment
    blocks = get_objects()
    # Sort blocks by their id to ensure a consistent order
    blocks.sort(key=lambda block: block.id)
    # Start placing blocks in a line
    for i in range(1, len(blocks)):
        base_block = blocks[i - 1]
        adjacent_block = blocks[i]
        # Place the current block next to the previous block
        place_block_next_to_another(base_block, adjacent_block, gap)