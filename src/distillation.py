"""
Knowledge Distillation Module for Supervised Learning (Track S)
CS3103 Machine Learning Project - IIT Patna

Implements:
1. Hard-Label Distillation across all 9 teacher-student combinations:
   - KNN-T -> KNN-S, RF-S, GNB-S
   - RF-T  -> KNN-S, RF-S, GNB-S
   - GNB-T -> KNN-S, RF-S, GNB-S
   Using transfer set D = L U U (203 images, strictly images only, no masks for U).
   Pseudo-labeling: q_p = P_T(y=1|phi_T), y_hat = I[q_p >= 0.5], c_p = max(q_p, 1 - q_p)
   Confidence filter: keep c_p >= tau, with tau in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95].
   Hyperparameter tuning on validation set (29 images).

2. Soft-Label Distillation for the best performing pair:
   - Weighted duplication for RF/GNB (each pixel added as (x, 1) w=q and (x, 0) w=1-q)
   - Regression for KNN (KNeighborsRegressor on q_p, thresholded at 0.5)

3. Metrics & Outputs:
   - Complete 3x3 test IoU matrix
   - Test F1 scores and Teacher-Student Agreement A
   - Distillation gain (Delta IoU, Delta F1) over no-teacher baselines
   - Validation IoU vs tau curve and % retained pixels plot
"""

import os
import time
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional

from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

from src.data_preprocessing import (
    get_dataset_splits,
    load_and_preprocess_image,
    load_and_preprocess_mask
)
from src.feature_extraction import (
    extract_teacher_features,
    extract_student_features
)
from src.evaluation import (
    compute_pixel_metrics,
    compute_agreement,
    compute_retention,
    get_model_size_bytes
)

