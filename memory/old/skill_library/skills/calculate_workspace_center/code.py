def calculate_workspace_center(workspace: Workspace) -> Point3D:
    """Calculate the center position of the workspace.
    :param workspace: The workspace with defined bounds.
    :return: The center position as a Point3D object.
    """
    center_x = (workspace.bounds[0][0] + workspace.bounds[0][1]) / 2
    center_y = (workspace.bounds[1][0] + workspace.bounds[1][1]) / 2
    center_z = (workspace.bounds[2][0] + workspace.bounds[2][1]) / 2
    return Point3D(center_x, center_y, center_z)