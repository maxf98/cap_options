 """
task:
 build a single layer of a jenga tower with 3 blocks 
""" 

 def find_blocks(objects: list[TaskObject]) -> list[TaskObject]:
    """
    Find all blocks in the environment.
    :param objects: A list of TaskObjects to search through.
    :return: A list of TaskObjects that are blocks.
    """
    return [obj for obj in objects if obj.objectType == 'block']
def get_block_pose(block: TaskObject) -> Pose:
    """
    Get the pose of a given block.
    :param block: The TaskObject representing the block.
    :return: The Pose of the block.
    """
    return get_object_pose(block)
def calculate_jenga_layer_position(index: int, base_position: Point3D, block_size: tuple[float, float, float]) -> Pose:
    """
    Calculate the position for a block in the jenga layer.
    :param index: The index of the block in the layer (0, 1, or 2).
    :param base_position: The base position for the jenga layer.
    :param block_size: The size of the block.
    :return: The Pose for the block in the jenga layer.
    """
    y_offset = index * (block_size[1] + 0.005)  # Add a small gap between blocks
    position = Point3D(base_position.x, base_position.y + y_offset, base_position.z)
    rotation = Rotation.identity()  # Assuming no rotation for simplicity
    return Pose(position, rotation)
def build_jenga_layer():
    """
    Build a single layer of a jenga tower with 3 blocks.
    """
    # Get all objects in the environment
    objects = get_objects()
    # Find all blocks in the environment
    blocks = find_blocks(objects)
    # Check if there are at least 3 blocks available
    if len(blocks) < 3:
        say("Not enough blocks to build a jenga layer.")
        return
    # Define the base position for the jenga layer
    base_position = Point3D(0.5, 0, 0.02)  # Slightly above the ground
    # Query the block size from the first block
    block_size = blocks[0].size
    # Build the jenga layer
    for index, block in enumerate(blocks[:3]):  # Use the first three blocks
        pick_pose = get_block_pose(block)
        place_pose = calculate_jenga_layer_position(index, base_position, block_size)
        put_first_on_second(pick_pose, place_pose)
        say(f"Placed block with ID {block.id} at position {index} in the jenga layer.")
# Execute the plan
build_jenga_layer()