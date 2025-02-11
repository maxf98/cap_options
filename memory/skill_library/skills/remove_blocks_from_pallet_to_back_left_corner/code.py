def remove_blocks_from_pallet_to_back_left_corner():
    """
    Main function to remove all blocks from the pallet and place them in the back-left corner of the workspace.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Assume the pallet is a specific object, e.g., with a known id or type
    pallet = next((obj for obj in objects if obj.objectType == 'pallet'), None)
    if not pallet:
        print("No pallet found in the environment.")
        return
    # Get the bounding box of the pallet
    pallet_bbox = get_bbox(pallet)
    # Iterate over all objects to find blocks on the pallet
    for block in objects:
        if block.objectType == 'block' and is_block_on_pallet(block, pallet_bbox):
            # Place the block in the back-left corner
            place_block_in_back_left_corner(block)