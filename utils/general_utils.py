"""Miscellaneous utilities."""

import os
import random
from collections import defaultdict

import numpy as np
import pybullet as p
import yaml
from omegaconf import OmegaConf
from transforms3d import euler


lmp_tabletop_coords = {
    'top_left': (0.25, -0.5),
    'top_side': (0.25, 0),
    'top_right': (0.25, 0.5),
    'left_side': (0.5, -0.5),
    'middle': (0.5, 0),
    'right_side': (0.5, 0.5),
    'bottom_left': (0.75, -0.5),
    'bottom_side': (0.75, 0),
    'bottom_right': (0.75, 0.5),
    'table_z': 0.0,
}

# -----------------------------------------------------------------------------
# HEIGHTMAP UTILS
# -----------------------------------------------------------------------------

def get_heightmap(points, colors, bounds, pixel_size):
    """Get top-down (z-axis) orthographic heightmap image from 3D pointcloud.
  
    Args:
      points: HxWx3 float array of 3D points in world coordinates.
      colors: HxWx3 uint8 array of values in range 0-255 aligned with points.
      bounds: 3x2 float array of values (rows: X,Y,Z; columns: min,max) defining
        region in 3D space to generate heightmap in world coordinates.
      pixel_size: float defining size of each pixel in meters.
  
    Returns:
      heightmap: HxW float array of height (from lower z-bound) in meters.
      colormap: HxWx3 uint8 array of backprojected color aligned with heightmap.
    """
    width = int(np.round((bounds[0, 1] - bounds[0, 0]) / pixel_size))
    height = int(np.round((bounds[1, 1] - bounds[1, 0]) / pixel_size))
    heightmap = np.zeros((height, width), dtype=np.float32)
    colormap = np.zeros((height, width, colors.shape[-1]), dtype=np.uint8)

    # Filter out 3D points that are outside of the predefined bounds.
    ix = (points[Ellipsis, 0] >= bounds[0, 0]) & (points[Ellipsis, 0] < bounds[0, 1])
    iy = (points[Ellipsis, 1] >= bounds[1, 0]) & (points[Ellipsis, 1] < bounds[1, 1])
    iz = (points[Ellipsis, 2] >= bounds[2, 0]) & (points[Ellipsis, 2] < bounds[2, 1])
    valid = ix & iy & iz
    points = points[valid]
    colors = colors[valid]

    # Sort 3D points by z-value, which works with array assignment to simulate
    # z-buffering for rendering the heightmap image.
    iz = np.argsort(points[:, -1])
    points, colors = points[iz], colors[iz]
    px = np.int32(np.floor((points[:, 0] - bounds[0, 0]) / pixel_size))
    py = np.int32(np.floor((points[:, 1] - bounds[1, 0]) / pixel_size))
    px = np.clip(px, 0, width - 1)
    py = np.clip(py, 0, height - 1)
    heightmap[py, px] = points[:, 2] - bounds[2, 0]
    for c in range(colors.shape[-1]):
        colormap[py, px, c] = colors[:, c]
    return heightmap, colormap


def get_pointcloud(depth, intrinsics):
    """Get 3D pointcloud from perspective depth image.
  
    Args:
      depth: HxW float array of perspective depth in meters.
      intrinsics: 3x3 float array of camera intrinsics matrix.
  
    Returns:
      points: HxWx3 float array of 3D points in camera coordinates.
    """
    height, width = depth.shape
    xlin = np.linspace(0, width - 1, width)
    ylin = np.linspace(0, height - 1, height)
    px, py = np.meshgrid(xlin, ylin)
    px = (px - intrinsics[0, 2]) * (depth / intrinsics[0, 0])
    py = (py - intrinsics[1, 2]) * (depth / intrinsics[1, 1])
    points = np.float32([px, py, depth]).transpose(1, 2, 0)
    return points


def transform_pointcloud(points, transform):
    """Apply rigid transformation to 3D pointcloud.
  
    Args:
      points: HxWx3 float array of 3D points in camera coordinates.
      transform: 4x4 float array representing a rigid transformation matrix.
  
    Returns:
      points: HxWx3 float array of transformed 3D points.
    """
    padding = ((0, 0), (0, 0), (0, 1))
    homogen_points = np.pad(points.copy(), padding,
                            'constant', constant_values=1)
    for i in range(3):
        points[Ellipsis, i] = np.sum(transform[i, :] * homogen_points, axis=-1)
    return points


def reconstruct_heightmaps(color, depth, configs, bounds, pixel_size):
    """Reconstruct top-down heightmap views from multiple 3D pointclouds."""
    heightmaps, colormaps = [], []
    for color, depth, config in zip(color, depth, configs):
        intrinsics = np.array(config['intrinsics']).reshape(3, 3)
        xyz = get_pointcloud(depth, intrinsics)
        position = np.array(config['position']).reshape(3, 1)
        rotation = p.getMatrixFromQuaternion(config['rotation'])
        rotation = np.array(rotation).reshape(3, 3)
        transform = np.eye(4)
        transform[:3, :] = np.hstack((rotation, position))
        xyz = transform_pointcloud(xyz, transform)
        heightmap, colormap = get_heightmap(xyz, color, bounds, pixel_size)
        heightmaps.append(heightmap)
        colormaps.append(colormap)
    return heightmaps, colormaps


def pix_to_xyz(pixel, height, bounds, pixel_size, skip_height=False):
    """Convert from pixel location on heightmap to 3D position."""
    u, v = pixel
    x = bounds[0, 0] + v * pixel_size
    y = bounds[1, 0] + u * pixel_size
    if not skip_height:
        z = bounds[2, 0] + height[u, v]
    else:
        z = 0.0
    return (x, y, z)


