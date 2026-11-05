# -*- coding: utf-8 -*-
"""
FloodVision AI - Environmental Image Intelligence Platform
Backend Server (Flask)
"""

import os
import io
import time
import base64
import pickle
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory

from src.feature_extraction import extract_teacher_features, extract_student_features

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

MODELS_DIR = os.path.join(os.path.dirname(__file__), "results", "models")
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "static", "samples")

LOADED_MODELS = {}

def get_or_load_model(model_key: str):
    """Lazy-load and cache models in RAM."""
    if model_key in LOADED_MODELS:
        return LOADED_MODELS[model_key]

    model_files = {
        "rf_student": "distilled_rf_student.pkl",
        "rf_teacher": "rf_teacher.pkl",
        "km_student": "distilled_km_student.pkl"
    }

    if model_key not in model_files:
        model_key = "rf_student"

    filepath = os.path.join(MODELS_DIR, model_files[model_key])
    if not os.path.exists(filepath):
        if model_key == "rf_teacher":
            print(f"[Notice] Teacher model ({filepath}) exceeds GitHub 100MB limit and is omitted. Falling back to flagship Distilled Student model.")
            return get_or_load_model("rf_student")
        raise FileNotFoundError(f"Model file missing: {filepath}")

    with open(filepath, "rb") as f:
        data = pickle.load(f)
        data["file_size_kb"] = round(os.path.getsize(filepath) / 1024, 2)
        LOADED_MODELS[model_key] = data

    return LOADED_MODELS[model_key]

def image_to_base64(img_bgr, ext=".png"):
    """Convert OpenCV image array to base64 data URI."""
    success, buffer = cv2.imencode(ext, img_bgr)
    if not success:
        return ""
    mime_type = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime_type};base64,{base64.b64encode(buffer).decode('utf-8')}"

def create_color_overlay(rgb_img, binary_mask):
    """
    Generate professional environmental overlay:
    - Water classification: Sky Blue tint (BGR: 225, 160, 40)
    - Perimeter boundary: Clean Red contour line (BGR: 40, 40, 220)
    """
    bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
    overlay = bgr_img.copy()

    # Soft blue tint for identified water pixels
    overlay[binary_mask == 1] = [225, 160, 40]

    # Blend 45% tint + 55% original photo
    blended = cv2.addWeighted(overlay, 0.45, bgr_img, 0.55, 0)

    # Edge waterline contour
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(blended, contours, -1, (40, 40, 220), 2)

    return blended

def compute_spatial_distribution(binary_mask: np.ndarray, flood_pixels: int, total_pixels: int):
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/static/samples/<path:filename>")
def serve_sample(filename):
    return send_from_directory(SAMPLES_DIR, filename)

