"""
Data Preprocessing Pipeline for Flood Area Segmentation
CS3103 Machine Learning Project - IIT Patna

Strictly adheres to official assignment requirements:
1. Mask binarisation: pixel >= 128 -> 1 (Flood), pixel < 128 -> 0 (Non-flood)
2. Image resizing: 256 x 256 (bilinear interpolation)
3. Mask resizing: 256 x 256 (nearest-neighbour interpolation)
4. Color space: OpenCV BGR converted to RGB
5. Fixed dataset splitting with random seed 42:
   - Labelled set L: 40 images (indices 87:127)
   - Unlabelled set U: 163 images (indices 127:290)
   - Validation set: 29 images (indices 58:87)
   - Test set: 58 images (indices 0:58)
"""

import os
import cv2
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

# Constants
IMAGE_SIZE = (256, 256)
RANDOM_SEED = 42

def get_dataset_splits(data_dir: str = "flood-area-segmentation") -> Dict[str, List[str]]:
    """
    Generate the exact fixed dataset split as specified on Page 2 of assignment.
    Robustly resolves data_dir regardless of whether called from project root or notebooks/ dir.
    """
    candidates = [
        data_dir,
        os.path.join("..", data_dir),
        "flood-area-segmentation",
        os.path.join("..", "flood-area-segmentation"),
        "dataset",
        os.path.join("..", "dataset")
    ]
    resolved_dir = None
    for cand in candidates:
        if os.path.exists(os.path.join(cand, "Image")):
            resolved_dir = cand
            break
            
    if resolved_dir is None:
        raise FileNotFoundError(f"Could not locate 'Image' folder in any candidate directory: {candidates}")
        
    data_dir = resolved_dir
    image_dir = os.path.join(data_dir, "Image")

    files = sorted(
        f for f in os.listdir(image_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )
    
    rng = np.random.default_rng(RANDOM_SEED)
    idx = rng.permutation(len(files))
    
    splits = {
        "test": [files[i] for i in idx[:58]],        # 58 images
        "val": [files[i] for i in idx[58:87]],       # 29 images
        "lab": [files[i] for i in idx[87:127]],      # 40 images (L)
        "unl": [files[i] for i in idx[127:]],       # 163 images (U)
        "data_dir": data_dir
    }
    return splits

def load_and_preprocess_image(file_path: str, target_size: Tuple[int, int] = IMAGE_SIZE) -> np.ndarray:
    """
    Load image, convert BGR to RGB, and resize to target_size.
    Returns RGB image as uint8 array (H, W, 3).
    """
    bgr_img = cv2.imread(file_path)
    if bgr_img is None:
        raise FileNotFoundError(f"Failed to read image at: {file_path}")
    rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
    resized_img = cv2.resize(rgb_img, target_size, interpolation=cv2.INTER_LINEAR)
    return resized_img

def load_and_preprocess_mask(file_path: str, target_size: Tuple[int, int] = IMAGE_SIZE) -> np.ndarray:
    """
    Load mask, binarise (>= 128 -> 1, else 0), and resize using nearest-neighbour.
    Returns binary mask as uint8 array (H, W) with values in {0, 1}.
    """
    raw_mask = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if raw_mask is None:
        raise FileNotFoundError(f"Failed to read mask at: {file_path}")
    binary_mask = (raw_mask >= 128).astype(np.uint8)
    resized_mask = cv2.resize(binary_mask, target_size, interpolation=cv2.INTER_NEAREST)
    return (resized_mask >= 1).astype(np.uint8)

def compute_split_statistics(splits: Dict[str, List[str]]) -> pd.DataFrame:
    """
    Compute total pixels and percentage of flood pixels across L, Val, and Test splits.
    Strictly adheres to data leakage prevention: Unlabelled U masks are never loaded.
    """
    data_dir = splits["data_dir"]
    stats = []
    
    for split_name in ["lab", "val", "test"]:
        file_list = splits[split_name]
        total_pixels = 0
        flood_pixels = 0
        
        for fname in file_list:
            mask_name = f"{os.path.splitext(fname)[0]}.png"
            mask_path = os.path.join(data_dir, "Mask", mask_name)
            mask = load_and_preprocess_mask(mask_path)
            total_pixels += mask.size
            flood_pixels += int(np.sum(mask))
            
        non_flood_pixels = total_pixels - flood_pixels
        flood_pct = (flood_pixels / total_pixels) * 100.0
        
        display_name = {
            "lab": "Labelled Training (L)",
            "val": "Validation Set",
            "test": "Test Set"
        }[split_name]
        
        stats.append({
            "Split": display_name,
            "Images": len(file_list),
            "Total Pixels": total_pixels,
            "Flood Pixels": flood_pixels,
            "Non-Flood Pixels": non_flood_pixels,
            "Flood Pixel %": round(flood_pct, 2),
            "Non-Flood Pixel %": round(100.0 - flood_pct, 2)
        })
        
    # Add Unlabelled set info (without accessing masks)
    stats.append({
        "Split": "Unlabelled Set (U)",
        "Images": len(splits["unl"]),
        "Total Pixels": len(splits["unl"]) * IMAGE_SIZE[0] * IMAGE_SIZE[1],
        "Flood Pixels": "N/A (No GT used)",
        "Non-Flood Pixels": "N/A (No GT used)",
        "Flood Pixel %": "N/A",
        "Non-Flood Pixel %": "N/A"
    })
    
    return pd.DataFrame(stats)

if __name__ == "__main__":
    splits = get_dataset_splits()
    print("Dataset split verification:")
    for k in ["lab", "unl", "val", "test"]:
        print(f"  {k}: {len(splits[k])} images")
    
    df_stats = compute_split_statistics(splits)
    print("\nSplit Class Distribution Statistics:")
    print(df_stats.to_string(index=False))
