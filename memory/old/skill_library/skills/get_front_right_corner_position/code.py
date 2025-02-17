def get_front_right_corner_position(workspace: Workspace) -> Point3D:
    """
    Calculate the position for the front right corner of the workspace from the robot's perspective.
    This corner is on the x-max and y-max bounds.
    :param workspace: The workspace with defined bounds.
    :return: The position of the front right corner as a Point3D object.
    """
    x_max = workspace.bounds[0][1]
    y_max = workspace.bounds[1][1]
    z_min = workspace.bounds[2][0]  # Assume blocks are placed on the surface
    return Point3D(x_max, y_max, z_min)