@app.route("/api/segment", methods=["POST"])
def segment():
    t0_total = time.perf_counter()
    model_choice = request.form.get("model_choice", "rf_student")
    threshold = float(request.form.get("threshold", 0.50))
    sample_id = request.form.get("sample_id", "").strip()

    # 1. Acquire Image
    img_bgr = None
    input_filename = "uploaded_image.jpg"
    input_file_size_kb = 0.0

    if "image" in request.files and request.files["image"].filename != "":
        file = request.files["image"]
        input_filename = file.filename
        content = file.read()
        input_file_size_kb = round(len(content) / 1024, 1)
        data = np.frombuffer(content, dtype=np.uint8)
        img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    elif sample_id:
        clean_id = os.path.basename(sample_id.strip())
        sample_path = os.path.join(SAMPLES_DIR, f"{clean_id}.jpg")
        if os.path.exists(sample_path):
            input_filename = f"{clean_id}.jpg"
            input_file_size_kb = round(os.path.getsize(sample_path) / 1024, 1)
            img_bgr = cv2.imread(sample_path, cv2.IMREAD_COLOR)

    if img_bgr is None:
        return jsonify({"success": False, "error": "No valid image uploaded or sample selected."}), 400

    orig_h, orig_w = img_bgr.shape[:2]

    # 2. Preprocess Image (256x256, normalized RGB)
    rgb_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    resized_rgb = cv2.resize(rgb_img, (256, 256), interpolation=cv2.INTER_LINEAR)

    # 3. Model Bundle
    model_bundle = get_or_load_model(model_choice)
    model = model_bundle["model"]
    scaler = model_bundle["scaler"]
    feature_type = model_bundle.get("feature_type", "student")

    # 4. Feature Extraction & Latency
    t0_inf = time.perf_counter()
    if feature_type == "teacher":
        features = extract_teacher_features(resized_rgb)
        dims = 18
    else:
        features = extract_student_features(resized_rgb)
        dims = 6

    features_scaled = scaler.transform(features)

    # 5. Prediction
    if model_choice in ["rf_student", "rf_teacher"]:
        probs = model.predict_proba(features_scaled)[:, 1]
        binary_mask = (probs >= threshold).astype(np.uint8).reshape((256, 256))
    else:  # K-Means student
        preds = model.predict(np.ascontiguousarray(features_scaled, dtype=np.float32))
        cluster_map = model_bundle.get("cluster_map", {0: 0, 1: 1})
        binary_mask = np.array([cluster_map.get(p, 0) for p in preds], dtype=np.uint8).reshape((256, 256))

    # 3x3 median spatial smoothing to suppress single-pixel sensor noise
    binary_mask = cv2.medianBlur(binary_mask, 3)

    t1_inf = time.perf_counter()
    inference_time_ms = round((t1_inf - t0_inf) * 1000, 2)
    total_time_ms = round((time.perf_counter() - t0_total) * 1000, 2)

    # 6. Factual Mathematical Statistics
    total_pixels = 256 * 256
    flood_pixels = int(np.sum(binary_mask == 1))
    non_flood_pixels = total_pixels - flood_pixels

    flood_percentage = round((flood_pixels / total_pixels) * 100, 2)
    non_flood_percentage = round(100.0 - flood_percentage, 2)

    # Dynamic, factual explanation (strictly grounded in actual pixels)
    summary_statement = (
        f"The model identified flood-class regions covering {flood_percentage}% "
        f"({flood_pixels:,} pixels) of the uploaded image. "
        f"The remaining {non_flood_percentage}% ({non_flood_pixels:,} pixels) were classified as non-flood."
    )

    # Spatial distribution
    spatial_data = compute_spatial_distribution(binary_mask, flood_pixels, total_pixels)

    # 7. Render Visual Artifacts
    resized_bgr = cv2.cvtColor(resized_rgb, cv2.COLOR_RGB2BGR)
    overlay_bgr = create_color_overlay(resized_rgb, binary_mask)
    mask_visual = (binary_mask * 255).astype(np.uint8)

    orig_b64 = image_to_base64(resized_bgr, ".jpg")
    mask_b64 = image_to_base64(mask_visual, ".png")
    overlay_b64 = image_to_base64(overlay_bgr, ".jpg")

    return jsonify({
        "success": True,
        "images": {
            "original": orig_b64,
            "mask": mask_b64,
            "overlay": overlay_b64
        },
        "analytics": {
            "filename": input_filename,
            "file_size_kb": input_file_size_kb,
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
            "total_execution_ms": total_time_ms,
            "fps": round(1000.0 / max(inference_time_ms, 1.0), 1),
            "model_display_name": "FloodVision Image Segmentation Model",
            "technical_details": {
                "internal_identifier": model_choice,
                "feature_space_dimensions": dims,
                "model_footprint_kb": model_bundle.get("file_size_kb", 0),
                "threshold_applied": threshold,
                "preprocessing": "Bilinear resizing to 256×256, standard feature scaling",
                "postprocessing": "3×3 median spatial smoothing filter"
            }
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 70)
    print("FloodVision AI — Environmental Image Intelligence Platform")
    print(f"Server Active: http://0.0.0.0:{port}")
    print("=" * 70)
    app.run(host="0.0.0.0", port=port, debug=False)