def xyz_to_pix(position, bounds, pixel_size):
    """Convert from 3D position to pixel location on heightmap."""
    u = int(np.round((position[1] - bounds[1, 0]) / pixel_size))
    v = int(np.round((position[0] - bounds[0, 0]) / pixel_size))
    return (u, v)


def unproject_vectorized(uv_coordinates, depth_values,
                         intrinsic,
                         distortion):
    """Vectorized version of unproject(), for N points.
  
    Args:
      uv_coordinates: pixel coordinates to unproject of shape (n, 2).
      depth_values: depth values corresponding index-wise to the uv_coordinates of
        shape (n).
      intrinsic: array of shape (3, 3). This is typically the return value of
        intrinsics_to_matrix.
      distortion: camera distortion parameters of shape (5,).
  
    Returns:
      xyz coordinates in camera frame of shape (n, 3).
    """
    cam_mtx = intrinsic  # shape [3, 3]
    cam_dist = np.array(distortion)  # shape [5]

    # shape of points_undistorted is [N, 2] after the squeeze().
    points_undistorted = cv2.undistortPoints(
        uv_coordinates.reshape((-1, 1, 2)), cam_mtx, cam_dist).squeeze()

    x = points_undistorted[:, 0] * depth_values
    y = points_undistorted[:, 1] * depth_values

    xyz = np.vstack((x, y, depth_values)).T
    return xyz


def unproject_depth_vectorized(im_depth, depth_dist,
                               camera_mtx,
                               camera_dist):
    """Unproject depth image into 3D point cloud, using calibration.
  
    Args:
      im_depth: raw depth image, pre-calibration of shape (height, width).
      depth_dist: depth distortion parameters of shape (8,)
      camera_mtx: intrinsics matrix of shape (3, 3). This is typically the return
        value of intrinsics_to_matrix.
      camera_dist: camera distortion parameters shape (5,).
  
    Returns:
      numpy array of shape [3, H*W]. each column is xyz coordinates
    """
    h, w = im_depth.shape

    # shape of each u_map, v_map is [H, W].
    u_map, v_map = np.meshgrid(np.linspace(
        0, w - 1, w), np.linspace(0, h - 1, h))

    adjusted_depth = depth_dist[0] + im_depth * depth_dist[1]

    # shape after stack is [N, 2], where N = H * W.
    uv_coordinates = np.stack((u_map.reshape(-1), v_map.reshape(-1)), axis=-1)

    return unproject_vectorized(uv_coordinates, adjusted_depth.reshape(-1),
                                camera_mtx, camera_dist)


# -----------------------------------------------------------------------------
# MATH UTILS
# -----------------------------------------------------------------------------


def sample_distribution(prob, n_samples=1):
    """Sample data point from a custom distribution."""
    flat_prob = prob.flatten() / np.sum(prob)
    rand_ind = np.random.choice(
        np.arange(len(flat_prob)), n_samples, p=flat_prob, replace=False)
    rand_ind_coords = np.array(np.unravel_index(rand_ind, prob.shape)).T
    return np.int32(rand_ind_coords.squeeze())


# -------------------------------------------------------------------------
# Transformation Helper Functions
# -------------------------------------------------------------------------


def invert(pose):
    return p.invertTransform(pose[0], pose[1])


def multiply(pose0, pose1):
    return p.multiplyTransforms(pose0[0], pose0[1], pose1[0], pose1[1])


def apply(pose, position):
    position = np.float32(position)
    position_shape = position.shape
    position = np.float32(position).reshape(3, -1)
    rotation = np.float32(p.getMatrixFromQuaternion(pose[1])).reshape(3, 3)
    translation = np.float32(pose[0]).reshape(3, 1)
    position = rotation @ position + translation
    return tuple(position.reshape(position_shape))


def eulerXYZ_to_quatXYZW(rotation):  # pylint: disable=invalid-name
    """Abstraction for converting from a 3-parameter rotation to quaterion.
  
    This will help us easily switch which rotation parameterization we use.
    Quaternion should be in xyzw order for pybullet.
  
    Args:
      rotation: a 3-parameter rotation, in xyz order tuple of 3 floats
  
    Returns:
      quaternion, in xyzw order, tuple of 4 floats
    """
    euler_zxy = (rotation[2], rotation[0], rotation[1])
    quaternion_wxyz = euler.euler2quat(*euler_zxy, axes='szxy')
    q = quaternion_wxyz
    quaternion_xyzw = (q[1], q[2], q[3], q[0])
    return quaternion_xyzw


def quatXYZW_to_eulerXYZ(quaternion_xyzw):  # pylint: disable=invalid-name
    """Abstraction for converting from quaternion to a 3-parameter toation.
  
    This will help us easily switch which rotation parameterization we use.
    Quaternion should be in xyzw order for pybullet.
  
    Args:
      quaternion_xyzw: in xyzw order, tuple of 4 floats
  
    Returns:
      rotation: a 3-parameter rotation, in xyz order, tuple of 3 floats
    """
    q = quaternion_xyzw
    quaternion_wxyz = np.array([q[3], q[0], q[1], q[2]])
    euler_zxy = euler.quat2euler(quaternion_wxyz, axes='szxy')
    euler_xyz = (euler_zxy[1], euler_zxy[2], euler_zxy[0])
    return euler_xyz


