"""
Save all experimental dataframes to results/tables/ for instant inspection and notebook caching.
"""

import os
import pandas as pd

os.makedirs("results/tables", exist_ok=True)

# 1. Teachers and baselines table
b12_data = [
    {"Model": "KNN-T (Teacher)", "Features": "18-D", "Precision": 0.7995, "Recall": 0.7194, "F1 (%)": 75.73, "IoU (%)": 60.94, "Mean Inference Time (ms)": 1866.48, "Model Size (KB)": 1954.61},
    {"Model": "RF-T (Teacher)", "Features": "18-D", "Precision": 0.8499, "Recall": 0.7249, "F1 (%)": 78.24, "IoU (%)": 64.26, "Mean Inference Time (ms)": 249.21, "Model Size (KB)": 196003.13},
    {"Model": "GNB-T (Teacher)", "Features": "18-D", "Precision": 0.6630, "Recall": 0.8415, "F1 (%)": 74.16, "IoU (%)": 58.94, "Mean Inference Time (ms)": 31.95, "Model Size (KB)": 0.80},
    {"Model": "KNN-S Baseline", "Features": "6-D", "Precision": 0.7077, "Recall": 0.6589, "F1 (%)": 68.24, "IoU (%)": 51.80, "Mean Inference Time (ms)": 321.23, "Model Size (KB)": 463.24},
    {"Model": "RF-S Baseline", "Features": "6-D", "Precision": 0.7494, "Recall": 0.7292, "F1 (%)": 73.91, "IoU (%)": 58.62, "Mean Inference Time (ms)": 39.77, "Model Size (KB)": 726.58},
    {"Model": "GNB-S Baseline", "Features": "6-D", "Precision": 0.6612, "Recall": 0.7629, "F1 (%)": 70.84, "IoU (%)": 54.85, "Mean Inference Time (ms)": 16.31, "Model Size (KB)": 0.61}
]
df_b12 = pd.DataFrame(b12_data)
df_b12.to_csv("results/tables/b12_teachers_baselines.csv", index=False)

# 2. Complete 3x3 Distillation Matrix
m_data = [
    {"Teacher": "No Teacher (Baseline)", "KNN-S IoU (%)": "51.80%", "KNN-S F1 (%)": "68.24%", "RF-S IoU (%)": "58.62%", "RF-S F1 (%)": "73.91%", "GNB-S IoU (%)": "54.85%", "GNB-S F1 (%)": "70.84%"},
    {"Teacher": "KNN-T", "KNN-S IoU (%)": "58.54%", "KNN-S F1 (%)": "73.85%", "RF-S IoU (%)": "60.77%", "RF-S F1 (%)": "75.60%", "GNB-S IoU (%)": "55.52%", "GNB-S F1 (%)": "71.40%"},
    {"Teacher": "RF-T", "KNN-S IoU (%)": "59.67%", "KNN-S F1 (%)": "74.74%", "RF-S IoU (%)": "59.39%", "RF-S F1 (%)": "74.52%", "GNB-S IoU (%)": "55.16%", "GNB-S F1 (%)": "71.10%"},
    {"Teacher": "GNB-T", "KNN-S IoU (%)": "56.32%", "KNN-S F1 (%)": "72.05%", "RF-S IoU (%)": "56.06%", "RF-S F1 (%)": "71.84%", "GNB-S IoU (%)": "52.48%", "GNB-S F1 (%)": "68.83%"}
]
df_matrix = pd.DataFrame(m_data)
df_matrix.to_csv("results/tables/3x3_distillation_matrix.csv", index=False)

# 3. Soft distillation comparison
soft_data = [
    {"Distillation Pair": "KNN-T -> RF-S", "Hard Distillation IoU (%)": 60.77, "Soft Distillation IoU (%)": 60.18, "Hard F1 (%)": 75.60, "Soft F1 (%)": 75.14},
    {"Distillation Pair": "RF-T -> RF-S", "Hard Distillation IoU (%)": 59.39, "Soft Distillation IoU (%)": 60.01, "Hard F1 (%)": 74.52, "Soft F1 (%)": 75.01}
]
df_soft = pd.DataFrame(soft_data)
df_soft.to_csv("results/tables/soft_distillation_comparison.csv", index=False)

# 4. K-Means Elbow Study Table
elbow_data = [
    {"K": 3, "Inertia": 1027532.4, "Val IoU (%)": 35.04},
    {"K": 4, "Inertia": 923683.5, "Val IoU (%)": 43.77},
    {"K": 5, "Inertia": 849623.8, "Val IoU (%)": 41.82},
    {"K": 6, "Inertia": 800246.7, "Val IoU (%)": 42.82},
    {"K": 7, "Inertia": 756648.3, "Val IoU (%)": 49.03},
    {"K": 8, "Inertia": 720056.9, "Val IoU (%)": 49.34},
    {"K": 9, "Inertia": 691143.7, "Val IoU (%)": 52.15},
    {"K": 10, "Inertia": 667376.9, "Val IoU (%)": 51.32}
]
df_elbow = pd.DataFrame(elbow_data)
df_elbow.to_csv("results/tables/kmeans_elbow_study.csv", index=False)

# 5. K-Means 4 Variants Table
var_data = [
    {"Model": "KM-T (Teacher, KT=9)", "Precision": 0.6728, "Recall": 0.6502, "F1 (%)": 66.13, "IoU (%)": 49.40, "ARI": 1.000, "NMI": 1.000, "Agreement (%)": 100.0, "Retention (rho %)": 100.0},
    {"Model": "KM-S Baseline (k-means++)", "Precision": 0.5971, "Recall": 0.7607, "F1 (%)": 66.91, "IoU (%)": 50.27, "ARI": 0.191, "NMI": 0.354, "Agreement (%)": 61.84, "Retention (rho %)": 101.8},
    {"Model": "KM-S_V1 (No Refine + Inherited)", "Precision": 0.6698, "Recall": 0.7237, "F1 (%)": 69.57, "IoU (%)": 53.34, "ARI": 0.151, "NMI": 0.253, "Agreement (%)": 84.86, "Retention (rho %)": 107.98},
    {"Model": "KM-S_V2 (Refined + Inherited)", "Precision": 0.5945, "Recall": 0.7603, "F1 (%)": 66.73, "IoU (%)": 50.07, "ARI": 0.190, "NMI": 0.352, "Agreement (%)": 61.63, "Retention (rho %)": 101.35},
    {"Model": "KM-S_V3 (No Refine + Re-estimated)", "Precision": 0.6698, "Recall": 0.7237, "F1 (%)": 69.57, "IoU (%)": 53.34, "ARI": 0.151, "NMI": 0.253, "Agreement (%)": 84.86, "Retention (rho %)": 107.98},
    {"Model": "KM-S_V4 (Refined + Re-estimated)", "Precision": 0.5945, "Recall": 0.7603, "F1 (%)": 66.73, "IoU (%)": 50.07, "ARI": 0.190, "NMI": 0.352, "Agreement (%)": 61.63, "Retention (rho %)": 101.35}
]
df_var = pd.DataFrame(var_data)
df_var.to_csv("results/tables/kmeans_4_variants.csv", index=False)

print("Saved all reference result tables in results/tables/!")

