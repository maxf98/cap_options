def get_back_right_corner_position(workspace: Workspace) -> Point3D:
    """
    Calculate the position for the back right corner of the workspace from the robot's perspective.
    The corner is on the x-min and y-max bounds.
    :param workspace: The workspace with defined bounds.
    :return: The position of the back right corner as a Point3D object.
    """
    x_min = workspace.bounds[0, 0]
    y_max = workspace.bounds[1, 1]
    z_min = workspace.bounds[2, 0]
    return Point3D(x_min, y_max, z_min)