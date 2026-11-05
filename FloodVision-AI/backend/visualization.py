# -*- coding: utf-8 -*-
"""
Visualization & Augmented Reality Rendering Engine
FloodVision-AI Backend
"""

import base64
import cv2
import numpy as np

def encode_to_base64(image_array: np.ndarray, ext: str = ".jpg") -> str:
    """Encode OpenCV BGR or single-channel image into base64 string."""
    success, buffer = cv2.imencode(ext, image_array)
    if not success:
        return ""
    mime_type = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime_type};base64,{base64.b64encode(buffer).decode('utf-8')}"

def render_color_overlay(rgb_image: np.ndarray, binary_mask: np.ndarray) -> np.ndarray:
    """
    Produce high-contrast situational awareness overlay:
    - Flooded Water: Translucent Azure/Cyan (BGR: 240, 160, 20) with 45% alpha
    - Waterline Perimeter: Solid Red Contour (BGR: 30, 30, 240) with 2px stroke
    """
    bgr = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    tinted = bgr.copy()

    # Cyan tint for flooded pixels
    tinted[binary_mask == 1] = [240, 160, 20]

    # Alpha blending: 45% tint + 55% background
    blended = cv2.addWeighted(tinted, 0.45, bgr, 0.55, 0)

    # Shoreline boundary contour detection
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(blended, contours, -1, (30, 30, 240), 2)

    return blended

def generate_visual_artifacts(rgb_256: np.ndarray, binary_mask: np.ndarray):
    """
    Generate all base64 image representations for the frontend:
    - original_b64: Resized input image
    - mask_b64: Pure binary mask (0 = black, 255 = white)
    - overlay_b64: Augmented reality color overlay
    """
    bgr_256 = cv2.cvtColor(rgb_256, cv2.COLOR_RGB2BGR)
    overlay_bgr = render_color_overlay(rgb_256, binary_mask)
    mask_255 = (binary_mask * 255).astype(np.uint8)

    return {
        "original": encode_to_base64(bgr_256, ".jpg"),
        "mask": encode_to_base64(mask_255, ".png"),
        "overlay": encode_to_base64(overlay_bgr, ".jpg")
    }