def apply_transform(transform_to_from, points_from):
    r"""Transforms points (3D) into new frame.
  
    Using transform_to_from notation.
  
    Args:
      transform_to_from: numpy.ndarray of shape [B,4,4], SE3
      points_from: numpy.ndarray of shape [B,3,N]
  
    Returns:
      points_to: numpy.ndarray of shape [B,3,N]
    """
    num_points = points_from.shape[-1]

    # non-batched
    if len(transform_to_from.shape) == 2:
        ones = np.ones((1, num_points))

        # makes these each into homogenous vectors
        points_from = np.vstack((points_from, ones))  # [4,N]
        points_to = transform_to_from @ points_from  # [4,N]
        return points_to[0:3, :]  # [3,N]

    # batched
    else:
        assert len(transform_to_from.shape) == 3
        batch_size = transform_to_from.shape[0]
        zeros = np.ones((batch_size, 1, num_points))
        points_from = np.concatenate((points_from, zeros), axis=1)
        assert points_from.shape[1] == 4
        points_to = transform_to_from @ points_from
        return points_to[:, 0:3, :]


# -----------------------------------------------------------------------------
# IMAGE UTILS
# -----------------------------------------------------------------------------


# def preprocess(img, dist='transporter'):
#     """Pre-process input (subtract mean, divide by std)."""

#     transporter_color_mean = [0.18877631, 0.18877631, 0.18877631]
#     transporter_color_std = [0.07276466, 0.07276466, 0.07276466]
#     transporter_depth_mean = 0.00509261
#     transporter_depth_std = 0.00903967

#     franka_color_mean = [0.622291933, 0.628313992, 0.623031488]
#     franka_color_std = [0.168154213, 0.17626014, 0.184527364]
#     franka_depth_mean = 0.872146842
#     franka_depth_std = 0.195743116

#     clip_color_mean = [0.48145466, 0.4578275, 0.40821073]
#     clip_color_std = [0.26862954, 0.26130258, 0.27577711]

#     # choose distribution
#     if dist == 'clip':
#         color_mean = clip_color_mean
#         color_std = clip_color_std
#     elif dist == 'mdetr':
#         color_mean = [0.485, 0.456, 0.406]
#         color_std = [0.229, 0.224, 0.225]
#     elif dist == 'franka':
#         color_mean = franka_color_mean
#         color_std = franka_color_std
#     else:
#         color_mean = transporter_color_mean
#         color_std = transporter_color_std

#     if dist == 'franka':
#         depth_mean = franka_depth_mean
#         depth_std = franka_depth_std
#     else:
#         depth_mean = transporter_depth_mean
#         depth_std = transporter_depth_std

#     # convert to pytorch tensor (if required)
#     if type(img) == torch.Tensor:
#         def cast_shape(stat, img):
#             tensor = torch.from_numpy(np.array(stat)).to(device=img.device, dtype=img.dtype)
#             tensor = tensor.unsqueeze(0).unsqueeze(-1).unsqueeze(-1)
#             tensor = tensor.repeat(img.shape[0], 1, img.shape[-2], img.shape[-1])
#             return tensor

#         color_mean = cast_shape(color_mean, img)
#         color_std = cast_shape(color_std, img)
#         depth_mean = cast_shape(depth_mean, img)
#         depth_std = cast_shape(depth_std, img)

#         # normalize
#         img = img.clone()
#         img[:, :3, :, :] = ((img[:, :3, :, :] / 255 - color_mean) / color_std)
#         img[:, 3:, :, :] = ((img[:, 3:, :, :] - depth_mean) / depth_std)
#     else:
#         # normalize
#         img[:, :, :3] = (img[:, :, :3] / 255 - color_mean) / color_std
#         img[:, :, 3:] = (img[:, :, 3:] - depth_mean) / depth_std

#     # if dist == 'franka' or dist == 'transporter':
#     #     print(np.mean(img[:,:3,:,:].detach().cpu().numpy(), axis=(0,2,3)),
#     #           np.mean(img[:,3,:,:].detach().cpu().numpy()))

#     return img


# def map_kit_scale(scale):
#     return (scale[0] / 10, scale[1] / 10, scale[2] / 10)


# def deprocess(img):
#     color_mean = 0.18877631
#     depth_mean = 0.00509261
#     color_std = 0.07276466
#     depth_std = 0.00903967

#     img[:, :, :3] = np.uint8(((img[:, :, :3] * color_std) + color_mean) * 255)
#     img[:, :, 3:] = np.uint8(((img[:, :, 3:] * depth_std) + depth_mean) * 255)
#     return img


# def get_fused_heightmap(obs, configs, bounds, pix_size):
#     """Reconstruct orthographic heightmaps with segmentation masks."""
#     heightmaps, colormaps = reconstruct_heightmaps(
#         obs['color'], obs['depth'], configs, bounds, pix_size)
#     colormaps = np.float32(colormaps)
#     heightmaps = np.float32(heightmaps)

#     # Fuse maps from different views.
#     valid = np.sum(colormaps, axis=3) > 0
#     repeat = np.sum(valid, axis=0)
#     repeat[repeat == 0] = 1
#     cmap = np.sum(colormaps, axis=0) / repeat[Ellipsis, None]
#     cmap = np.uint8(np.round(cmap))
#     hmap = np.max(heightmaps, axis=0)  # Max to handle occlusions.
#     return cmap, hmap


# def get_image_transform(theta, trans, pivot=(0, 0)):
#     """Compute composite 2D rigid transformation matrix."""
#     # Get 2D rigid transformation matrix that rotates an image by theta (in
#     # radians) around pivot (in pixels) and translates by trans vector (in
#     # pixels)
#     pivot_t_image = np.array([[1., 0., -pivot[0]], [0., 1., -pivot[1]],
#                               [0., 0., 1.]])
#     image_t_pivot = np.array([[1., 0., pivot[0]], [0., 1., pivot[1]],
#                               [0., 0., 1.]])
#     transform = np.array([[np.cos(theta), -np.sin(theta), trans[0]],
#                           [np.sin(theta), np.cos(theta), trans[1]], [0., 0., 1.]])
#     return np.dot(image_t_pivot, np.dot(transform, pivot_t_image))


