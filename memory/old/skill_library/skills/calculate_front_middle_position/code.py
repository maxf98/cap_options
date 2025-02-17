def calculate_front_middle_position(workspace: Workspace) -> Point3D:
    """
    Calculate the position for the middle of the front edge of the workspace.
    The front edge is along the x-max bound for the workspace.
    :param workspace: The workspace with defined bounds.
    :return: The position of the front middle edge as a Point3D object.
    """
    # The front edge, middle is at max of x, middle of y, zero height.
    x_max = workspace.bounds[0, 1]
    y_middle = (workspace.bounds[1, 0] + workspace.bounds[1, 1]) / 2
    z = 0  # Surface level
    return Point3D(x_max, y_middle, z)