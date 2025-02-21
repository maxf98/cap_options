def stack_blocks(blocks: list[TaskObject]):
    """
    Stacks multiple blocks on top of each other. The order of stacking is as provided in the list,
    with the first block in the list being placed at the bottom and each subsequent block stacked above the previous one.
    Args:
        blocks (list[TaskObject]): A list of TaskObject instances representing the blocks to be stacked.
    """
    say("Starting to stack blocks.")
    # Ensure there are at least two blocks to stack
    if len(blocks) < 2:
        say("Error: Need at least two blocks to perform stacking.")
        return
    # Iterate over the list of blocks and stack each on top of the previous
    for i in range(1, len(blocks)):
        bottom_block = blocks[i - 1]
        top_block = blocks[i]
        # Get the pose of the bottom block
        bottom_pose = get_object_pose(bottom_block)
        # Calculate the placement pose for the top block
        # We need to account for the height of the bottom block to position the top block correctly
        bottom_bbox = get_bbox(bottom_block)
        bottom_height = bottom_bbox.size[2]
        # Create the new pose for the top block, right above the bottom block
        top_placement_pose = Pose(
            position=Point3D(
                x=bottom_pose.position.x,
                y=bottom_pose.position.y,
                z=bottom_pose.position.z + bottom_height
            ),
            rotation=bottom_pose.rotation
        )
        # Use the pick-and-place primitive to put the top block on the bottom block
        put_first_on_second(get_object_pose(top_block), top_placement_pose)
        say(f"{top_block.description} has been stacked on {bottom_block.description}.")
    say("Finished stacking all blocks.")