# def check_transform(image, pixel, transform):
#     """Valid transform only if pixel locations are still in FoV after transform."""
#     new_pixel = np.flip(
#         np.int32(
#             np.round(
#                 np.dot(transform,
#                        np.float32([pixel[1], pixel[0],
#                                    1.]).reshape(3, 1))))[:2].squeeze())
#     valid = np.all(
#         new_pixel >= 0
#     ) and new_pixel[0] < image.shape[0] and new_pixel[1] < image.shape[1]
#     return valid, new_pixel


# def get_se3_from_image_transform(theta, trans, pivot, heightmap, bounds,
#                                  pixel_size):
#     """Calculate SE3 from image transform."""
#     position_center = pix_to_xyz(
#         np.flip(np.int32(np.round(pivot))),
#         heightmap,
#         bounds,
#         pixel_size,
#         skip_height=False)
#     new_position_center = pix_to_xyz(
#         np.flip(np.int32(np.round(pivot + trans))),
#         heightmap,
#         bounds,
#         pixel_size,
#         skip_height=True)
#     # Don't look up the z height, it might get augmented out of frame
#     new_position_center = (new_position_center[0], new_position_center[1],
#                            position_center[2])

#     delta_position = np.array(new_position_center) - np.array(position_center)

#     t_world_center = np.eye(4)
#     t_world_center[0:3, 3] = np.array(position_center)

#     t_centernew_center = np.eye(4)
#     euler_zxy = (-theta, 0, 0)
#     t_centernew_center[0:3, 0:3] = euler.euler2mat(
#         *euler_zxy, axes='szxy')[0:3, 0:3]

#     t_centernew_center_tonly = np.eye(4)
#     t_centernew_center_tonly[0:3, 3] = -delta_position
#     t_centernew_center = t_centernew_center @ t_centernew_center_tonly

#     t_world_centernew = t_world_center @ np.linalg.inv(t_centernew_center)
#     return t_world_center, t_world_centernew


# def get_random_image_transform_params(image_size, theta_sigma=60):
#     theta = np.random.normal(0, np.deg2rad(theta_sigma))

#     trans_sigma = np.min(image_size) / 6
#     trans = np.random.normal(0, trans_sigma, size=2)  # [x, y]
#     pivot = (image_size[1] / 2, image_size[0] / 2)
#     return theta, trans, pivot


# def q_mult(q1, q2):
#     w1, x1, y1, z1 = q1
#     w2, x2, y2, z2 = q2
#     w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
#     x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
#     y = w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2
#     z = w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2
#     return (w, x, y, z)


# def perturb(input_image, pixels, theta_sigma=60, add_noise=False):
#     """Data augmentation on images."""
#     image_size = input_image.shape[:2]

#     # Compute random rigid transform.
#     while True:
#         theta, trans, pivot = get_random_image_transform_params(image_size,
#                                                                 theta_sigma=theta_sigma)
#         transform = get_image_transform(theta, trans, pivot)
#         transform_params = theta, trans, pivot

#         # Ensure pixels remain in the image after transform.
#         is_valid = True
#         new_pixels = []
#         new_rounded_pixels = []
#         for pixel in pixels:
#             pixel = np.float32([pixel[1], pixel[0], 1.]).reshape(3, 1)

#             rounded_pixel = np.int32(np.round(transform @ pixel))[:2].squeeze()
#             rounded_pixel = np.flip(rounded_pixel)

#             pixel = (transform @ pixel)[:2].squeeze()
#             pixel = np.flip(pixel)

#             in_fov_rounded = rounded_pixel[0] < image_size[0] and rounded_pixel[
#                 1] < image_size[1]
#             in_fov = pixel[0] < image_size[0] and pixel[1] < image_size[1]

#             is_valid = is_valid and np.all(rounded_pixel >= 0) and np.all(
#                 pixel >= 0) and in_fov_rounded and in_fov

#             new_pixels.append(pixel)
#             new_rounded_pixels.append(rounded_pixel)
#         if is_valid:
#             break

#     # Apply rigid transform to image and pixel labels.
#     input_image = cv2.warpAffine(
#         input_image,
#         transform[:2, :], (image_size[1], image_size[0]),
#         flags=cv2.INTER_LINEAR)

#     # Apply noise
#     color = np.int32(input_image[:, :, :3])
#     depth = np.float32(input_image[:, :, 3:])

#     if add_noise:
#         color += np.int32(np.random.normal(0, 3, image_size + (3,)))
#         color = np.uint8(np.clip(color, 0, 255))

#         depth += np.float32(np.random.normal(0, 0.003, image_size + (3,)))

#     input_image = np.concatenate((color, depth), axis=2)

#     # length of 5
#     transform_params = np.array([theta, trans[0], trans[1], pivot[0], pivot[1]])
#     return input_image, new_pixels, new_rounded_pixels, transform_params


# def apply_perturbation(input_image, transform_params):
#     '''Apply data augmentation with specific transform params'''
#     image_size = input_image.shape[:2]

#     # Apply rigid transform to image and pixel labels.
#     theta, trans, pivot = transform_params[0], transform_params[1:3], transform_params[3:5]
#     transform = get_image_transform(theta, trans, pivot)

#     input_image = cv2.warpAffine(
#         input_image,
#         transform[:2, :], (image_size[1], image_size[0]),
#         flags=cv2.INTER_LINEAR)
#     return input_image


# class ImageRotator:
#     """Rotate for n rotations."""

#     # Reference: https://kornia.readthedocs.io/en/latest/tutorials/warp_affine.html?highlight=rotate

#     def __init__(self, n_rotations):
#         self.angles = []
#         for i in range(n_rotations):
#             theta = i * 2 * 180 / n_rotations
#             self.angles.append(theta)

