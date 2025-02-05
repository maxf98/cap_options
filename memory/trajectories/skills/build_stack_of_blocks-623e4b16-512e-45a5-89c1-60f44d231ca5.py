def build_stack_of_blocks():
    """
    Build a stack of 5 blocks using the available blocks in the environment.
    """
    blocks = get_objects()
    num_blocks = len(blocks)
    if num_blocks < 5:
        say("Not enough blocks to complete the task.")
        return
    # Assume the first block is the base of the stack
    base_block = blocks[0]
    base_pose = get_object_pose(base_block)
    block_size = base_block.size
    for i in range(1, 5):
        current_block = blocks[i]
        pick_pose = get_object_pose(current_block)
        place_pose = get_highest_point_on_stack(base_pose, i, block_size)
        put_first_on_second(pick_pose, place_pose)
        say(f"Placed block {current_block.id} on the stack.")