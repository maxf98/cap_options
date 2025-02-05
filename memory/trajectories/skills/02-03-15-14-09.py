 """
task:
 build a 4*4 chessboard from the blocks 
""" 

 def find_blocks_by_color(color: str, objects: list[TaskObject]) -> list[TaskObject]:
    """
    Find all blocks of a specific color from the list of objects.
    :param color: The color of the blocks to find.
    :param objects: The list of TaskObjects in the environment.
    :return: A list of TaskObjects that match the specified color.
    """
    return [obj for obj in objects if obj.color == color and obj.objectType == 'block']
def calculate_chessboard_position(row: int, col: int, block_size: tuple[float, float, float], spacing: float) -> Pose:
    """
    Calculate the position for a block on the chessboard grid with spacing.
    :param row: The row index on the chessboard.
    :param col: The column index on the chessboard.
    :param block_size: The size of the block.
    :param spacing: The space to leave between blocks.
    :return: The Pose for the block on the chessboard.
    """
    x = Workspace.bottom_left.x + col * (block_size[0] + spacing)
    y = Workspace.bottom_left.y + row * (block_size[1] + spacing)
    z = Workspace.bottom_left.z + block_size[2] / 2  # Place block on the surface
    return Pose(Point3D(x, y, z), Rotation.identity())
def build_chessboard_with_spacing(spacing: float = 0.01):
    """
    Build a 4x4 chessboard using blocks in the environment with spacing between blocks.
    :param spacing: The space to leave between blocks.
    """
    objects = get_objects()
    black_blocks = find_blocks_by_color('black', objects)
    white_blocks = find_blocks_by_color('white', objects)
    if len(black_blocks) < 8 or len(white_blocks) < 8:
        say("Not enough blocks to build a 4x4 chessboard.")
        return
    block_size = black_blocks[0].size  # Assuming all blocks are of the same size
    for row in range(4):
        for col in range(4):
            if (row + col) % 2 == 0:
                block = black_blocks.pop()
            else:
                block = white_blocks.pop()
            pick_pose = get_object_pose(block)
            place_pose = calculate_chessboard_position(row, col, block_size, spacing)
            put_first_on_second(pick_pose, place_pose)
    say("4x4 chessboard with spacing has been built.")
# Execute the plan
build_chessboard_with_spacing()