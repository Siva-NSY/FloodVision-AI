# -*- coding: utf-8 -*-
"""
Inference Engine & Spatial Analytics
FloodVision-AI Backend
"""

import time
import cv2
import numpy as np
from typing import Dict, Any

from preprocessing import preprocess_image
from feature_extraction import extract_teacher_features, extract_student_features
from model_loader import load_model_bundle
from visualization import generate_visual_artifacts

def compute_spatial_distribution(binary_mask: np.ndarray, flood_pixels: int, total_pixels: int) -> Dict[str, Any]:
    """
    Calculate factual spatial distribution of flood-class pixels in 2D image coordinates.
    Does NOT invent GPS coordinates, terrain elevations, or water depths.
    """
    H, W = binary_mask.shape
    mid_h, mid_w = H // 2, W // 2
    quadrant_area = mid_h * mid_w

    q_tl = int(np.sum(binary_mask[:mid_h, :mid_w] == 1))
    q_tr = int(np.sum(binary_mask[:mid_h, mid_w:] == 1))
    q_bl = int(np.sum(binary_mask[mid_h:, :mid_w] == 1))
    q_br = int(np.sum(binary_mask[mid_h:, mid_w:] == 1))

    top_half = q_tl + q_tr
    bottom_half = q_bl + q_br
    left_half = q_tl + q_bl
    right_half = q_tr + q_br

    if flood_pixels > 0:
        top_pct = round((top_half / flood_pixels) * 100, 1)
        bottom_pct = round((bottom_half / flood_pixels) * 100, 1)
        left_pct = round((left_half / flood_pixels) * 100, 1)
        right_pct = round((right_half / flood_pixels) * 100, 1)

        q_tl_pct = round((q_tl / flood_pixels) * 100, 1)
        q_tr_pct = round((q_tr / flood_pixels) * 100, 1)
        q_bl_pct = round((q_bl / flood_pixels) * 100, 1)
        q_br_pct = round((q_br / flood_pixels) * 100, 1)

        if bottom_half > top_half * 1.3:
            dist_summary = f"Identified flood-class pixels are predominantly concentrated in the lower half of the frame ({bottom_pct}% of water pixels across rows {mid_h}–{H-1})."
        elif top_half > bottom_half * 1.3:
            dist_summary = f"Identified flood-class pixels are predominantly concentrated in the upper half of the frame ({top_pct}% of water pixels across rows 0–{mid_h-1})."
        else:
            dist_summary = "Identified flood-class pixels are distributed across both the upper and lower sections of the image frame."
    else:
        top_pct = bottom_pct = left_pct = right_pct = 0.0
        q_tl_pct = q_tr_pct = q_bl_pct = q_br_pct = 0.0
        dist_summary = "No significant flood-class pixel clusters were detected in this image."

    return {
        "top_half_pixels": top_half,
        "bottom_half_pixels": bottom_half,
        "left_half_pixels": left_half,
        "right_half_pixels": right_half,
        "top_half_pct": top_pct,
        "bottom_half_pct": bottom_pct,
        "left_half_pct": left_pct,
        "right_half_pct": right_pct,
        "quadrants": {
            "top_left": {"pixels": q_tl, "pct_of_flood": q_tl_pct, "coverage": round((q_tl / quadrant_area) * 100, 1)},
            "top_right": {"pixels": q_tr, "pct_of_flood": q_tr_pct, "coverage": round((q_tr / quadrant_area) * 100, 1)},
            "bottom_left": {"pixels": q_bl, "pct_of_flood": q_bl_pct, "coverage": round((q_bl / quadrant_area) * 100, 1)},
            "bottom_right": {"pixels": q_br, "pct_of_flood": q_br_pct, "coverage": round((q_br / quadrant_area) * 100, 1)},
        },
        "summary": dist_summary,
        "coordinate_notice": "Note: Spatial distribution metrics reflect 2D image coordinates (pixel rows and columns), not geographic positions, ground elevations, or physical GPS coordinates."
    }

