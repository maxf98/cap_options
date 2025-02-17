def get_front_left_corner_position(workspace: Workspace) -> Point3D:
    """
    Calculate the position for the front left corner of the workspace from the robot's perspective.
    This corner is on the x-max and y-min bounds.
    :param workspace: The workspace with defined bounds.
    :return: The position of the front left corner as a Point3D object.
    """
    x = workspace.bounds[0][1]  # x-max
    y = workspace.bounds[1][0]  # y-min
    z = workspace.bounds[2][0]  # typically start at the lowest z
    return Point3D(x, y, z)