# TASK:put one block on top of the other block

blocks_to_stack = get_objects()
blocks_to_stack = [block for block in blocks_to_stack if block.objectType == 'block']
stack_blocks(blocks_to_stack)