def run_segmentation_pipeline(
    bgr_image: np.ndarray,
    model_key: str = "rf_student",
    threshold: float = 0.50
) -> Dict[str, Any]:
    t_start = time.perf_counter()
    orig_h, orig_w = bgr_image.shape[:2]

    # 1. Preprocess
    rgb_256, _ = preprocess_image(bgr_image)

    # 2. Model Bundle
    bundle = load_model_bundle(model_key)
    model = bundle["model"]
    scaler = bundle["scaler"]
    feature_type = bundle.get("feature_type", "student")

    # 3. Feature Extraction
    t_feat_start = time.perf_counter()
    if feature_type == "teacher":
        features = extract_teacher_features(rgb_256)
        dims = 18
    else:
        features = extract_student_features(rgb_256)
        dims = 6
    t_feat_end = time.perf_counter()

    # 4. Feature Scaling & Prediction
    t_pred_start = time.perf_counter()
    features_scaled = scaler.transform(features)

    if model_key in ["rf_student", "rf_teacher"]:
        probs = model.predict_proba(features_scaled)[:, 1]
        binary_mask = (probs >= threshold).astype(np.uint8).reshape((256, 256))
    else:  # K-Means student
        preds = model.predict(np.ascontiguousarray(features_scaled, dtype=np.float32))
        cluster_map = bundle.get("cluster_map", {0: 0, 1: 1})
        binary_mask = np.array([cluster_map.get(p, 0) for p in preds], dtype=np.uint8).reshape((256, 256))

    # 3x3 median spatial smoothing to eliminate single-pixel sensor noise
    binary_mask = cv2.medianBlur(binary_mask, 3)
    t_pred_end = time.perf_counter()

    feature_time_ms = round((t_feat_end - t_feat_start) * 1000, 2)
    inference_time_ms = round((t_pred_end - t_pred_start) * 1000, 2)
    total_time_ms = round((time.perf_counter() - t_start) * 1000, 2)

    # 5. Factual Numerical Statistics
    total_pixels = 256 * 256
    flood_pixels = int(np.sum(binary_mask == 1))
    non_flood_pixels = total_pixels - flood_pixels

    flood_percentage = round((flood_pixels / total_pixels) * 100, 2)
    non_flood_percentage = round(100.0 - flood_percentage, 2)

    summary_statement = (
        f"The model identified flood-class regions covering {flood_percentage}% "
        f"({flood_pixels:,} pixels) of the uploaded image. "
        f"The remaining {non_flood_percentage}% ({non_flood_pixels:,} pixels) were classified as non-flood."
    )

    spatial_data = compute_spatial_distribution(binary_mask, flood_pixels, total_pixels)
    visuals = generate_visual_artifacts(rgb_256, binary_mask)

    return {
        "images": visuals,
        "analytics": {
            "original_resolution": f"{orig_w}×{orig_h}",
            "processing_resolution": "256×256",
            "total_pixels": total_pixels,
            "flood_pixels": flood_pixels,
            "non_flood_pixels": non_flood_pixels,
            "flood_percentage": flood_percentage,
            "non_flood_percentage": non_flood_percentage,
            "summary_statement": summary_statement,
            "spatial_distribution": spatial_data,
            "processing_time_ms": inference_time_ms,
            "feature_extraction_ms": feature_time_ms,
            "total_execution_ms": total_time_ms,
            "fps": round(1000.0 / max(inference_time_ms, 1.0), 1),
            "model_display_name": "FloodVision Image Segmentation Model",
            "technical_details": {
                "internal_identifier": model_key,
                "feature_space_dimensions": dims,
                "model_footprint_kb": bundle["file_size_kb"],
                "threshold_applied": threshold,
                "preprocessing": "Bilinear resizing to 256×256, standard feature scaling",
                "postprocessing": "3×3 median spatial smoothing filter"
            }
        }
    }
