"""
Feature Extraction Module for Flood Area Segmentation
CS3103 Machine Learning Project - IIT Patna

Implements:
1. Rich Teacher Features (phi_T): dT = 18 dimensions (>= 12)
   - Color: RGB (3), HSV (3), CIE-Lab (3)
   - Neighborhood Context: Gaussian Blurred RGB (sigma=2) (3)
   - Local Texture Statistics: Local Mean (7x7) and Local Std (7x7) of Luminance L* (2)
   - Edges: Sobel gradient magnitude (1), Laplacian response (1)
   - Spatial Coordinates: Normalized row (y/H), normalized column (x/W) (2)

2. Compact Student Features (phi_S): dS = 6 dimensions (<= 6 and <= dT / 2 = 9)
   - Direct image features (strictly NO PCA projections):
   - Spectral: Red, Green, Blue (3)
   - Perceptual Chrominance: Hue, Saturation (2)
   - Spatial Prior: Normalized row coordinate (y/H) (1)
"""

import time
import cv2
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

# Pre-generate coordinate grids for 256x256 to accelerate feature extraction
_H, _W = 256, 256
_Y_GRID, _X_GRID = np.meshgrid(
    np.linspace(0, 1, _H, dtype=np.float32),
    np.linspace(0, 1, _W, dtype=np.float32),
    indexing='ij'
)

def extract_teacher_features(rgb_image: np.ndarray) -> np.ndarray:
    """
    Extract 18-dimensional rich feature representation for an image.
    Input: rgb_image (H, W, 3) uint8 [0, 255]
    Output: features (H*W, 18) float32
    """
    H, W, _ = rgb_image.shape
    img_f32 = rgb_image.astype(np.float32) / 255.0
    
    # 1. RGB (3 dims)
    r = img_f32[:, :, 0]
    g = img_f32[:, :, 1]
    b = img_f32[:, :, 2]
    
    # 2. HSV (3 dims)
    hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.float32)
    h = hsv[:, :, 0] / 179.0   # OpenCV H is [0, 179]
    s = hsv[:, :, 1] / 255.0   # S is [0, 255]
    v = hsv[:, :, 2] / 255.0   # V is [0, 255]
    
    # 3. CIE-Lab (3 dims)
    lab = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2LAB).astype(np.float32)
    l_chan = lab[:, :, 0] / 255.0
    a_chan = (lab[:, :, 1] - 128.0) / 128.0
    b_chan = (lab[:, :, 2] - 128.0) / 128.0
    
    # 4. Gaussian Blurred RGB (sigma=2) for neighborhood context (3 dims)
    blurred_rgb = cv2.GaussianBlur(img_f32, (0, 0), sigmaX=2.0)
    b_r = blurred_rgb[:, :, 0]
    b_g = blurred_rgb[:, :, 1]
    b_b = blurred_rgb[:, :, 2]
    
    # 5. Local Texture Statistics (7x7 window on L* channel) (2 dims)
    # Mean of L* and Std of L*
    kernel_size = (7, 7)
    local_mean = cv2.blur(l_chan, kernel_size)
    local_sq_mean = cv2.blur(l_chan ** 2, kernel_size)
    local_var = np.maximum(local_sq_mean - local_mean ** 2, 0)
    local_std = np.sqrt(local_var)
    
    # 6. Edge Features: Sobel magnitude and Laplacian on L* (2 dims)
    sobel_x = cv2.Sobel(l_chan, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(l_chan, cv2.CV_32F, 0, 1, ksize=3)
    sobel_mag = np.sqrt(sobel_x**2 + sobel_y**2)
    laplacian = np.abs(cv2.Laplacian(l_chan, cv2.CV_32F, ksize=3))
    
    # 7. Spatial Coordinates (2 dims)
    if H == _H and W == _W:
        y_coord = _Y_GRID
        x_coord = _X_GRID
    else:
        y_coord, x_coord = np.meshgrid(
            np.linspace(0, 1, H, dtype=np.float32),
            np.linspace(0, 1, W, dtype=np.float32),
            indexing='ij'
        )
        
    # Stack all 18 features: (H, W, 18) -> (H*W, 18)
    features = np.stack([
        r, g, b,             # 0, 1, 2: RGB
        h, s, v,             # 3, 4, 5: HSV
        l_chan, a_chan, b_chan, # 6, 7, 8: Lab
        b_r, b_g, b_b,       # 9, 10, 11: Blurred RGB
        local_mean, local_std, # 12, 13: Local statistics
        sobel_mag, laplacian, # 14, 15: Edges
        y_coord, x_coord     # 16, 17: Spatial coordinates
    ], axis=-1).reshape(-1, 18)
    
    return features.astype(np.float32)

def extract_student_features(rgb_image: np.ndarray) -> np.ndarray:
    """
    Extract 6-dimensional compact student features directly from image.
    Input: rgb_image (H, W, 3) uint8 [0, 255]
    Output: features (H*W, 6) float32
    """
    H, W, _ = rgb_image.shape
    img_f32 = rgb_image.astype(np.float32) / 255.0
    
    # 1. RGB (3 dims)
    r = img_f32[:, :, 0]
    g = img_f32[:, :, 1]
    b = img_f32[:, :, 2]
    
    # 2. Hue & Saturation (2 dims)
    hsv = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV).astype(np.float32)
    h = hsv[:, :, 0] / 179.0
    s = hsv[:, :, 1] / 255.0
    
    # 3. Normalized Vertical Position (y/H) (1 dim)
    if H == _H and W == _W:
        y_coord = _Y_GRID
    else:
        y_coord, _ = np.meshgrid(
            np.linspace(0, 1, H, dtype=np.float32),
            np.linspace(0, 1, W, dtype=np.float32),
            indexing='ij'
        )
        
    # Stack 6 features: (H*W, 6)
    features = np.stack([
        r, g, b,     # 0, 1, 2: RGB
        h, s,        # 3, 4: Hue, Saturation
        y_coord      # 5: Vertical position
    ], axis=-1).reshape(-1, 6)
    
    return features.astype(np.float32)

