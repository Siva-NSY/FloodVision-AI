# -*- coding: utf-8 -*-
"""
Feature Extraction Module
FloodVision-AI Backend
Implements:
1. 18-Dimensional Rich Teacher Feature Space (phi_T)
2. 6-Dimensional Compact Student Feature Space (phi_S)
"""

import cv2
import numpy as np

def extract_teacher_features(rgb_image: np.ndarray) -> np.ndarray:
    """
    Extract 18-dimensional rich feature representation (phi_T).
    Features:
      0, 1, 2:   Normalized RGB [0, 1]
      3, 4, 5:   HSV Color Space
      6, 7, 8:   CIE-Lab Color Space
      9, 10, 11: Gaussian-smoothed RGB (sigma=1.0)
      12:        Local Mean in 5x5 box
      13:        Local Standard Deviation in 5x5 box (Texture variance)
      14:        Sobel Edge Gradient Magnitude
      15:        Laplacian of Gaussian (Edge curvature)
      16:        Normalized X coordinate in [0, 1]
      17:        Normalized Y coordinate in [0, 1] (Gravity spatial prior)
    Returns:
      Array of shape (H*W, 18) as float32
    """
    H, W, _ = rgb_image.shape
    features = []

    # 1. RGB Normalized
    rgb_norm = rgb_image.astype(np.float32) / 255.0
    features.append(rgb_norm)

    # 2. HSV Color Space
    hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[:, :, 0] /= 180.0
    hsv[:, :, 1] /= 255.0
    hsv[:, :, 2] /= 255.0
    features.append(hsv)

    # 3. CIE-Lab Color Space
    lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB).astype(np.float32)
    lab[:, :, 0] /= 255.0
    lab[:, :, 1] /= 255.0
    lab[:, :, 2] /= 255.0
    features.append(lab)

    # 4. Gaussian Smoothed RGB (sigma=1.0)
    blurred_rgb = cv2.GaussianBlur(rgb_norm, (5, 5), 1.0)
    features.append(blurred_rgb)

    # Grayscale for spatial filters
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

    # 5. Local Mean (5x5 box filter)
    local_mean = cv2.blur(gray, (5, 5))
    features.append(local_mean[:, :, np.newaxis])

    # 6. Local Standard Deviation (5x5)
    mean_sq = cv2.blur(gray ** 2, (5, 5))
    local_var = np.maximum(mean_sq - (local_mean ** 2), 0.0)
    local_std = np.sqrt(local_var)
    features.append(local_std[:, :, np.newaxis])

    # 7. Sobel Gradient Magnitude
    sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    sobel_mag = cv2.magnitude(sobel_x, sobel_y)
    features.append(sobel_mag[:, :, np.newaxis])

    # 8. Laplacian
    laplacian = np.abs(cv2.Laplacian(gray, cv2.CV_32F, ksize=3))
    features.append(laplacian[:, :, np.newaxis])

    # 9. Spatial Coordinates (X, Y)
    y_coords, x_coords = np.mgrid[0:H, 0:W].astype(np.float32)
    norm_x = (x_coords / (W - 1))[:, :, np.newaxis]
    norm_y = (y_coords / (H - 1))[:, :, np.newaxis]
    features.append(norm_x)
    features.append(norm_y)

    feature_matrix = np.concatenate(features, axis=2).reshape(-1, 18)
    return np.ascontiguousarray(feature_matrix, dtype=np.float32)

def extract_student_features(rgb_image: np.ndarray) -> np.ndarray:
    """
    Extract 6-dimensional compact feature representation (phi_S).
    Features:
      0, 1, 2: Normalized RGB [0, 1]
      3:       Local Mean in 3x3 box
      4:       Sobel Edge Gradient Magnitude
      5:       Normalized Y coordinate (Gravity spatial prior)
    Returns:
      Array of shape (H*W, 6) as float32
    """
    H, W, _ = rgb_image.shape
    features = []

    # 1. RGB Normalized
    rgb_norm = rgb_image.astype(np.float32) / 255.0
    features.append(rgb_norm)

    # Grayscale
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

    # 2. Local Mean (3x3 fast box)
    local_mean = cv2.blur(gray, (3, 3))
    features.append(local_mean[:, :, np.newaxis])

    # 3. Sobel Edge Gradient Magnitude
    sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    sobel_mag = cv2.magnitude(sobel_x, sobel_y)
    features.append(sobel_mag[:, :, np.newaxis])

    # 4. Normalized Vertical Coordinate Y
    y_coords, _ = np.mgrid[0:H, 0:W].astype(np.float32)
    norm_y = (y_coords / (H - 1))[:, :, np.newaxis]
    features.append(norm_y)

    feature_matrix = np.concatenate(features, axis=2).reshape(-1, 6)
    return np.ascontiguousarray(feature_matrix, dtype=np.float32)