#     def __call__(self, x_list, pivot, reverse=False):
#         rot_x_list = []
#         for i, angle in enumerate(self.angles):
#             x = x_list[i]  # .unsqueeze(0)
#             # create transformation (rotation)
#             size = len(x)
#             alpha = angle if not reverse else (-1.0 * angle)  # in degrees
#             angle = torch.ones(size) * alpha

#             # define the rotation center
#             if type(pivot) is not torch.Tensor:
#                 center = torch.FloatTensor(pivot)[..., [1, 0]]
#                 center = center.view(1, -1).repeat((size, 1))
#             else:
#                 center = pivot[..., [1, 0]].view(1, -1).clone().to(angle.device)
#             # center: torch.tensor = torch.ones(size, 2)
#             # center[..., 0] = int(pivot[1])
#             # center[..., 1] = int(pivot[0])

#             # define the scale factor
#             scale = torch.ones(size, 2)

#             # # compute the transformation matrix
#             M = kornia.geometry.get_rotation_matrix2d(center, angle, scale)
#             # x_warped = torchvision.transforms.functional.affine(x.float(), scale=1., 
#             #             center=[int(pivot[1]),int(pivot[0])], 
#             #             angle=alpha, translate=[0,0], shear=0, 
#             #             interpolation= torchvision.transforms.InterpolationMode.BILINEAR)

#             # apply the transformation to original image
#             # M = M.repeat(len(x), 1, 1)
#             _, _, h, w = x.shape
#             x_warped = kornia.geometry.transform.warp_affine(x.float(), M.to(x.device),
#                                                              dsize=(h, w))
#             x_warped = x_warped
#             rot_x_list.append(x_warped)

#         return rot_x_list


# KD Tree Utils
# Construct K-D Tree to roughly estimate how many objects can fit inside the box.
class TreeNode:

    def __init__(self, parent, children, bbox):
        self.parent = parent
        self.children = children
        self.bbox = bbox  # min x, min y, min z, max x, max y, max z


def KDTree(node, min_object_dim, margin, bboxes):
    size = node.bbox[3:] - node.bbox[:3]

    # Choose which axis to split.
    split = size > 2 * min_object_dim
    if np.sum(split) == 0:
        bboxes.append(node.bbox)
        return
    split = np.float32(split) / np.sum(split)
    split_axis = np.random.choice(range(len(split)), 1, p=split)[0]

    # Split along chosen axis and create 2 children
    cut_ind = np.random.rand() * \
              (size[split_axis] - 2 * min_object_dim) + \
              node.bbox[split_axis] + min_object_dim
    child1_bbox = node.bbox.copy()
    child1_bbox[3 + split_axis] = cut_ind - margin / 2.
    child2_bbox = node.bbox.copy()
    child2_bbox[split_axis] = cut_ind + margin / 2.
    node.children = [
        TreeNode(node, [], bbox=child1_bbox),
        TreeNode(node, [], bbox=child2_bbox)
    ]
    KDTree(node.children[0], min_object_dim, margin, bboxes)
    KDTree(node.children[1], min_object_dim, margin, bboxes)


# -----------------------------------------------------------------------------
# Shape Name UTILS
# -----------------------------------------------------------------------------
google_seen_obj_shapes = {
    'train': [
        'alarm clock',
        'android toy',
        'black boot with leopard print',
        'black fedora',
        'black razer mouse',
        'black sandal',
        'black shoe with orange stripes',
        'bull figure',
        'butterfinger chocolate',
        'c clamp',
        'can opener',
        'crayon box',
        'dog statue',
        'frypan',
        'green and white striped towel',
        'grey soccer shoe with cleats',
        'hard drive',
        'honey dipper',
        'magnifying glass',
        'mario figure',
        'nintendo 3ds',
        'nintendo cartridge',
        'office depot box',
        'orca plush toy',
        'pepsi gold caffeine free box',
        'pepsi wild cherry box',
        'porcelain cup',
        'purple tape',
        'red and white flashlight',
        'rhino figure',
        'rocket racoon figure',
        'scissors',
        'silver tape',
        'spatula with purple head',
        'spiderman figure',
        'tablet',
        'toy school bus',
    ],
    'val': [
        'ball puzzle',
        'black and blue sneakers',
        'black shoe with green stripes',
        'brown fedora',
        'dinosaur figure',
        'hammer',
        'light brown boot with golden laces',
        'lion figure',
        'pepsi max box',
        'pepsi next box',
        'porcelain salad plate',
        'porcelain spoon',
        'red and white striped towel',
        'red cup',
        'screwdriver',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure'
    ],
    'test': [
        'ball puzzle',
        'black and blue sneakers',
        'black shoe with green stripes',
        'brown fedora',
        'dinosaur figure',
        'hammer',
        'light brown boot with golden laces',
        'lion figure',
        'pepsi max box',
        'pepsi next box',
        'porcelain salad plate',
        'porcelain spoon',
        'red and white striped towel',
        'red cup',
        'screwdriver',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure'
    ],
}

