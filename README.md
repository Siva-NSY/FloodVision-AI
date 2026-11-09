# FloodVision AI: Environmental Image Intelligence Platform
### Classical Machine Learning & Knowledge Distillation for Flood Area Segmentation
**Department of Computer Science & Engineering | IIT Patna**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-18794E.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Creator](https://img.shields.io/badge/Creator-Siva%20Yaswanth-18794E.svg)](https://github.com/Siva-NSY)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0A66C2.svg)](https://www.linkedin.com/in/siva-yaswanth-nallangari-155902324/)

---
<img width="1466" height="716" alt="image" src="https://github.com/user-attachments/assets/3e28610a-f45f-4c06-ba41-e8f617b30751" />
<img width="1253" height="712" alt="image" src="https://github.com/user-attachments/assets/0f373742-3913-43d3-8374-0220ce0ef96e" />


## 📌 Project Overview

**FloodVision AI** is an independent environmental image intelligence platform that converts aerial and ground-level flood photography into actionable spatial insight in milliseconds.

While contemporary deep neural networks require massive GPU resources and gigabytes of memory, this platform proves that **classical machine learning with Teacher–Student Knowledge Distillation** can compress image segmentation models by **270×** (down to **444 KB**) while operating at sub-40ms speed on standard CPUs.

### 🌟 Core Highlights
* **Flagship Distilled Student Model (`444 KB`)**: A compact 20-tree Random Forest student trained on multi-spectral features using teacher pseudo-labels. Retains **99.73%** of teacher accuracy with **46.9× inference speedup** (sub-40ms).
* **Unsupervised Cluster Segmenter (`41 KB`)**: 6-D K-Means student initialized from teacher centroids, capable of segmentation with **zero human-annotated masks**.
* **Modern Climate-Tech Web Interface**: Designed with clean editorial layouts (inspired by Stripe, Linear, and Notion) in Warm White (`#FAFBF8`) and Deep Forest Green (`#18794E`).
* **Zero Deep Learning Hardware Dependencies**: Runs entirely offline on standard laptops, embedded drone processors, and edge devices.

---

## 👨‍💻 Creator Attribution

* **Developer**: **Siva Yaswanth**
* **Institution**: Indian Institute of Technology Patna (IIT Patna)
* **Role**: Computer Science Undergraduate
* **GitHub**: [github.com/Siva-NSY](https://github.com/Siva-NSY)
* **LinkedIn**: [linkedin.com/in/siva-yaswanth-nallangari-155902324](https://www.linkedin.com/in/siva-yaswanth-nallangari-155902324/)

---

## 🚀 Quick Start: Run the Web Platform

### Option A: All-in-One Flask Application (Recommended)
The full web experience runs with a single command:

```bash
# 1. Clone the repository
git clone https://github.com/Siva-NSY/FloodVision-AI.git
cd FloodVision-AI

# 2. Install lightweight dependencies
pip install -r requirements.txt

# 3. Launch the platform
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser. The pre-trained student models are already included in the repository, so the app is immediately operational with zero downloads!

### Option B: Decoupled Enterprise Stack (FastAPI + Vite React)
For microservice production deployment:

```bash
# Terminal 1: FastAPI Backend
cd FloodVision-AI/backend
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Vite React Frontend
cd FloodVision-AI/frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 📁 Repository Structure

```
FloodVision-AI/
├── app.py                         # Standalone Flask application (Port 5000)
├── templates/
│   └── index.html                 # Modern Stripe/Linear climate-tech UI
├── static/
│   └── samples/                   # Pre-calibrated 1-click benchmark test scenes
├── results/
│   ├── figures/                   # Quantitative plots, elbow curves & diagrams
│   ├── metrics/                   # CSV tables & evaluation telemetry
│   └── models/
│       ├── distilled_rf_student.pkl  # Flagship Student Model (444 KB) [INCLUDED]
│       └── distilled_km_student.pkl  # Unsupervised Student (41 KB)  [INCLUDED]
├── src/                           # Complete ML pipeline source code
│   ├── data_preprocessing.py     # Bilinear resizing, binarisation, seed-42 split
│   ├── feature_extraction.py     # 18-D teacher & 6-D student feature pipelines
│   ├── supervised_models.py      # Random Forest, KNN, Naive Bayes baselines
│   ├── distillation.py           # 9-pair distillation with confidence thresholding
│   ├── unsupervised_models.py    # K-Means clustering & centroid transfer
│   └── evaluation.py             # IoU, F1 score, agreement, and efficiency Z
├── notebooks/
│   └── CS3103_ML_Project.ipynb   # Complete reproducible Jupyter Notebook
├── FloodVision-AI/                # Decoupled FastAPI + Vite React enterprise package
│   ├── backend/                   # FastAPI REST API endpoints
│   ├── frontend/                  # Vite + React 18 component architecture
│   └── docs/                      # Technical architecture documentation
├── presentation/                  # Slide deck (PPTX)
├── report/                        # Academic technical report (PDF & LaTeX)
├── .gitignore                     # Git filter for large files & raw datasets
├── APP_RUN_GUIDE.txt              # In-depth operational handbook
└── requirements.txt               # Python package dependencies
```

---


## 📦 Dataset Notice & Model Size

* **Pre-trained Models**: Both the **Distilled RF Student (`444 KB`)** and **Distilled K-Means Student (`41 KB`)** are tracked directly in this repository so anyone can run inference out of the box.
* **Teacher Model Ensemble (`rf_teacher.pkl`, 224 MB)**: The 200-tree teacher ensemble exceeds GitHub's 100 MB single-file push limit and is excluded via `.gitignore`. If needed, it can be re-trained locally in 2 minutes by running `python build_notebook.py`.
* **Full Dataset**: Available on Kaggle: [Flood Area Segmentation Dataset](https://www.kaggle.com/datasets/faizalkarim/flood-area-segmentation) (290 aerial & street flood images paired with binary masks).
