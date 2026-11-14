"""
Script to build the official CS3103_ML_Project.ipynb Jupyter Notebook
CS3103 Machine Learning Project - IIT Patna
"""

import nbformat as nbf

nb = nbf.v4.new_notebook()

nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.14.4"
    }
}

cells = []

# Title & Abstract Cell
cells.append(nbf.v4.new_markdown_cell("""# IIT Patna - CS3103: Machine Learning Project
## Project Title: Flood Area Segmentation with Teacher–Student Learning
**Course**: CS3103 Machine Learning  
**Roll Number**: 2401CS74  
**Author**: B.Tech Computer Science & Engineering, IIT Patna  
**Dataset**: Kaggle Flood Area Segmentation (290 samples)  
**Strict Classical ML Protocol**: Random Seed = 42, No Deep Learning, No External Data, Zero Data Leakage.

---

### Abstract
This project implements, evaluates, and analyzes classical machine learning pipelines for binary flood area segmentation using teacher–student knowledge distillation. Two parallel tracks are developed:
1. **Supervised Teacher–Student Learning (Track S)**: High-capacity teachers (KNN, Random Forest, Gaussian Naive Bayes) operating on 18-dimensional rich features ($\\phi_T$) distill into budget-compliant compact students (6-dimensional features, $\\phi_S$) via confident pseudo-labeling over $L \\cup U$ (203 images) with threshold $\\tau$-filtering and soft-label weighted duplication.
2. **Unsupervised Teacher–Student Learning (Track U)**: An 18-D K-Means teacher ($K_T=9$) discovered via inertia elbow analysis distills cluster centroid knowledge into compact 6-D students ($K_S=2$) across four architectural variants (with/without Lloyd refinement $\\times$ inherited vs. re-estimated mapping).

Every model is evaluated on all 3,801,088 pixels across the 58 test images. Compression ratios up to $270\\times$ and inference speedups up to $47\\times$ are demonstrated while retaining $>99\\%$ of teacher IoU.
"""))

# Cell 1: Environment & Setup
cells.append(nbf.v4.new_markdown_cell("""## 1. Setup, Environment & Imports
We import all approved classical machine learning libraries, set random seeds, and configure reproducible paths.
"""))

cells.append(nbf.v4.new_code_cell("""import os
import sys

# Auto-heal: If running in Google Colab without unzipping, auto-extract colab_files.zip or fetch from GitHub
if not os.path.exists("src"):
    if os.path.exists("colab_files.zip"):
        print("Auto-extracting colab_files.zip...")
        import zipfile
        with zipfile.ZipFile("colab_files.zip", "r") as z:
            z.extractall(".")
    elif os.path.exists("/content/colab_files.zip"):
        print("Auto-extracting /content/colab_files.zip...")
        import zipfile
        with zipfile.ZipFile("/content/colab_files.zip", "r") as z:
            z.extractall("/content")
    else:
        print("Auto-cloning src and results from GitHub...")
        os.system("git clone https://github.com/Siva-NSY/FloodVision-AI.git repo && cp -rn repo/src repo/results repo/flood-area-segmentation . && rm -rf repo")

import time
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cv2
import sklearn

# Ensure working directory is set to project root
if os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")
print(f"Working Directory: {os.getcwd()}")

# Add root directory to path
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("src"))

from src.data_preprocessing import (
    get_dataset_splits,
    load_and_preprocess_image,
    load_and_preprocess_mask,
    compute_split_statistics
)
from src.feature_extraction import (
    extract_teacher_features,
    extract_student_features,
    benchmark_feature_extraction,
    get_feature_comparison_table
)
from src.evaluation import (
    compute_pixel_metrics,
    compute_agreement,
    compute_retention,
    compute_efficiency_score
)

RANDOM_SEED = 42
print(f"NumPy Version: {np.__version__}")
print(f"Scikit-Learn Version: {sklearn.__version__}")
print(f"OpenCV Version: {cv2.__version__}")
print("Random State initialized to 42.")
"""))

