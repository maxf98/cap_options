def place_block_next_to_another(block: TaskObject, referenceBlock: TaskObject, direction: str):
    """
    Places the specified block right next to another block in the chosen direction.
    Args:
    - block (TaskObject): The block to be placed.
    - referenceBlock (TaskObject): The block next to which the block will be placed.
    - direction (str): The direction in which to place the block relative to the reference block. 
      Valid options are 'front', 'back', 'left', or 'right'.
    """
    ref_bbox = get_bbox(referenceBlock)
    ref_pose = get_object_pose(referenceBlock)
    # Determine placement vector based on the direction
    if direction == 'left':
        offset_vec = np.array([0, -1, 0])  # Negative y-direction
    elif direction == 'right':
        offset_vec = np.array([0, 1, 0])  # Positive y-direction
    elif direction == 'front':
        offset_vec = np.array([1, 0, 0])  # Positive x-direction
    elif direction == 'back':
        offset_vec = np.array([-1, 0, 0])  # Negative x-direction
    else:
        raise ValueError(f"Invalid direction: {direction}. Valid options are 'front', 'back', 'left', 'right'.")
    # Calculate the place position
    distance_to_move = ref_bbox.size[1] / 2 + block.size[1] / 2
    place_point = get_point_at_distance_and_rotation_from_point(
        ref_pose.position, ref_pose.rotation, distance_to_move, offset_vec
    )
    place_pose = Pose(position=place_point, rotation=ref_pose.rotation)
    pick_pose = get_object_pose(block)
    # Use the robotic arm to pick and then place the block
    put_first_on_second(pick_pose, place_pose)