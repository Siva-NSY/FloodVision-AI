# -*- coding: utf-8 -*-
"""
Model Loader & Memory Cache
FloodVision-AI Backend
"""

import os
import pickle
from typing import Dict, Any

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")

# In-memory model registry
_MODEL_CACHE: Dict[str, Any] = {}

MODEL_METADATA = {
    "rf_student": {
        "filename": "distilled_rf_student.pkl",
        "name": "Distilled Random Forest Student",
        "tag": "Edge Champion",
        "description": "Compressed 20-tree student trained on confident teacher pseudo-labels. 40ms inference, ideal for drones.",
        "dims": 6,
        "feature_type": "student",
        "recommended": True
    },
    "rf_teacher": {
        "filename": "rf_teacher.pkl",
        "name": "Random Forest Teacher",
        "tag": "High Precision",
        "description": "High-capacity 200-tree ensemble trained on 18-D rich feature space. Maximum segmentation accuracy.",
        "dims": 18,
        "feature_type": "teacher",
        "recommended": False
    },
    "km_student": {
        "filename": "distilled_km_student.pkl",
        "name": "Distilled K-Means Student",
        "tag": "Zero-Annotation",
        "description": "Unsupervised student initialized from teacher centroids. Zero training masks needed, 24ms speed.",
        "dims": 6,
        "feature_type": "student",
        "recommended": False
    }
}

def load_model_bundle(model_key: str) -> Dict[str, Any]:
    """Retrieve model bundle from in-memory cache or load from disk."""
    if model_key in _MODEL_CACHE:
        return _MODEL_CACHE[model_key]

    if model_key not in MODEL_METADATA:
        model_key = "rf_student"

    meta = MODEL_METADATA[model_key]
    filepath = os.path.join(MODELS_DIR, meta["filename"])

    if not os.path.exists(filepath):
        if model_key == "rf_teacher":
            print(f"[Notice] Teacher model ({filepath}) exceeds GitHub 100MB limit and is omitted. Falling back to flagship Distilled Student model.")
            return load_model_bundle("rf_student")
        raise FileNotFoundError(f"Model file missing: {filepath}")

    with open(filepath, "rb") as f:
        bundle = pickle.load(f)

    file_size_kb = round(os.path.getsize(filepath) / 1024, 2)
    bundle.update({
        "key": model_key,
        "name": meta["name"],
        "tag": meta["tag"],
        "description": meta["description"],
        "dims": meta["dims"],
        "feature_type": meta["feature_type"],
        "file_size_kb": file_size_kb
    })

    _MODEL_CACHE[model_key] = bundle
    return bundle

def get_available_models():
    """Return catalog of available models for UI dropdowns."""
    models_info = []
    for key, meta in MODEL_METADATA.items():
        filepath = os.path.join(MODELS_DIR, meta["filename"])
        size_kb = round(os.path.getsize(filepath) / 1024, 2) if os.path.exists(filepath) else 0.0
        models_info.append({
            "key": key,
            "name": meta["name"],
            "tag": meta["tag"],
            "description": meta["description"],
            "dims": meta["dims"],
            "file_size_kb": size_kb,
            "recommended": meta["recommended"]
        })
    return models_info

