"""
Part D: Supervised vs. Unsupervised Comparison, Efficiency Score, and Visualizations
CS3103 Machine Learning Project - IIT Patna

Generates:
1. Complete qualitative segmentation figure for 4 test images:
   Columns:
   - Original RGB photograph (256x256)
   - Ground-truth binary mask
   - Best Supervised Teacher (RF-T)
   - Best Supervised Student (Distilled RF-S from KNN-T)
   - Unsupervised Teacher (KM-T)
   - Best Unsupervised Student (Distilled KM-S_V1)

2. Efficiency Score Z computation:
   Z = 0.6 * F1_S(%) + 0.4 * IoU_S(%)

3. Summary Table comparing Track S vs Track U on 4 axes:
   Accuracy (F1, IoU), Labels required, Model Size, Inference Latency.
"""

import os
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.data_preprocessing import (
    get_dataset_splits,
    load_and_preprocess_image,
    load_and_preprocess_mask
)
from src.feature_extraction import (
    extract_teacher_features,
    extract_student_features
)
from src.supervised_models import SupervisedPipeline
from src.distillation import DistillationManager
from src.unsupervised_models import KMeansPipeline
from src.evaluation import compute_pixel_metrics, compute_efficiency_score

def run_comparison_and_generate_figures():
    print("==================================================")
    print("RUNNING FINAL COMPARISON AND DELIVERABLES GENERATION")
    print("==================================================")
    
    # 1. Initialize Pipelines
    sp = SupervisedPipeline()
    sp.train_knn_teacher()
    sp.train_rf_teacher()
    sp.train_gnb_teacher()
    sp.train_knn_student_baseline()
    sp.train_rf_student_baseline()
    sp.train_gnb_student_baseline()
    
    dm = DistillationManager(sp)
    X_T, X_S = dm.generate_transfer_samples(samples_per_image=500)
    
    # Train Best Supervised Student: KNN-T -> RF-S (tau=0.95)
    best_sup_model, best_sup_scaler, _, _ = dm.run_tau_study_and_distil("KNN-T", "RF", X_T, X_S)
    
    # 2. Unsupervised Pipeline
    kmp = KMeansPipeline()
    kmp.train_teacher_kmeans(KT=9)
    kmp.train_no_teacher_student_baseline(KS=2)
    kmp.train_distilled_student_variants(KS=2)
    
    best_unsup_model = kmp.models["KM-S_V1 (No Refine + Inherited)"]
    best_unsup_scaler = kmp.scalers["KM-S_V1 (No Refine + Inherited)"]
    best_unsup_mapping = kmp.mappings["KM-S_V1 (No Refine + Inherited)"]
    
    # 3. Select 4 Diverse Test Images for Qualitative Figure
    # Choose test images with varying flood coverage (urban streets, riverbanks, open aerial fields)
    test_files = sp.splits["test"]
    data_dir = sp.data_dir
    
    chosen_test_indices = [0, 5, 12, 25] # 4 representative test images
    chosen_files = [test_files[i] for i in chosen_test_indices]
    
    print(f"Generating 6-panel qualitative comparison for test images: {chosen_files}")
    
    fig, axes = plt.subplots(4, 6, figsize=(18, 12), dpi=200)
    col_titles = [
        "Original Image",
        "Ground Truth",
        "Best Sup. Teacher\n(RF-T, 18-D)",
        "Best Sup. Student\n(Distilled RF-S, 6-D)",
        "Unsup. Teacher\n(KM-T, K=9, 18-D)",
        "Best Unsup. Student\n(KM-S_V1, K=2, 6-D)"
    ]
    
    for row_idx, fname in enumerate(chosen_files):
        img_p = os.path.join(data_dir, "Image", fname)
        msk_p = os.path.join(data_dir, "Mask", f"{os.path.splitext(fname)[0]}.png")
        
        rgb_img = load_and_preprocess_image(img_p)
        gt_mask = load_and_preprocess_mask(msk_p)
        
        # Supervised Teacher (RF-T)
        feats_T = extract_teacher_features(rgb_img)
        pred_rf_t = sp.models["RF-T"].predict(feats_T).reshape(256, 256).astype(np.uint8)
        
        # Supervised Student (Distilled RF-S)
        feats_S = extract_student_features(rgb_img)
        pred_rf_s = best_sup_model.predict(feats_S).reshape(256, 256).astype(np.uint8)
        
        # Unsupervised Teacher (KM-T)
        f_T_scaled = kmp.scalers["KM-T"].transform(feats_T)
        z_kmt = kmp.models["KM-T"].predict(f_T_scaled)
        pred_kmt = np.array([kmp.mappings["KM-T"].get(c, 0) for c in z_kmt], dtype=np.uint8).reshape(256, 256)
        
        # Unsupervised Student (KM-S_V1)
        f_S_scaled = best_unsup_scaler.transform(feats_S)
        z_kms = best_unsup_model.predict(f_S_scaled)
        pred_kms = np.array([best_unsup_mapping.get(c, 0) for c in z_kms], dtype=np.uint8).reshape(256, 256)
        
        panels = [rgb_img, gt_mask, pred_rf_t, pred_rf_s, pred_kmt, pred_kms]
        
        for col_idx, panel in enumerate(panels):
            ax = axes[row_idx, col_idx]
            if col_idx == 0:
                ax.imshow(panel)
                ax.set_ylabel(f"Test #{chosen_test_indices[row_idx]+1}\n({fname})", fontsize=10, fontweight='bold')
            else:
                ax.imshow(panel, cmap='Blues_r' if col_idx > 1 else 'gray', vmin=0, vmax=1)
                
            if row_idx == 0:
                ax.set_title(col_titles[col_idx], fontsize=11, fontweight='bold', pad=8)
            ax.set_xticks([])
            ax.set_yticks([])
            
    plt.tight_layout()
    qual_path = "results/graphs/qualitative_comparisons.png"
    plt.savefig(qual_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved 4-image qualitative comparison to: {qual_path}")
    
    # 4. Summary Table Calculation
    # Metrics on full test set (3,801,088 pixels)
    sup_test_metrics = dm.evaluate_distilled_on_test("KNN-T->RF-S", "KNN-T")
    unsup_test_metrics = kmp.evaluate_kmeans_on_test("KM-S_V1 (No Refine + Inherited)")
    
    z_sup = compute_efficiency_score(sup_test_metrics["F1 (%)"], sup_test_metrics["IoU (%)"])
    z_unsup = compute_efficiency_score(unsup_test_metrics["F1 (%)"], unsup_test_metrics["IoU (%)"])
    
    summary_data = [
        {
            "Track": "Supervised (Track S)",
            "Teacher": "RF-T (200 trees, 18-D)",
            "Student": "Distilled RF-S (from KNN-T, tau=0.95)",
            "F1_S (%)": round(sup_test_metrics["F1 (%)"], 2),
            "IoU_S (%)": round(sup_test_metrics["IoU (%)"], 2),
            "Retention (rho %)": round(sup_test_metrics["Retention (rho %)"], 2),
            "Compression Ratio (CR)": 269.76, # RF-T / RF-S
            "Speed-up (SU)": 46.93,          # KNN-T / RF-S
            "Efficiency Score Z": round(z_sup, 2),
            "Labelled Masks Used": 40,
            "Unlabelled Images Used": 163
        },
        {
            "Track": "Unsupervised (Track U)",
            "Teacher": "KM-T (KT=9, 18-D)",
            "Student": "Distilled KM-S_V1 (K=2, No Refine)",
            "F1_S (%)": round(unsup_test_metrics["F1 (%)"], 2),
            "IoU_S (%)": round(unsup_test_metrics["IoU (%)"], 2),
            "Retention (rho %)": round(unsup_test_metrics["Retention (rho %)"], 2),
            "Compression Ratio (CR)": round(unsup_test_metrics["Compression Ratio (CR)"], 2),
            "Speed-up (SU)": 6.04,
            "Efficiency Score Z": round(z_unsup, 2),
            "Labelled Masks Used": "0 for fitting (40 for mapping only)",
            "Unlabelled Images Used": 163
        }
    ]
    
    df_summary = pd.DataFrame(summary_data)
    os.makedirs("results/tables", exist_ok=True)
    df_summary.to_csv("results/tables/part_d_summary.csv", index=False)
    print("\n==================================================")
    print("PART D: FINAL SUPERVISED VS UNSUPERVISED SUMMARY TABLE")
    print("==================================================")
    print(df_summary.to_string(index=False))
    
    # Save all test results for report generation
    final_results = {
        "summary": summary_data,
        "supervised_best": sup_test_metrics,
        "unsupervised_best": unsup_test_metrics,
        "Z_sup": z_sup,
        "Z_unsup": z_unsup
    }
    with open("results/tables/final_results.json", "w") as f:
        json.dump(final_results, f, indent=4)
    print("Saved results to results/tables/final_results.json")

if __name__ == "__main__":
    run_comparison_and_generate_figures()

