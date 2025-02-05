 """
task:
 rotate the gripper in a circle, while maintaining its position 
""" 

 def move_gripper_down_and_rotate_in_four_steps():
    """
    Moves the gripper down further and then rotates the final link of the robotic arm
    in four steps, each representing a quarter circle around the x-axis.
    Returns:
    None
    """
    # Get the current pose of the end effector
    current_pose = get_end_effector_pose()
    # Move the gripper down further
    down_offset = 0.15  # Adjust this value as needed for a more significant downward movement
    new_position = Point3D(current_pose.position.x, current_pose.position.y, current_pose.position.z - down_offset)
    move_end_effector_to(Pose(position=new_position, rotation=current_pose.rotation))
    # Define the number of steps for the full circle
    num_steps = 4  # Four steps for four quarter circles
    # Calculate the angle increment for each quarter circle
    angle_increment = np.pi / 2  # 90 degrees for each quarter circle
    # Iterate over the number of steps to create a full circular rotation
    for i in range(num_steps):
        # Calculate the angle for the current step
        angle = (i + 1) * angle_increment
        # Calculate the new rotation for the gripper
        new_rotation = current_pose.rotation * Rotation.from_euler('x', angle)
        # Create a new pose with the same position and the new rotation
        new_pose = Pose(position=new_position, rotation=new_rotation)
        # Move the end effector to the new pose
        move_end_effector_to(new_pose)
        # Optionally, add a small delay here if needed for smooth motion
# Execute the function to move the gripper down further and rotate it in four steps
move_gripper_down_and_rotate_in_four_steps()