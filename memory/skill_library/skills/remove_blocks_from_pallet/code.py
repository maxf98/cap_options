def remove_blocks_from_pallet():
    """
    Main function to remove blocks that are on top of the pallet and place them in the back-left corner of the workspace.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Identify the pallet
    pallet = next((obj for obj in objects if obj.objectType == 'pallet'), None)
    if not pallet:
        say("No pallet found in the environment.")
        return
    # Get the bounding box of the pallet
    pallet_bbox = get_bbox(pallet)
    # Filter out the blocks that are on top of the pallet
    blocks_on_pallet = [block for block in objects if block.objectType == 'block' and is_block_on_pallet(block, pallet_bbox)]
    # Calculate the back-left corner position of the workspace
    workspace = Workspace()
    back_left_corner = calculate_back_left_corner(workspace.bounds)
    # Move each block on the pallet to the back-left corner
    for block in blocks_on_pallet:
        move_block_to_position(block, back_left_corner)