# -*- coding: utf-8 -*-
"""
Image Preprocessing Pipeline
FloodVision-AI Backend
"""

import io
import cv2
import numpy as np
from typing import Tuple

IMAGE_SIZE = (256, 256)

def decode_image_bytes(image_bytes: bytes) -> np.ndarray:
    """Decode raw image bytes into OpenCV BGR uint8 array."""
    data = np.frombuffer(image_bytes, dtype=np.uint8)
    bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError("Failed to decode uploaded image data.")
    return bgr

def preprocess_image(bgr_image: np.ndarray, target_size: Tuple[int, int] = IMAGE_SIZE) -> Tuple[np.ndarray, np.ndarray]:
    """
    Preprocess image for feature extraction:
    - Resizes to target_size (256x256) using bilinear interpolation.
    - Converts BGR to RGB.
    Returns:
      (resized_rgb_uint8, resized_bgr_uint8)
    """
    resized_bgr = cv2.resize(bgr_image, target_size, interpolation=cv2.INTER_LINEAR)
    resized_rgb = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)
    return resized_rgb, resized_bgr