def benchmark_feature_extraction(num_images: int = 40) -> Dict[str, Any]:
    """
    Measure extraction time per image for both teacher and student feature extractors.
    """
    dummy_img = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    
    # Warmup
    _ = extract_teacher_features(dummy_img)
    _ = extract_student_features(dummy_img)
    
    # Benchmark Teacher
    t0 = time.perf_counter()
    for _ in range(num_images):
        _ = extract_teacher_features(dummy_img)
    t_teacher_total = time.perf_counter() - t0
    t_teacher_per_img = (t_teacher_total / num_images) * 1000.0 # ms
    
    # Benchmark Student
    t0 = time.perf_counter()
    for _ in range(num_images):
        _ = extract_student_features(dummy_img)
    t_student_total = time.perf_counter() - t0
    t_student_per_img = (t_student_total / num_images) * 1000.0 # ms
    
    feature_speedup = t_teacher_per_img / t_student_per_img
    
    return {
        "Teacher Dims (dT)": 18,
        "Teacher Time per Image (ms)": round(t_teacher_per_img, 2),
        "Student Dims (dS)": 6,
        "Student Time per Image (ms)": round(t_student_per_img, 2),
        "Feature Speedup": round(feature_speedup, 2)
    }

def get_feature_comparison_table() -> pd.DataFrame:
    """
    Returns the comprehensive feature specification and justification table.
    """
    data = [
        # Teacher features
        {"Model": "Teacher (phi_T)", "Feature Group": "Color (RGB)", "Dimensions": 3, 
         "Features": "Red, Green, Blue normalized [0, 1]", 
         "Domain Justification": "Provides base tri-stimulus spectral intensity of scene elements."},
        {"Model": "Teacher (phi_T)", "Feature Group": "Color (HSV)", "Dimensions": 3, 
         "Features": "Hue, Saturation, Value normalized [0, 1]", 
         "Domain Justification": "Decouples chromaticity from illumination; murky brown flood water displays low saturation and distinctive muddy hue."},
        {"Model": "Teacher (phi_T)", "Feature Group": "Color (CIE-Lab)", "Dimensions": 3, 
         "Features": "L*, a*, b* perceptual channels", 
         "Domain Justification": "Perceptually uniform space separating lightness (L*) from color-opponent dimensions (a*, b*)."},
        {"Model": "Teacher (phi_T)", "Feature Group": "Neighborhood Smoothing", "Dimensions": 3, 
         "Features": "Gaussian-blurred RGB (sigma=2.0)", 
         "Domain Justification": "Suppresses water surface ripple noise, glint, and specular sky reflections by integrating spatial context."},
        {"Model": "Teacher (phi_T)", "Feature Group": "Local Texture Statistics", "Dimensions": 2, 
         "Features": "Local Mean and Local Std of L* (7x7 window)", 
         "Domain Justification": "Water surfaces are spatially homogeneous (low variance) compared to complex textures of foliage, trees, and debris."},
        {"Model": "Teacher (phi_T)", "Feature Group": "Edge Characteristics", "Dimensions": 2, 
         "Features": "Sobel Gradient Magnitude, Laplacian on L*", 
         "Domain Justification": "Flood water bodies have low internal edge energy; structural boundaries, building edges, and trees display strong edge energy."},
        {"Model": "Teacher (phi_T)", "Feature Group": "Spatial Prior", "Dimensions": 2, 
         "Features": "Normalized Row (y/H), Normalized Col (x/W)", 
         "Domain Justification": "Gravitational prior: standing/flowing flood water settles at lower elevations (higher y index), while sky/trees dominate upper rows."},
        
        # Student features
        {"Model": "Student (phi_S)", "Feature Group": "Color (RGB)", "Dimensions": 3, 
         "Features": "Red, Green, Blue normalized [0, 1]", 
         "Domain Justification": "Compact raw spectral baseline directly computed from image with zero convolutional latency."},
        {"Model": "Student (phi_S)", "Feature Group": "Color (HSV)", "Dimensions": 2, 
         "Features": "Hue, Saturation normalized [0, 1]", 
         "Domain Justification": "Captures murky turbidity and low-saturation water appearance without multi-scale texture convolutions."},
        {"Model": "Student (phi_S)", "Feature Group": "Spatial Prior", "Dimensions": 1, 
         "Features": "Normalized Vertical Coordinate (y/H)", 
         "Domain Justification": "High-impact vertical position prior distinguishing sky/upper rooftops from low ground water at zero runtime cost."}
    ]
    return pd.DataFrame(data)

if __name__ == "__main__":
    df_feat = get_feature_comparison_table()
    print("Feature Specification Table:")
    print(df_feat.to_string(index=False))
    
    bench = benchmark_feature_extraction(num_images=50)
    print("\nFeature Extraction Timing Benchmark (50 runs):")
    for k, v in bench.items():
        print(f"  {k}: {v}")

