def place_blue_blocks_around_red_block():
    """
    Place blue blocks on each side of the red block, ensuring edges align with a tiny gap between them.
    """
    # Retrieve all objects in the workspace
    objects = get_objects()
    # Locate the red block and all blue blocks
    red_block = None
    blue_blocks = []
    for obj in objects:
        if obj.objectType == 'block' and obj.color == 'red':
            red_block = obj
        elif obj.objectType == 'block' and obj.color == 'blue':
            blue_blocks.append(obj)
    if not red_block:
        say("No red block found in the workspace.")
        return
    if len(blue_blocks) < 4:
        say("Not enough blue blocks available.")
        return
    # Make sure the red block is in place
    place_red_block_in_center()
    # Define directions for the sides (x, -x, y, -y)
    directions = [np.array([1, 0, 0]), np.array([-1, 0, 0]), np.array([0, 1, 0]), np.array([0, -1, 0])]
    # Place blue blocks around the red block with a tiny gap
    for blue_block, direction in zip(blue_blocks, directions):
        place_block_next_to(red_block, blue_block, side_vector=direction, gap=0.005)
    say("Placed blue blocks on each side of the red block, aligning the edges with a tiny gap.")