# Part A: Data Pipeline & Features
cells.append(nbf.v4.new_markdown_cell("""## Part A: Data Pipeline and Feature Design [10 Marks]
### A.1 Dataset Splitting & Preprocessing
In accordance with the assignment specification (Page 2):
- Images resized to $256 \\times 256$ (bilinear interpolation).
- Masks binarised ($y=1$ if pixel $\\ge 128$, else $0$) and resized to $256 \\times 256$ using nearest-neighbour interpolation.
- Fixed Split ($L=40, U=163, \\text{Val}=29, \\text{Test}=58$). Unlabelled $U$ masks are strictly never loaded.
"""))

cells.append(nbf.v4.new_code_cell("""# Load splits and verify counts
splits = get_dataset_splits("flood-area-segmentation")
print("Verified Split Partition Sizes:")
for k, v in splits.items():
    if k != "data_dir":
        print(f"  {k.upper()}: {len(v)} images")

df_stats = compute_split_statistics(splits)
print("\\nDataset Class Distribution Statistics:")
display(df_stats)
"""))

cells.append(nbf.v4.new_markdown_cell("""### A.2 Feature Engineering & Extraction Cost Profiling
Two hand-crafted feature sets are extracted:
1. **Rich Teacher Features ($\\phi_T$, $d_T = 18$ dims $\\ge 12$)**:
   - RGB (3 dims)
   - HSV (3 dims: Hue, Saturation, Value)
   - CIE-Lab (3 dims: Lightness, $a^*$, $b^*$)
   - Neighborhood Gaussian Blurred RGB ($\\sigma=2.0$) (3 dims)
   - Local Texture Statistics ($7 \\times 7$ window mean & std on $L^*$) (2 dims)
   - Edge responses (Sobel gradient magnitude, Laplacian) (2 dims)
   - Spatial Coordinates (normalized row $y/H$, col $x/W$) (2 dims)
2. **Compact Student Features ($\\phi_S$, $d_S = 6$ dims $\\le 6$ and $\\le d_T/2$)**:
   - Computed directly from the image without PCA projections:
   - RGB (3 dims)
   - Hue & Saturation (2 dims)
   - Normalized Vertical Position ($y/H$) (1 dim)
"""))

cells.append(nbf.v4.new_code_cell("""# Display feature specifications and justifications
df_feats = get_feature_comparison_table()
display(df_feats)

# Benchmark extraction time per image
bench = benchmark_feature_extraction(num_images=40)
print("\\nFeature Extraction Benchmark:")
for k, v in bench.items():
    print(f"  {k}: {v}")
"""))

cells.append(nbf.v4.new_markdown_cell("""### A.3 Pipeline Architecture Diagram & Visual Preprocessing
"""))

cells.append(nbf.v4.new_code_cell("""# Display Pipeline Diagram and Preprocessing Samples
fig_diag = plt.imread("results/graphs/pipeline_diagram.png")
plt.figure(figsize=(14, 7), dpi=150)
plt.imshow(fig_diag)
plt.axis('off')
plt.title("Figure 1: Complete Classical ML Teacher-Student Architecture Pipeline", fontsize=12, fontweight='bold')
plt.show()

fig_pre = plt.imread("results/graphs/preprocessing_samples.png")
plt.figure(figsize=(12, 10), dpi=150)
plt.imshow(fig_pre)
plt.axis('off')
plt.title("Preprocessing Visual Samples: RGB Image, Binary Mask, and Flood Overlay", fontsize=12, fontweight='bold')
plt.show()
"""))

# Part B: Supervised Learning
cells.append(nbf.v4.new_markdown_cell("""## Part B: Supervised Teacher–Student Learning [30 Marks]
### B.1 Supervised Teachers & B.2 No-Teacher Baselines
We train:
- **Teachers on $\\phi_T$ (18 dims)**:
  - KNN-T: $\\ge 20,000$ reference pixels (25,000 pixels used, $k=7$) + StandardScaler
  - RF-T: $\\ge 200$ trees, unrestricted depth
  - GNB-T: Gaussian Naive Bayes with variance smoothing
- **No-Teacher Baselines on $\\phi_S$ (6 dims)**:
  - KNN-S: $\\le 5,000$ reference pixels (5,000 pixels used, $k=7$) + StandardScaler
  - RF-S: $\\le 20$ trees, max depth $\\le 8$
  - GNB-S: Gaussian Naive Bayes on $\\phi_S$
"""))

cells.append(nbf.v4.new_code_cell("""# Load and display Teachers and Baselines Evaluation Summary
df_b12 = pd.read_csv("results/tables/b12_teachers_baselines.csv")
display(df_b12)
"""))

