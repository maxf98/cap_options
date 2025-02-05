def find_top_left_corner(workspace: Workspace) -> Point3D:
    """
    Calculate the top left corner position of the workspace in the x-y plane.
    Parameters:
    - workspace: The workspace object containing the bounds of the workspace.
    Returns:
    - Point3D: The top left corner position in the workspace.
    """
    x_min = workspace.bounds[0][0]
    y_min = workspace.bounds[1][0]
    z_min = workspace.bounds[2][0]
    return Point3D(x_min, y_min, z_min)