google_unseen_obj_shapes = {
    'train': [
        'alarm clock',
        'android toy',
        'black boot with leopard print',
        'black fedora',
        'black razer mouse',
        'black sandal',
        'black shoe with orange stripes',
        'bull figure',
        'butterfinger chocolate',
        'c clamp',
        'can opener',
        'crayon box',
        'dog statue',
        'frypan',
        'green and white striped towel',
        'grey soccer shoe with cleats',
        'hard drive',
        'honey dipper',
        'magnifying glass',
        'mario figure',
        'nintendo 3ds',
        'nintendo cartridge',
        'office depot box',
        'orca plush toy',
        'pepsi gold caffeine free box',
        'pepsi wild cherry box',
        'porcelain cup',
        'purple tape',
        'red and white flashlight',
        'rhino figure',
        'rocket racoon figure',
        'scissors',
        'silver tape',
        'spatula with purple head',
        'spiderman figure',
        'tablet',
        'toy school bus',
    ],
    'val': [
        'ball puzzle',
        'black and blue sneakers',
        'black shoe with green stripes',
        'brown fedora',
        'dinosaur figure',
        'hammer',
        'light brown boot with golden laces',
        'lion figure',
        'pepsi max box',
        'pepsi next box',
        'porcelain salad plate',
        'porcelain spoon',
        'red and white striped towel',
        'red cup',
        'screwdriver',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure'
    ],
    'test': [
        'ball puzzle',
        'black and blue sneakers',
        'black shoe with green stripes',
        'brown fedora',
        'dinosaur figure',
        'hammer',
        'light brown boot with golden laces',
        'lion figure',
        'pepsi max box',
        'pepsi next box',
        'porcelain salad plate',
        'porcelain spoon',
        'red and white striped towel',
        'red cup',
        'screwdriver',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure'
    ],
}

google_all_shapes = {
    'train': [
        'alarm clock',
        'android toy',
        'ball puzzle',
        'black and blue sneakers',
        'black boot with leopard print',
        'black fedora',
        'black razer mouse',
        'black sandal',
        'black shoe with green stripes',
        'black shoe with orange stripes',
        'brown fedora',
        'bull figure',
        'butterfinger chocolate',
        'c clamp',
        'can opener',
        'crayon box',
        'dinosaur figure',
        'dog statue',
        'frypan',
        'green and white striped towel',
        'grey soccer shoe with cleats',
        'hammer',
        'hard drive',
        'honey dipper',
        'light brown boot with golden laces',
        'lion figure',
        'magnifying glass',
        'mario figure',
        'nintendo 3ds',
        'nintendo cartridge',
        'office depot box',
        'orca plush toy',
        'pepsi gold caffeine free box',
        'pepsi max box',
        'pepsi next box',
        'pepsi wild cherry box',
        'porcelain cup',
        'porcelain salad plate',
        'porcelain spoon',
        'purple tape',
        'red and white flashlight',
        'red and white striped towel',
        'red cup',
        'rhino figure',
        'rocket racoon figure',
        'scissors',
        'screwdriver',
        'silver tape',
        'spatula with purple head',
        'spiderman figure',
        'tablet',
        'toy school bus',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure',
    ],
    'val': [
        'alarm clock',
        'android toy',
        'ball puzzle',
        'black and blue sneakers',
        'black boot with leopard print',
        'black fedora',
        'black razer mouse',
        'black sandal',
        'black shoe with green stripes',
        'black shoe with orange stripes',
        'brown fedora',
        'bull figure',
        'butterfinger chocolate',
        'c clamp',
        'can opener',
        'crayon box',
        'dinosaur figure',
        'dog statue',
        'frypan',
        'green and white striped towel',
        'grey soccer shoe with cleats',
        'hammer',
        'hard drive',
        'honey dipper',
        'light brown boot with golden laces',
        'lion figure',
        'magnifying glass',
        'mario figure',
        'nintendo 3ds',
        'nintendo cartridge',
        'office depot box',
        'orca plush toy',
        'pepsi gold caffeine free box',
        'pepsi max box',
        'pepsi next box',
        'pepsi wild cherry box',
        'porcelain cup',
        'porcelain salad plate',
        'porcelain spoon',
        'purple tape',
        'red and white flashlight',
        'red and white striped towel',
        'red cup',
        'rhino figure',
        'rocket racoon figure',
        'scissors',
        'screwdriver',
        'silver tape',
        'spatula with purple head',
        'spiderman figure',
        'tablet',
        'toy school bus',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure',
    ],
    'test': [
        'alarm clock',
        'android toy',
        'ball puzzle',
        'black and blue sneakers',
        'black boot with leopard print',
        'black fedora',
        'black razer mouse',
        'black sandal',
        'black shoe with green stripes',
        'black shoe with orange stripes',
        'brown fedora',
        'bull figure',
        'butterfinger chocolate',
        'c clamp',
        'can opener',
        'crayon box',
        'dinosaur figure',
        'dog statue',
        'frypan',
        'green and white striped towel',
        'grey soccer shoe with cleats',
        'hammer',
        'hard drive',
        'honey dipper',
        'light brown boot with golden laces',
        'lion figure',
        'magnifying glass',
        'mario figure',
        'nintendo 3ds',
        'nintendo cartridge',
        'office depot box',
        'orca plush toy',
        'pepsi gold caffeine free box',
        'pepsi max box',
        'pepsi next box',
        'pepsi wild cherry box',
        'porcelain cup',
        'porcelain salad plate',
        'porcelain spoon',
        'purple tape',
        'red and white flashlight',
        'red and white striped towel',
        'red cup',
        'rhino figure',
        'rocket racoon figure',
        'scissors',
        'screwdriver',
        'silver tape',
        'spatula with purple head',
        'spiderman figure',
        'tablet',
        'toy school bus',
        'toy train',
        'unicorn toy',
        'white razer mouse',
        'yoshi figure',
    ],
}
assembling_kit_shapes = {
    0: "letter R shape",
    1: "letter A shape",
    2: "triangle",
    3: "square",
    4: "plus",
    5: "letter T shape",
    6: "diamond",
    7: "pentagon",
    8: "rectangle",
    9: "flower",
    10: "star",
    11: "circle",
    12: "letter G shape",
    13: "letter V shape",
    14: "letter E shape",
    15: "letter L shape",
    16: "ring",
    17: "hexagon",
    18: "heart",
    19: "letter M shape",
}

