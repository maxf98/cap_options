from utils.core_types import *

def place_block_next_to_other_block(block: TaskObject, otherBlock: TaskObject, side: str = 'right'):
    """ 
    Places one block next to another block. The side parameter determines on which side of the other block 
    the block is placed (options: 'right', 'left', 'front', or 'back'). 
    """
    otherBlockPose = get_object_pose(otherBlock)
    otherBlockSize = get_object_size(otherBlock)
    # Determine the target position based on the specified side
    if side == 'right':
        target_position = Point3D(otherBlockPose.position.x, 
                                  otherBlockPose.position.y + (otherBlockSize[1] + block.size[1]) / 2, 
                                  otherBlockPose.position.z)
    elif side == 'left':
        target_position = Point3D(otherBlockPose.position.x, 
                                  otherBlockPose.position.y - (otherBlockSize[1] + block.size[1]) / 2, 
                                  otherBlockPose.position.z)
    elif side == 'front':
        target_position = Point3D(otherBlockPose.position.x + (otherBlockSize[0] + block.size[0]) / 2, 
                                  otherBlockPose.position.y, 
                                  otherBlockPose.position.z)
    elif side == 'back':
        target_position = Point3D(otherBlockPose.position.x - (otherBlockSize[0] + block.size[0]) / 2, 
                                  otherBlockPose.position.y, 
                                  otherBlockPose.position.z)
    else:
        raise ValueError("Invalid side. Choose from 'right', 'left', 'front', 'back'.")
    # Create the target pose for the block
    target_pose = Pose(target_position, otherBlockPose.rotation)
    # Get current pose of the block that needs to be moved
    blockPose = get_object_pose(block)
    # Use the primitive to place the block at the target position
    put_first_on_second(blockPose, target_pose)

