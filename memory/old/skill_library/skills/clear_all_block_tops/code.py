def clear_all_block_tops():
    """Ensure no blocks have other blocks on top of them."""
    blocks = get_all_blocks()
    for block in blocks:
        clear_block_top(block)