# -----------------------------------------------------------------------------
# COLOR AND PLOT UTILS
# -----------------------------------------------------------------------------


# Colors (Tableau palette).
COLORS = {
    'blue': [78.0 / 255.0, 121.0 / 255.0, 167.0 / 255.0],
    'red': [255.0 / 255.0, 087.0 / 255.0, 089.0 / 255.0],
    'green': [089.0 / 255.0, 169.0 / 255.0, 078.0 / 255.0],
    'orange': [242.0 / 255.0, 142.0 / 255.0, 043.0 / 255.0],
    'yellow': [237.0 / 255.0, 201.0 / 255.0, 072.0 / 255.0],
    'purple': [176.0 / 255.0, 122.0 / 255.0, 161.0 / 255.0],
    'pink': [255.0 / 255.0, 157.0 / 255.0, 167.0 / 255.0],
    'cyan': [118.0 / 255.0, 183.0 / 255.0, 178.0 / 255.0],
    'brown': [156.0 / 255.0, 117.0 / 255.0, 095.0 / 255.0],
    'white': [255.0 / 255.0, 255.0 / 255.0, 255.0 / 255.0],
    'gray': [186.0 / 255.0, 176.0 / 255.0, 172.0 / 255.0],
    'indigo': [75.0 / 255.0, 0.0 / 255.0, 130.0 / 255.0],
    'violet': [143.0 / 255.0, 0.0 / 255.0, 255.0 / 255.0],
    'black': [0.0 / 255.0, 0.0 / 255.0, 0.0 / 255.0],
    'silver': [192.0 / 255.0, 192.0 / 255.0, 192.0 / 255.0],
    'gold': [255.0 / 255.0, 215.0 / 255.0, 0.0 / 255.0],
}
COLORS = defaultdict(lambda: [255.0 / 255.0, 0.0, 0.], COLORS)

COLORS_NAMES = list(COLORS.keys())
TRAIN_COLORS = ['blue', 'red', 'green', 'yellow', 'brown', 'purple', 'cyan', 'indigo', 'silver']
EVAL_COLORS = ['blue', 'red', 'green', 'orange', 'purple', 'pink', 'indigo', 'violet', 'gold']


def get_colors(mode='train', n_colors=-1, **kwargs):
    all_color_names = get_colors_names(mode)

    if n_colors == -1:
        all_color_names = all_color_names
    else:
        all_color_names = random.sample(all_color_names, n_colors)
    return [COLORS[cn] for cn in all_color_names], all_color_names


def get_colors_names(mode):
    if mode == 'test':
        return EVAL_COLORS
    else:
        return TRAIN_COLORS


def get_random_color():
    return get_colors(mode='train', n_colors=1)


def solve_hanoi_all(n_disks):
    # Solve Hanoi sequence with dynamic programming.
    hanoi_steps = []  # [[object index, from rod, to rod], ...]

    def solve_hanoi(n, t0, t1, t2):
        if n == 0:
            hanoi_steps.append([n, t0, t1])
            return
        solve_hanoi(n - 1, t0, t2, t1)
        hanoi_steps.append([n, t0, t1])
        solve_hanoi(n - 1, t2, t1, t0)

    solve_hanoi(n_disks - 1, 0, 2, 1)
    return hanoi_steps


def plot(fname,  # pylint: disable=dangerous-default-value
         title,
         ylabel,
         xlabel,
         data,
         xlim=[-np.inf, 0],
         xticks=None,
         ylim=[np.inf, -np.inf],
         show_std=True):
    """Plot frame data."""
    # Data is a dictionary that maps experiment names to tuples with 3
    # elements: x (size N array) and y (size N array) and y_std (size N array)

    # Get data limits.
    for name, (x, y, _) in data.items():
        del name
        y = np.array(y)
        xlim[0] = max(xlim[0], np.min(x))
        xlim[1] = max(xlim[1], np.max(x))
        ylim[0] = min(ylim[0], np.min(y))
        ylim[1] = max(ylim[1], np.max(y))

    # Draw background.
    plt.title(title, fontsize=14)
    plt.ylim(ylim)
    plt.ylabel(ylabel, fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlim(xlim)
    plt.xlabel(xlabel, fontsize=14)
    plt.grid(True, linestyle='-', color=[0.8, 0.8, 0.8])
    ax = plt.gca()
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_color('#000000')
    plt.rcParams.update({'font.size': 14})
    plt.rcParams['mathtext.default'] = 'regular'
    matplotlib.rcParams['pdf.fonttype'] = 42
    matplotlib.rcParams['ps.fonttype'] = 42

    # Draw data.
    color_iter = 0
    for name, (x, y, std) in data.items():
        del name
        x, y, std = np.float32(x), np.float32(y), np.float32(std)
        upper = np.clip(y + std, ylim[0], ylim[1])
        lower = np.clip(y - std, ylim[0], ylim[1])
        color = COLORS[list(COLORS.keys())[color_iter]]
        if show_std:
            plt.fill_between(x, upper, lower, color=color, linewidth=0, alpha=0.3)
        plt.plot(x, y, color=color, linewidth=2, marker='o', alpha=1.)
        color_iter += 1

    if xticks:
        plt.xticks(ticks=range(len(xticks)), labels=xticks, fontsize=14)
    else:
        plt.xticks(fontsize=14)
    plt.legend([name for name, _ in data.items()],
               loc='lower right', fontsize=14)
    plt.tight_layout()
    plt.savefig(fname)
    plt.clf()


# -----------------------------------------------------------------------------
# CAP UTILS
# -----------------------------------------------------------------------------

CORNER_POS = {
    'top left corner': (0.25, -0.5, 0),
    'top side': (0.25, 0, 0),
    'top right corner': (0.25, 0.5, 0),
    'left side': (0.5, -0.5, 0),
    'middle': (0.5, 0, 0),
    'right side': (0.5, 0.5, 0),
    'bottom left corner': (0.75, -0.5, 0),
    'bottom side': (0.75, 0, 0),
    'bottom right corner': (0.75, 0.5, 0),
}


def find_best_keys(words_dict, sentence):
    sentence_words = set(sentence.lower().split())
    max_match_count = 0
    best_keys = []
    for key, word_list in words_dict.items():
        match_count = len(set(word.lower() for word in word_list) & sentence_words)
        if match_count > max_match_count:
            max_match_count = match_count
            best_keys = [key]
        elif match_count == max_match_count:
            best_keys.append(key)
    return best_keys

def rotation_to_rotation_matrix(rot):
    if len(rot) == 4:
        x, y, z, w = rot
        R = np.array([
            [1 - 2*(y**2 + z**2), 2*(x*y - z*w), 2*(x*z + y*w)],
            [2*(x*y + z*w), 1 - 2*(x**2 + z**2), 2*(y*z - x*w)],
            [2*(x*z - y*w), 2*(y*z + x*w), 1 - 2*(x**2 + y**2)]
        ])
        return R
    elif len(rot) == 3:
        roll, yaw, pitch = rot
        R_x = np.array([
            [1, 0, 0],
            [0, np.cos(roll), -np.sin(roll)],
            [0, np.sin(roll), np.cos(roll)]
        ])
        R_y = np.array([
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])
        R_z = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw), np.cos(yaw), 0],
            [0, 0, 1]
        ]) 
        R = np.dot(R_z, np.dot(R_y, R_x))
        return R
    else:
        raise ValueError('rotation must be in 3 or 4 length')


