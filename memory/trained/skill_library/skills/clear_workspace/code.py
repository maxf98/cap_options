def clear_workspace(objects: list[TaskObject]):
    """Clears objects from the workspace by lining them up neatly along the left edge, just outside of the workspace.
    If there are too many objects to fit in a single line, it will start stacking them.
    """
    if len(objects) == 0:
        return
    workspace = Workspace()
    spacing_between_objects = 0.005

    block_size = get_object_size(objects[0])[
        0
    ]  # Assuming all objects have the same width
    left_side_start = Point3D(
        workspace.bounds[0, 0] + block_size,
        workspace.bounds[1, 0] - block_size,
        block_size / 2,
    )  # Correct the shift to directly left, just outside

    max_objects_per_line = int(0.45 // (block_size + spacing_between_objects))
    # Adjust the spacing between blocks to make it smaller
    num_lines = (len(objects) // max_objects_per_line) + (
        1 if len(objects) % max_objects_per_line != 0 else 0
    )
    dimensions = (max_objects_per_line, 1, num_lines)
    build_structure_from_blocks(
        objects,
        dimensions,
        Pose(left_side_start, Rotation.identity()),
        spacing_between_objects,
    )
