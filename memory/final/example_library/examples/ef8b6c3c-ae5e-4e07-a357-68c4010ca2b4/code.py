# TASK: stack all the blocks

blocks = get_objects()
stacking_position = get_object_pose(blocks[0]).position
blocks.sort(key=lambda block: get_object_pose(block).position.z)
current_base_pose = get_object_pose(blocks[0])
for block in blocks:
    block_pose = get_object_pose(block)
    put_first_on_second(block_pose, current_base_pose)
    current_base_pose = get_object_pose(block)