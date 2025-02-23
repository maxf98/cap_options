# TASK:put the red block on the left side of the green block

red_block = retrieve_blocks(color='red')[0]
green_block = retrieve_blocks(color='green')[0]
place_block_next_to_another(red_block, green_block, 'left')