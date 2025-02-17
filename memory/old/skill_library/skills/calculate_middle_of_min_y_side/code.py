def calculate_middle_of_min_y_side(workspace: Workspace) -> Point3D:
    """
    Calculate the middle position along the side with the smallest y-coordinate (i.e., the left side).
    :param workspace: The workspace with defined bounds.
    :return: The position in the middle of the minimal y-coordinate side as a Point3D object.
    """
    y_min = workspace.bounds[1][0]  # y-min for the left side
    x_middle = (workspace.bounds[0][0] + workspace.bounds[0][1]) / 2  # Middle of the x-axis
    z = workspace.bounds[2][0]  # Surface level
    return Point3D(x_middle, y_min, z)