# -----------------------------------------------------------------------------
# MESHCAT UTILS
# -----------------------------------------------------------------------------

# def create_visualizer(clear=True):
#     print('Waiting for meshcat server... have you started a server?')
#     vis = meshcat.Visualizer(zmq_url='tcp://127.0.0.1:6000')
#     if clear:
#         vis.delete()
#     return vis


# def make_frame(vis, name, h, radius, o=1.0):
#     """Add a red-green-blue triad to the Meschat visualizer.
  
#     Args:
#       vis (MeshCat Visualizer): the visualizer
#       name (string): name for this frame (should be unique)
#       h (float): height of frame visualization
#       radius (float): radius of frame visualization
#       o (float): opacity
#     """
#     vis[name]['x'].set_object(
#         g.Cylinder(height=h, radius=radius),
#         g.MeshLambertMaterial(color=0xff0000, reflectivity=0.8, opacity=o))
#     rotate_x = mtf.rotation_matrix(np.pi / 2.0, [0, 0, 1])
#     rotate_x[0, 3] = h / 2
#     vis[name]['x'].set_transform(rotate_x)

#     vis[name]['y'].set_object(
#         g.Cylinder(height=h, radius=radius),
#         g.MeshLambertMaterial(color=0x00ff00, reflectivity=0.8, opacity=o))
#     rotate_y = mtf.rotation_matrix(np.pi / 2.0, [0, 1, 0])
#     rotate_y[1, 3] = h / 2
#     vis[name]['y'].set_transform(rotate_y)

#     vis[name]['z'].set_object(
#         g.Cylinder(height=h, radius=radius),
#         g.MeshLambertMaterial(color=0x0000ff, reflectivity=0.8, opacity=o))
#     rotate_z = mtf.rotation_matrix(np.pi / 2.0, [1, 0, 0])
#     rotate_z[2, 3] = h / 2
#     vis[name]['z'].set_transform(rotate_z)


# def meshcat_visualize(vis, obs, act, info):
#     """Visualize data using meshcat."""

#     for key in sorted(info.keys()):
#         pose = info[key]
#         pick_transform = np.eye(4)
#         pick_transform[0:3, 3] = pose[0]
#         quaternion_wxyz = np.asarray(
#             [pose[1][3], pose[1][0], pose[1][1], pose[1][2]])
#         pick_transform[0:3, 0:3] = mtf.quaternion_matrix(quaternion_wxyz)[0:3, 0:3]
#         label = 'obj_' + str(key)
#         make_frame(vis, label, h=0.05, radius=0.0012, o=1.0)
#         vis[label].set_transform(pick_transform)

#     for cam_index in range(len(act['camera_config'])):
#         verts = unproject_depth_vectorized(
#             obs['depth'][cam_index], np.array([0, 1]),
#             np.array(act['camera_config'][cam_index]['intrinsics']).reshape(3, 3),
#             np.zeros(5))

#         # switch from [N,3] to [3,N]
#         verts = verts.T

#         cam_transform = np.eye(4)
#         cam_transform[0:3, 3] = act['camera_config'][cam_index]['position']
#         quaternion_xyzw = act['camera_config'][cam_index]['rotation']
#         quaternion_wxyz = np.asarray([
#             quaternion_xyzw[3], quaternion_xyzw[0], quaternion_xyzw[1],
#             quaternion_xyzw[2]
#         ])
#         cam_transform[0:3, 0:3] = mtf.quaternion_matrix(quaternion_wxyz)[0:3, 0:3]
#         verts = apply_transform(cam_transform, verts)

#         colors = obs['color'][cam_index].reshape(-1, 3).T / 255.0

#         vis['pointclouds/' + str(cam_index)].set_object(
#             g.PointCloud(position=verts, color=colors))


# -----------------------------------------------------------------------------
# CONFIG UTILS
# -----------------------------------------------------------------------------

def set_seed(seed, torch=False):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)

    if torch:
        import torch
        torch.manual_seed(seed)


def load_cfg(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data


def load_hydra_config(config_path):
    return OmegaConf.load(config_path)
