# FloodVision AI — User & Consumer Guide

Welcome to **FloodVision AI**, an independent environmental image intelligence platform designed to extract actionable water boundaries and surface coverage metrics from aerial, drone, and ground-level flood photography.

---

## 🚀 How to Use the Application (4 Simple Steps)

### Step 1: Upload an Image or Choose a Benchmark Scene
* **Drag-and-Drop / Browse**: Drag any RGB flood photograph onto the ingestion area, or click **Browse Files** to select a file from your computer. Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`. All imagery is normalized to a standard matrix for analysis.
* **1-Click Benchmark Demos**: If you do not have an image at hand, click any of the 4 pre-calibrated benchmark scenes:
  1. **Urban**: Street inundation scenario featuring vehicles and buildings.
  2. **Street**: Asphalt roadway under reflective water accumulation.
  3. **Aerial**: High-altitude drone photograph showing extensive landscape flooding.
  4. **Rural**: Flood basin near agricultural fields and vegetation.

### Step 2: Review or Adjust Settings (Optional)
The system operates automatically with optimized default settings. If desired, expand **Advanced Settings (Optional)**:
* **FloodVision Fast Model (Default, 40ms)**: Ultra-fast ($<50\text{ ms}$ processing), lightweight ($444\text{ KB}$ memory footprint) model optimized for real-time edge and drone deployments.
* **High-Precision Extended Ensemble**: Multi-spectral $18$-dimensional feature ensemble for forensic post-disaster analysis.
* **Unsupervised Cluster Segmenter**: Unsupervised pixel clustering model.
* **Threshold Sensitivity ($\tau$)**:
  * Default setting ($0.50$): Balanced decision boundary suitable for typical daylight flood scenes.
  * Lower values ($0.30 - 0.45$): Increases detection sensitivity for turbid, muddy, or shaded water.
  * Higher values ($0.55 - 0.75$): Reduces sensitivity where bright sunlight creates intense specular reflections on dry pavement or glass.

### Step 3: Click 'Analyze Image'
Click the green **Analyze Image** button. Inference executes locally in milliseconds.

### Step 4: Review Insights & Export
Inspect the generated maps, key statistical ribbon, spatial distribution, and download your results.

---

## 📊 Reading Your Image Analysis Summary

The results dashboard provides an objective, mathematically grounded breakdown:

### A. Analysis Overview Statement
A factual sentence summarizing the exact segmentation findings, for example:
> *"The model identified flood-class regions covering 34.2% (22,412 pixels) of the uploaded image. The remaining 65.8% (43,124 pixels) were classified as non-flood."*

### B. Key Image Statistics
* **Flood Coverage (%)**: Percentage of analyzed image pixels classified as flood water.
* **Non-Flood Coverage (%)**: Percentage of pixels classified as dry terrain, structures, or vegetation (ensuring percentages sum to $100\%$).
* **Total Evaluated Pixels**: Exact matrix dimension ($65,536\text{ pixels}$ across $256 \times 256$).
* **Processing Latency**: Inference execution time in milliseconds along with throughput frame-rate (FPS).

### C. Visual Inspection & Color Legend
* **1. Original Image**: Clean uncompressed input photograph.
* **2. Binary Mask**: Crisp black-and-white segmentation mask ($0 = \text{dry}$, $1 = \text{flood}$).
* **3. Colored Overlay**: Multi-channel situational overlay:
  * 🔵 **Sky Blue (`#38bdf8`)**: Classified flood water bodies.
  * 🔴 **Red Contour (`#ef4444`)**: Detected shoreline boundary contours.
  * ⚫ **Black (in Mask)**: Non-flood / dry terrain.
  * ⚪ **White (in Mask)**: Identified flood-class pixels.

### D. Spatial Distribution (2D Frame Analysis)
A quadrant-by-quadrant breakdown displaying pixel concentrations:
* **Top-Left (NW) Quadrant**
* **Top-Right (NE) Quadrant**
* **Bottom-Left (SW) Quadrant**
* **Bottom-Right (SE) Quadrant**

> **Notice**: Spatial distribution metrics reflect 2D image coordinates (pixel rows and columns within the photograph frame), not geographic positions, ground elevations, or physical GPS coordinates.

### E. Understanding This Result (Limitations & Meaning)
* Flood coverage values represent the **proportion of photographic pixels** classified as flood water by the algorithm.
* Pixel percentages do **not** directly represent physical ground area in square meters or water depth in meters.
* The tool is designed to assist environmental analysts and drone operators as a visual screening tool, and should not be used as the sole automated trigger for critical emergency life-safety decisions.

---

## 📥 Exporting Deliverables
* **Download Mask (PNG)**: Click **PNG** on the binary mask card for GIS ingestion or custom computer vision pipelines.
* **Download Overlay (JPG)**: Click **Download / JPG** to export high-contrast situational maps.
* **Print / Save PDF Report**: Click the **Print / Save PDF Report** button to generate a clean, printer-friendly summary sheet.
* **Export Analysis Data (JSON)**: Click **Export Analysis Data (JSON)** to download structured telemetry logs containing complete quadrant breakdowns, model metadata, and pixel counts.

---

## 🕒 Session Insights History
At the bottom of the workspace, the **Analysis History & Comparison** table logs every image analyzed during your active session, enabling rapid side-by-side comparison of multiple scenes.
