# TASK:stack all the red blocks in the environment

red_blocks = retrieve_blocks(color='red')
if red_blocks:
    say(f'Found {len(red_blocks)} red blocks to stack.')
    base_block = red_blocks[0]
    other_blocks = red_blocks[1:]
    stack_blocks(base_block, other_blocks)
else:
    say('No red blocks found to stack.')