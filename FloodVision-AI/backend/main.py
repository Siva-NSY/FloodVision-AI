# -*- coding: utf-8 -*-
"""
Main Application Entry Point (FastAPI)
FloodVision-AI Backend
Author: 2401CS74 | IIT Patna CS3103
"""

import os
import io
import cv2
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from preprocessing import decode_image_bytes
from inference import run_segmentation_pipeline
from model_loader import get_available_models
from report_generator import generate_incident_report

app = FastAPI(
    title="FloodVision-AI API",
    description="Enterprise Knowledge Distillation Flood Area Segmentation Platform",
    version="2.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "public", "samples")

@app.get("/api/health")
def health_check():
    """Health status and telemetry."""
    return {
        "status": "healthy",
        "service": "FloodVision-AI Backend",
        "version": "2.0.0",
        "institution": "IIT Patna (CS3103 Machine Learning)",
        "roll_number": "2401CS74"
    }

@app.get("/api/models")
def list_models():
    """Return available machine learning models and specifications."""
    return {"models": get_available_models()}

@app.get("/api/samples")
def list_samples():
    """Return catalog of pre-loaded test scenes."""
    samples = [
        {"id": "sample1", "title": "Urban Flood Scene", "category": "Street", "url": "/samples/sample1.jpg"},
        {"id": "sample2", "title": "Submerged Roadway", "category": "Thoroughfare", "url": "/samples/sample2.jpg"},
        {"id": "sample3", "title": "Aerial Flood Basin", "category": "Aerial", "url": "/samples/sample3.jpg"},
        {"id": "sample4", "title": "Rural Inundation", "category": "Basin", "url": "/samples/sample4.jpg"}
    ]
    return {"samples": samples}

@app.post("/api/segment")
async def segment_image(
    image: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    model_choice: str = Form("rf_student"),
    threshold: float = Form(0.50)
):
    """
    Execute AI flood segmentation on uploaded image or selected sample.
    """
    bgr_img = None
    filename = "uploaded_scene.jpg"

    # Handle direct file upload
    if image is not None and image.filename != "":
        filename = image.filename
        content = await image.read()
        try:
            bgr_img = decode_image_bytes(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Image decoding failed: {str(e)}")

    # Handle preloaded demo sample selection
    elif sample_id:
        clean_id = os.path.basename(sample_id.strip())
        sample_path = os.path.join(SAMPLES_DIR, f"{clean_id}.jpg")
        if os.path.exists(sample_path):
            filename = f"{clean_id}.jpg"
            bgr_img = cv2.imread(sample_path, cv2.IMREAD_COLOR)
        else:
            raise HTTPException(status_code=404, detail=f"Sample scene '{sample_id}' not found.")

    if bgr_img is None:
        raise HTTPException(status_code=400, detail="Please upload a photo or select a sample scene.")

    # Execute Segmentation Pipeline
    try:
        result = run_segmentation_pipeline(
            bgr_image=bgr_img,
            model_key=model_choice,
            threshold=threshold
        )
        result["filename"] = filename
        result["success"] = True
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

class ReportExportRequest(BaseModel):
    analysis: dict
    filename: Optional[str] = "flood_scene.jpg"

@app.post("/api/report/export")
def export_report(req: ReportExportRequest):
    """Generate structured incident damage report."""
    report = generate_incident_report(req.analysis, req.filename)
    return report

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("FloodVision-AI Enterprise Backend (FastAPI)")
    print("Author: 2401CS74 | Department of CSE, IIT Patna")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 70)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)

