def clear_area_for_cube(cube_pose: Pose, cube_size: float, gap: float):
    """Clears the area where the cube will be built."""
    # Retrieve all objects in the workspace
    objects = get_objects()
    # Calculate a bounding area for the cube
    half_size = (cube_size + gap) * 1.5  # 1.5 times the half diagonal (safety margin)
    cube_center = cube_pose.position
    min_bound = Point3D(cube_center.x - half_size, cube_center.y - half_size, cube_center.z)
    max_bound = Point3D(cube_center.x + half_size, cube_center.y + half_size, cube_center.z + cube_size + gap)
    # Move objects out of this area
    for obj in objects:
        obj_pose = get_object_pose(obj)
        if (min_bound.x <= obj_pose.position.x <= max_bound.x and
            min_bound.y <= obj_pose.position.y <= max_bound.y):
            # Move block to a safe place, assume workspace space bound on x is safe
            safe_position = Point3D(0.2, obj_pose.position.y, obj_pose.position.z)
            safe_pose = Pose(position=safe_position, rotation=obj_pose.rotation)
            put_first_on_second(obj_pose, safe_pose)
            say(f"Moved {obj.description} to clear build area.")