RANDOM_SEED = 42
TAU_VALUES = [0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

class DistillationManager:
    def __init__(self, supervised_pipeline):
        self.sp = supervised_pipeline
        self.splits = supervised_pipeline.splits
        self.data_dir = self.splits["data_dir"]
        self.transfer_images = self.splits["lab"] + self.splits["unl"] # 203 images
        
        self.distilled_models: Dict[str, Any] = {}
        self.distilled_scalers: Dict[str, Any] = {}
        self.tuning_history: Dict[str, Dict[float, Dict[str, float]]] = {}

    def generate_transfer_samples(
        self,
        samples_per_image: int = 500
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract paired teacher features (phi_T, 18 dims) and student features (phi_S, 6 dims)
        from 203 transfer images of L U U without looking at ground-truth masks.
        """
        print(f"Generating transfer samples from {len(self.transfer_images)} images ({samples_per_image} px/img)...")
        rng = np.random.default_rng(RANDOM_SEED)
        all_X_T = []
        all_X_S = []
        
        for fname in self.transfer_images:
            img_path = os.path.join(self.data_dir, "Image", fname)
            rgb_img = load_and_preprocess_image(img_path)
            
            feats_T = extract_teacher_features(rgb_img) # (65536, 18)
            feats_S = extract_student_features(rgb_img) # (65536, 6)
            
            n_pixels = feats_T.shape[0]
            chosen_idx = rng.choice(n_pixels, size=min(samples_per_image, n_pixels), replace=False)
            all_X_T.append(feats_T[chosen_idx])
            all_X_S.append(feats_S[chosen_idx])
            
        X_T = np.vstack(all_X_T)
        X_S = np.vstack(all_X_S)
        return X_T, X_S

    def evaluate_on_validation(
        self,
        student_model: Any,
        student_scaler: Optional[Any],
        is_regressor: bool = False
    ) -> float:
        """
        Evaluate student model on validation set (29 images) to get Validation IoU (%).
        """
        all_y_true = []
        all_y_pred = []
        
        for fname in self.splits["val"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            feats_S = extract_student_features(rgb_img)
            if student_scaler is not None:
                feats_S = student_scaler.transform(feats_S)
                
            if is_regressor:
                preds = student_model.predict(feats_S)
                pred_mask = (preds >= 0.5).astype(np.uint8)
            else:
                pred_mask = student_model.predict(feats_S).astype(np.uint8)
                
            all_y_true.append(gt_mask.flatten())
            all_y_pred.append(pred_mask)
            
        y_true = np.concatenate(all_y_true)
        y_pred = np.concatenate(all_y_pred)
        
        metrics = compute_pixel_metrics(y_true, y_pred)
        return metrics["IoU (%)"]

    def run_tau_study_and_distil(
        self,
        teacher_name: str,
        student_type: str, # 'KNN', 'RF', 'GNB'
        X_T: np.ndarray,
        X_S: np.ndarray
    ) -> Tuple[Any, Any, float, Dict[float, Dict[str, float]]]:
        """
        Tune confidence threshold tau in [0.5, 0.6, 0.7, 0.8, 0.9, 0.95] on validation data,
        and train the best student model.
        """
        pair_key = f"{teacher_name}->{student_type}-S"
        print(f"\n--- Running Distillation & Tau Study: {pair_key} ---")
        
        # 1. Teacher produces soft probability q_p
        teacher_model = self.sp.models[teacher_name]
        teacher_scaler = self.sp.scalers.get(teacher_name, None)
        
        if teacher_scaler is not None:
            X_T_proc = teacher_scaler.transform(X_T)
        else:
            X_T_proc = X_T
            
        q_p = teacher_model.predict_proba(X_T_proc)[:, 1]
        y_hat = (q_p >= 0.5).astype(np.uint8)
        confidence = np.maximum(q_p, 1.0 - q_p)
        total_transfer_pixels = len(q_p)
        
        tau_results = {}
        best_tau = 0.5
        best_val_iou = -1.0
        best_model = None
        best_scaler = None
        
        for tau in TAU_VALUES:
            mask_tau = (confidence >= tau)
            retained_count = int(np.sum(mask_tau))
            retained_pct = (retained_count / total_transfer_pixels) * 100.0
            
            if retained_count < 100:
                print(f"  tau={tau:.2f}: only {retained_count} pixels retained. Skipping.")
                continue
                
            X_filtered = X_S[mask_tau]
            y_filtered = y_hat[mask_tau]
            
            # Train student within capacity budget
            scaler = None
            if student_type == "KNN":
                # Budget: <= 5,000 reference pixels
                n_ref = min(5000, len(y_filtered))
                rng = np.random.default_rng(RANDOM_SEED)
                sample_idx = rng.choice(len(y_filtered), size=n_ref, replace=False)
                X_fit = X_filtered[sample_idx]
                y_fit = y_filtered[sample_idx]
                
                scaler = StandardScaler()
                X_fit_scaled = scaler.fit_transform(X_fit)
                student = KNeighborsClassifier(n_neighbors=7, weights='distance', n_jobs=-1)
                student.fit(X_fit_scaled, y_fit)
                
            elif student_type == "RF":
                # Budget: <= 20 trees, max_depth <= 8
                # Sub-sample to 50,000 for fast robust training
                n_fit = min(50000, len(y_filtered))
                rng = np.random.default_rng(RANDOM_SEED)
                sample_idx = rng.choice(len(y_filtered), size=n_fit, replace=False)
                X_fit = X_filtered[sample_idx]
                y_fit = y_filtered[sample_idx]
                
                student = RandomForestClassifier(
                    n_estimators=20,
                    max_depth=8,
                    random_state=RANDOM_SEED,
                    n_jobs=-1
                )
                student.fit(X_fit, y_fit)
                
            elif student_type == "GNB":
                # Gaussian Naive Bayes on phi_S
                n_fit = min(100000, len(y_filtered))
                rng = np.random.default_rng(RANDOM_SEED)
                sample_idx = rng.choice(len(y_filtered), size=n_fit, replace=False)
                X_fit = X_filtered[sample_idx]
                y_fit = y_filtered[sample_idx]
                
                student = GaussianNB(var_smoothing=1e-3)
                student.fit(X_fit, y_fit)
                
            # Evaluate on validation
            val_iou = self.evaluate_on_validation(student, scaler)
            tau_results[tau] = {
                "Retained Pct": round(retained_pct, 2),
                "Retained Pixels": retained_count,
                "Val IoU (%)": round(val_iou, 2)
            }
            print(f"  tau={tau:.2f} | Retained: {retained_pct:.1f}% ({retained_count} px) | Val IoU: {val_iou:.2f}%")
            
            if val_iou > best_val_iou:
                best_val_iou = val_iou
                best_tau = tau
                best_model = student
                best_scaler = scaler
                
        print(f"--> Best tau for {pair_key}: tau={best_tau:.2f} with Val IoU={best_val_iou:.2f}%")
        self.distilled_models[pair_key] = best_model
        if best_scaler is not None:
            self.distilled_scalers[pair_key] = best_scaler
        self.tuning_history[pair_key] = tau_results
        
        return best_model, best_scaler, best_tau, tau_results

    def evaluate_distilled_on_test(
        self,
        pair_key: str,
        teacher_name: str
    ) -> Dict[str, Any]:
        """
        Evaluate distilled student on all 58 test images, comparing with its teacher.
        """
        student_model = self.distilled_models[pair_key]
        student_scaler = self.distilled_scalers.get(pair_key, None)
        
        all_y_true = []
        all_y_student = []
        all_y_teacher = []
        inference_times = []
        
        for fname in self.splits["test"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            # Predict teacher
            _, teacher_mask = self.sp.predict_image(rgb_img, teacher_name)
            
            # Predict student & measure time incl. feature extraction
            t0 = time.perf_counter()
            feats_S = extract_student_features(rgb_img)
            if student_scaler is not None:
                feats_S = student_scaler.transform(feats_S)
            student_pred = student_model.predict(feats_S).astype(np.uint8)
            student_mask = student_pred.reshape(256, 256)
            t1 = time.perf_counter()
            inference_times.append(t1 - t0)
            
            all_y_true.append(gt_mask.flatten())
            all_y_student.append(student_mask.flatten())
            all_y_teacher.append(teacher_mask.flatten())
            
        y_true_all = np.concatenate(all_y_true)
        y_student_all = np.concatenate(all_y_student)
        y_teacher_all = np.concatenate(all_y_teacher)
        
        metrics = compute_pixel_metrics(y_true_all, y_student_all)
        agreement = compute_agreement(y_teacher_all, y_student_all)
        
        # Teacher IoU reference
        teacher_metrics = compute_pixel_metrics(y_true_all, y_teacher_all)
        retention = compute_retention(metrics["IoU (%)"], teacher_metrics["IoU (%)"])
        
        # Model size
        size_bytes = get_model_size_bytes(student_model)
        if student_scaler is not None:
            size_bytes += get_model_size_bytes(student_scaler)
            
        mean_time_ms = float(np.mean(inference_times) * 1000.0)
        
        metrics.update({
            "Pair": pair_key,
            "Agreement (%)": round(agreement, 2),
            "Retention (rho %)": round(retention, 2),
            "Mean Inference Time (ms)": round(mean_time_ms, 2),
            "Model Size (KB)": round(size_bytes / 1024.0, 2),
            "Teacher IoU (%)": round(teacher_metrics["IoU (%)"], 2),
            "Teacher F1 (%)": round(teacher_metrics["F1 (%)"], 2)
        })
        return metrics

    def run_soft_distillation(
        self,
        best_pair_teacher: str,
        best_pair_student_type: str,
        X_T: np.ndarray,
        X_S: np.ndarray,
        best_tau: float = 0.5
    ) -> Dict[str, Any]:
        """
        Implement soft-label distillation for the best performing pair.
        Methods:
        - Weighted Duplication for RF/GNB (weights q and 1-q).
        - Regression for KNN (KNeighborsRegressor on q_p, thresholded at 0.5).
        """
        print(f"\n==================================================")
        print(f"RUNNING SOFT-LABEL DISTILLATION: {best_pair_teacher} -> {best_pair_student_type}-S")
        print(f"==================================================")
        
        teacher_model = self.sp.models[best_pair_teacher]
        teacher_scaler = self.sp.scalers.get(best_pair_teacher, None)
        
        if teacher_scaler is not None:
            X_T_proc = teacher_scaler.transform(X_T)
        else:
            X_T_proc = X_T
            
        q_p = teacher_model.predict_proba(X_T_proc)[:, 1] # soft continuous probabilities [0, 1]
        
        scaler = None
        if best_pair_student_type == "RF":
            # Weighted duplication: add every sample as 1 with weight q_p, and 0 with weight 1 - q_p
            # Sub-sample 25,000 samples -> 50,000 weighted samples
            n_sub = min(25000, len(q_p))
            rng = np.random.default_rng(RANDOM_SEED)
            idx = rng.choice(len(q_p), size=n_sub, replace=False)
            
            X_sub = X_S[idx]
            q_sub = q_p[idx]
            
            X_dup = np.vstack([X_sub, X_sub])
            y_dup = np.concatenate([np.ones(n_sub, dtype=np.uint8), np.zeros(n_sub, dtype=np.uint8)])
            w_dup = np.concatenate([q_sub, 1.0 - q_sub]).astype(np.float32)
            
            soft_student = RandomForestClassifier(
                n_estimators=20,
                max_depth=8,
                random_state=RANDOM_SEED,
                n_jobs=-1
            )
            print("Fitting RF Student with weighted duplication (sample_weight)...")
            soft_student.fit(X_dup, y_dup, sample_weight=w_dup)
            
        elif best_pair_student_type == "KNN":
            # Regression distillation
            n_sub = min(5000, len(q_p))
            rng = np.random.default_rng(RANDOM_SEED)
            idx = rng.choice(len(q_p), size=n_sub, replace=False)
            
            scaler = StandardScaler()
            X_sub_scaled = scaler.fit_transform(X_S[idx])
            soft_student = KNeighborsRegressor(n_neighbors=7, weights='distance', n_jobs=-1)
            print("Fitting KNN Student with regression on soft probabilities...")
            soft_student.fit(X_sub_scaled, q_p[idx])
            
        else: # GNB
            n_sub = min(50000, len(q_p))
            rng = np.random.default_rng(RANDOM_SEED)
            idx = rng.choice(len(q_p), size=n_sub, replace=False)
            
            X_sub = X_S[idx]
            q_sub = q_p[idx]
            
            X_dup = np.vstack([X_sub, X_sub])
            y_dup = np.concatenate([np.ones(n_sub, dtype=np.uint8), np.zeros(n_sub, dtype=np.uint8)])
            w_dup = np.concatenate([q_sub, 1.0 - q_sub]).astype(np.float32)
            
            soft_student = GaussianNB(var_smoothing=1e-3)
            print("Fitting GNB Student with weighted duplication (sample_weight)...")
            soft_student.fit(X_dup, y_dup, sample_weight=w_dup)
            
        # Evaluate on test set
        all_y_true = []
        all_y_pred = []
        
        for fname in self.splits["test"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            feats_S = extract_student_features(rgb_img)
            if scaler is not None:
                feats_S = scaler.transform(feats_S)
                
            if best_pair_student_type == "KNN":
                probs = soft_student.predict(feats_S)
                pred_mask = (probs >= 0.5).astype(np.uint8)
            else:
                pred_mask = soft_student.predict(feats_S).astype(np.uint8)
                
            all_y_true.append(gt_mask.flatten())
            all_y_pred.append(pred_mask)
            
        y_true_all = np.concatenate(all_y_true)
        y_pred_all = np.concatenate(all_y_pred)
        
        metrics = compute_pixel_metrics(y_true_all, y_pred_all)
        return metrics

def plot_tau_curve(
    tau_results: Dict[float, Dict[str, float]],
    pair_label: str = "RF-T -> RF-S",
    save_path: str = "results/graphs/tau_confidence_study.png"
):
    """
    Plot Validation IoU (%) and Percentage of Retained Pixels vs Confidence Threshold tau.
    """
    taus = sorted(tau_results.keys())
    val_ious = [tau_results[t]["Val IoU (%)"] for t in taus]
    retained_pcts = [tau_results[t]["Retained Pct"] for t in taus]
    
    fig, ax1 = plt.subplots(figsize=(8, 5), dpi=200)
    
    color1 = '#1976d2'
    ax1.set_xlabel('Confidence Threshold (tau)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Validation IoU (%)', color=color1, fontsize=12, fontweight='bold')
    line1 = ax1.plot(taus, val_ious, marker='o', linewidth=2.5, markersize=8, color=color1, label='Validation IoU (%)')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_ylim(min(val_ious) - 2.0, max(val_ious) + 2.0)
    
    # Highlight best tau
    best_idx = np.argmax(val_ious)
    best_tau = taus[best_idx]
    best_val_iou = val_ious[best_idx]
    ax1.scatter([best_tau], [best_val_iou], color='#d32f2f', s=120, zorder=5)
    ax1.annotate(f"Optimal tau={best_tau:.2f}\n(IoU: {best_val_iou:.2f}%)",
                 xy=(best_tau, best_val_iou), xytext=(best_tau - 0.1, best_val_iou + 0.8),
                 arrowprops=dict(facecolor='#d32f2f', shrink=0.08, width=1.5, headwidth=6),
                 fontweight='bold', fontsize=9.5, color='#b71c1c')
    
    ax2 = ax1.twinx()
    color2 = '#388e3c'
    ax2.set_ylabel('Retained Pixels (%)', color=color2, fontsize=12, fontweight='bold')
    line2 = ax2.plot(taus, retained_pcts, marker='s', linestyle='--', linewidth=2.0, markersize=7, color=color2, label='Retained Pixels (%)')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 105)
    
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower left', frameon=True)
    
    plt.title(f"Confidence Threshold (tau) Study: {pair_label}", fontsize=13, fontweight='bold', pad=12)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved tau confidence study plot to: {save_path}")

if __name__ == "__main__":
    from src.supervised_models import SupervisedPipeline
    sp = SupervisedPipeline()
    sp.train_knn_teacher()
    sp.train_rf_teacher()
    sp.train_gnb_teacher()
    sp.train_knn_student_baseline()
    sp.train_rf_student_baseline()
    sp.train_gnb_student_baseline()
    
    dm = DistillationManager(sp)
    X_T, X_S = dm.generate_transfer_samples(samples_per_image=500)
    
    teachers = ["KNN-T", "RF-T", "GNB-T"]
    students = ["KNN", "RF", "GNB"]
    
    matrix_results = {}
    tau_studies = {}
    
    for t_name in teachers:
        for s_type in students:
            pair_key = f"{t_name}->{s_type}-S"
            m, sc, best_tau, tau_hist = dm.run_tau_study_and_distil(t_name, s_type, X_T, X_S)
            tau_studies[pair_key] = tau_hist
            test_res = dm.evaluate_distilled_on_test(pair_key, t_name)
            matrix_results[pair_key] = test_res
            print(f"[{pair_key}] Optimal tau: {best_tau:.2f} | Test IoU: {test_res['IoU (%)']:.2f}% | F1: {test_res['F1 (%)']:.2f}% | Agreement: {test_res['Agreement (%)']:.2f}%")
            
    # Save tau plot for best pair RF-T -> RF-S
    if "RF-T->RF-S" in tau_studies:
        plot_tau_curve(tau_studies["RF-T->RF-S"], "RF-T -> RF-S")
        
    print("\nComplete 3x3 Test IoU (%) Matrix:")
    # Format 3x3 table
    table_data = []
    for t_name in teachers:
        row = {"Teacher": t_name}
        for s_type in students:
            pair_key = f"{t_name}->{s_type}-S"
            row[f"{s_type}-S"] = f"{matrix_results[pair_key]['IoU (%)']:.2f}%"
        table_data.append(row)
    print(pd.DataFrame(table_data).to_string(index=False))

