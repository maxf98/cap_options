# TASK:put the red block on top of the green block

red_block = TaskObject(objectType='block', color='red', id=1)
green_block = TaskObject(objectType='block', color='green', id=2)
stack_blocks(green_block, [red_block])