cells.append(nbf.v4.new_markdown_cell("""### B.3 Hard-Label Distillation: All 9 Combinations & $\\tau$ Study
Every teacher distills into every student type over $L \\cup U$ (203 transfer images).
Confidence filter threshold $\\tau \\in \\{0.5, 0.6, 0.7, 0.8, 0.9, 0.95\\}$ is tuned on the 29 validation images.
"""))

cells.append(nbf.v4.new_code_cell("""# Load and display Complete 3x3 Test IoU & F1 Distillation Matrix
df_matrix = pd.read_csv("results/tables/3x3_distillation_matrix.csv")
print("Complete 3x3 Distillation Results Matrix (Test IoU & F1):")
display(df_matrix)
"""))

cells.append(nbf.v4.new_code_cell("""# Display Confidence Threshold (tau) Study Curve
fig_tau = plt.imread("results/graphs/tau_confidence_study.png")
plt.figure(figsize=(10, 6), dpi=150)
plt.imshow(fig_tau)
plt.axis('off')
plt.title("Figure 2: Confidence Filter Threshold (tau) Study & Retained Pixels", fontsize=12, fontweight='bold')
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("""### B.4 Soft-Label Distillation Comparison
For the best performing pair (KNN-T $\\to$ RF-S and RF-T $\\to$ RF-S), we compare hard distillation against soft-label distillation using weighted duplication.
"""))

cells.append(nbf.v4.new_code_cell("""# Display Soft Distillation Comparison
df_soft = pd.read_csv("results/tables/soft_distillation_comparison.csv")
display(df_soft)
"""))

cells.append(nbf.v4.new_markdown_cell("""### B.5 Detailed Analysis Questions (a)–(e)
**Answer (a) Which teacher produced the best students?**  
KNN-T and RF-T produced the top-performing students (Test IoU: 60.77% and 59.67%). RF-T was the most accurate teacher (Test IoU 64.26%), while KNN-T produced the student with the highest single IoU (60.77%).  
*GNB Over-confidence*: GNB multiplies probabilities across 18 correlated channels, pushing posterior probabilities to extreme saturated values near 0 or 1. Even at $\\tau=0.95$, GNB retains $>83\\%$ of pixels, failing to filter out noisy boundary pixels and causing lower student quality.

**Answer (b) Which student absorbs teacher knowledge best?**  
The **Random Forest Student (RF-S)** absorbs knowledge best, achieving $60.77\\%$ IoU. Its non-linear decision tree ensemble flexibly partitions the compact 6-D feature space, unlike linear/probabilistic boundaries.

**Answer (c) Distillation Gain & Role of $U$**:  
Distillation significantly outperforms no-teacher baselines:
- KNN-S gained **$+7.87\\%$ IoU** ($51.80\\% \\to 59.67\\%$) from RF-T.
- RF-S gained **$+2.15\\%$ IoU** ($58.62\\% \\to 60.77\\%$) from KNN-T.  
The 163 unlabelled images ($U$) provide over 10 million pixels of diverse real-world scenes, expanding the training manifold beyond the limited 40 images in $L$.

**Answer (d) Did any student match or exceed its teacher?**  
The distilled RF-S student reached $60.77\\%$ IoU, virtually matching its KNN-T teacher ($60.94\\%$ IoU, $99.72\\%$ retention). Distillation regularizes noisy hand-drawn boundary annotations into smooth probabilistic teacher surfaces, preventing student overfitting.

**Answer (e) Compression and Speedup**:  
For the best RF-S student:
- Retention $\\rho = 99.73\\%$
- Compression Ratio $CR = 269.76\\times$ (RF-T 196 MB vs RF-S 0.73 MB)
- Speed-up $SU = 46.93\\times$ (KNN-T 1866 ms vs RF-S 39.77 ms)
"""))

# Part C: Unsupervised Learning
cells.append(nbf.v4.new_markdown_cell("""## Part C: Unsupervised Teacher–Student Learning with K-Means [20 Marks]
### C.1 K-Means Teacher ($K_T \\ge 6$) & Cluster Selection Study
Cluster count $K_T$ is selected via inertia elbow analysis and confirmed on validation IoU.
"""))

cells.append(nbf.v4.new_code_cell("""# Display K-Selection Study Table
df_elbow = pd.read_csv("results/tables/kmeans_elbow_study.csv")
display(df_elbow)

# Display Elbow Curve
fig_elbow = plt.imread("results/graphs/kmeans_elbow_curve.png")
plt.figure(figsize=(10, 6), dpi=150)
plt.imshow(fig_elbow)
plt.axis('off')
plt.title("Figure 3: K-Means Teacher Cluster Selection: Inertia Elbow & Validation IoU", fontsize=12, fontweight='bold')
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("""### C.2 & C.3 Distilled K-Means 4 Variants Table
- Variant 1: Without Lloyd refinement + Inherited mapping $\\pi_S$
- Variant 2: With Lloyd refinement + Inherited mapping $\\pi_S$
- Variant 3: Without Lloyd refinement + Re-estimated mapping from $L$
- Variant 4: With Lloyd refinement + Re-estimated mapping from $L$
"""))

cells.append(nbf.v4.new_code_cell("""# Display 4 Variants Table
df_var = pd.read_csv("results/tables/kmeans_4_variants.csv")
display(df_var)
"""))

cells.append(nbf.v4.new_markdown_cell("""### C.4 Analysis: Lloyd Refinement Drift & Scene Element Confusions
1. **Refinement Drift**:
   - Without Lloyd refinement (Variant 1), the student maintains **84.86% agreement** with the teacher, achieving **53.34% Test IoU** and beating the teacher (Retention $\\rho = 107.98\\%$).
   - When Lloyd refinement is applied (Variant 2), agreement drops severely to **61.63%**, and Test IoU drops to **50.07%**.
   - *Cause*: Unsupervised Lloyd refinement optimizes purely geometric inertia in 6-D space, pulling centroids toward dominant dark asphalt roads and shadow clusters rather than semantic water boundaries.
2. **Confusions**:
   - Asphalt roads and wet mud: Identical low saturation and neutral hue.
   - Sky reflections: Mirror water reflections exhibit high lightness $L^*$, confusing naive colour models unless vertical coordinate $y/H$ is present.
"""))

# Part D: Comparison & Deliverables
cells.append(nbf.v4.new_markdown_cell("""## Part D: Supervised vs. Unsupervised Comparison and Efficiency [20 Marks]
### D.1 Summary Table & Efficiency Score $Z$
$$Z = 0.6 \\times \\text{F1}_{S, \\%} + 0.4 \\times \\text{IoU}_{S, \\%}$$
"""))

cells.append(nbf.v4.new_code_cell("""df_part_d = pd.read_csv("results/tables/part_d_summary.csv")
display(df_part_d)
"""))

cells.append(nbf.v4.new_markdown_cell("""### D.2 Qualitative Visual Comparisons (6-Panel Figure)
Comparison across 4 test images:
1. Original RGB Photograph
2. Ground Truth Binary Mask
3. Best Supervised Teacher (RF-T)
4. Best Supervised Student (Distilled RF-S)
5. Unsupervised Teacher (KM-T, $K_T=9$)
6. Best Unsupervised Student (Distilled KM-S_V1)
"""))

cells.append(nbf.v4.new_code_cell("""fig_qual = plt.imread("results/graphs/qualitative_comparisons.png")
plt.figure(figsize=(18, 12), dpi=150)
plt.imshow(fig_qual)
plt.axis('off')
plt.title("Figure 4: Qualitative Segmentation Comparison Across 4 Diverse Test Scenes", fontsize=14, fontweight='bold')
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("""### D.3 Technical Verdict: Supervised vs. Unsupervised
1. **Accuracy**: Supervised distillation ($Z=69.67\\%$, IoU $60.77\\%$) decisively outperforms unsupervised distillation ($Z=63.08\\%$, IoU $53.34\\%$).
2. **Annotation Efficiency**: Unsupervised K-Means requires zero ground truth for cluster discovery, utilizing labels only for cluster-to-class assignment.
3. **Deployment**: The distilled RF-S model offers the ideal balance for real-time edge devices (drones/smartphones), requiring only 0.73 MB memory and 39.77 ms per image while maintaining $99.7\\%$ teacher accuracy.
"""))

nb.cells = cells

with open("notebooks/CS3103_ML_Project.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Saved notebooks/CS3103_ML_Project.ipynb successfully!")
