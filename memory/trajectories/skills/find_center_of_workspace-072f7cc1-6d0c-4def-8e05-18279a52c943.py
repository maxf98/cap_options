def find_center_of_workspace() -> Point3D:
    """
    Calculate the center point of the workspace.
    Returns:
        Point3D: The center point of the workspace.
    """
    center_x = (Workspace.bottom_left.x + Workspace.top_right.x) / 2
    center_y = (Workspace.bottom_left.y + Workspace.top_right.y) / 2
    center_z = (Workspace.bottom_left.z + Workspace.top_right.z) / 2
    return Point3D(center_x, center_y, center_z)