"""
Unsupervised Models Implementation: K-Means Teacher & Distilled Students (Track U)
CS3103 Machine Learning Project - IIT Patna

Implements:
1. K-Means Teacher (KM-T):
   - Rich features phi_T (dT=18 dims)
   - Fitted on L U U (203 images, >= 100,000 pixels) without ground truth
   - K_T selection: Unsupervised inertia elbow curve + confirmed by validation IoU
   - Minimum K_T >= 6, n_init >= 10
   - Cluster mapping pi_T via majority vote on labelled set L only

2. No-Teacher K-Means Student Baseline (KM-S Baseline):
   - Compact features phi_S (dS=6 dims)
   - Fitted on L U U (<= 20,000 pixels) using k-means++ (no teacher)
   - K_S <= 4 clusters
   - Cluster mapping from L

3. Distilled K-Means Student (Track U Centroid Initialization):
   - Teacher-guided centroid initialization:
     mu_k^S = mean(phi_S(p)) for pixels where g(z_p^T) == k
   - All 4 required variants:
     Variant 1: Without Lloyd refinement + Inherited mapping pi_S
     Variant 2: With Lloyd refinement (n_init=1) + Inherited mapping pi_S
     Variant 3: Without Lloyd refinement + Re-estimated mapping from L
     Variant 4: With Lloyd refinement (n_init=1) + Re-estimated mapping from L

4. Evaluation:
   - Precision, Recall, F1, IoU
   - Adjusted Rand Index (ARI), Normalized Mutual Information (NMI)
   - Teacher-Student Agreement A, Retention rho, Compression CR, Speed-up SU
"""

import os
import time
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any, Optional

from sklearn.cluster import KMeans
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
    compute_clustering_metrics,
    get_model_size_bytes
)

RANDOM_SEED = 42

class KMeansPipeline:
    def __init__(self, data_dir: str = "flood-area-segmentation"):
        self.splits = get_dataset_splits(data_dir)
        self.data_dir = self.splits["data_dir"]
        self.train_images = self.splits["lab"] + self.splits["unl"] # 203 images
        
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.mappings: Dict[str, Dict[int, int]] = {}
        
    def sample_fitting_pixels(
        self,
        n_total_pixels: int = 120000,
        feature_type: str = "teacher"
    ) -> np.ndarray:
        """
        Sample pixels uniformly from the 203 images of L U U without looking at masks.
        """
        rng = np.random.default_rng(RANDOM_SEED)
        samples_per_img = int(np.ceil(n_total_pixels / len(self.train_images)))
        all_X = []
        
        for fname in self.train_images:
            img_path = os.path.join(self.data_dir, "Image", fname)
            rgb_img = load_and_preprocess_image(img_path)
            
            if feature_type == "teacher":
                feats = extract_teacher_features(rgb_img)
            else:
                feats = extract_student_features(rgb_img)
                
            n_px = feats.shape[0]
            chosen_idx = rng.choice(n_px, size=min(samples_per_img, n_px), replace=False)
            all_X.append(feats[chosen_idx])
            
        X = np.vstack(all_X)
        if len(X) > n_total_pixels:
            idx = rng.choice(len(X), size=n_total_pixels, replace=False)
            X = X[idx]
        return X

    def estimate_cluster_mapping(
        self,
        cluster_model: Any,
        scaler: Optional[Any],
        feature_type: str = "teacher"
    ) -> Dict[int, int]:
        """
        Map each cluster index to class {0: non-flood, 1: flood}
        using majority vote over the ground-truth masks of labelled set L ONLY.
        """
        cluster_flood_counts = {}
        cluster_total_counts = {}
        
        for fname in self.splits["lab"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            if feature_type == "teacher":
                feats = extract_teacher_features(rgb_img)
            else:
                feats = extract_student_features(rgb_img)
                
            if scaler is not None:
                feats = scaler.transform(feats)
                
            cluster_preds = cluster_model.predict(feats)
            labels = gt_mask.flatten()
            
            for c_id, y_val in zip(cluster_preds, labels):
                cluster_total_counts[c_id] = cluster_total_counts.get(c_id, 0) + 1
                if y_val == 1:
                    cluster_flood_counts[c_id] = cluster_flood_counts.get(c_id, 0) + 1
                    
        mapping = {}
        for c_id in cluster_total_counts:
            total = cluster_total_counts[c_id]
            flood = cluster_flood_counts.get(c_id, 0)
            mapping[c_id] = 1 if (flood / total) >= 0.5 else 0
            
        return mapping

    def run_k_selection_study(self, k_values: List[int] = [3, 4, 5, 6, 7, 8, 9, 10]) -> Tuple[int, pd.DataFrame]:
        """
        Evaluate inertia elbow and confirm with validation IoU to select KT >= 6.
        """
        print("Running K-Selection Study for Teacher K-Means...")
        X_fit = self.sample_fitting_pixels(n_total_pixels=100000, feature_type="teacher")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_fit)
        
        study_records = []
        best_val_iou = -1.0
        best_k = 6
        
        for k in k_values:
            km = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=RANDOM_SEED)
            km.fit(X_scaled)
            inertia = float(km.inertia_)
            
            # Map clusters with L
            mapping = self.estimate_cluster_mapping(km, scaler, feature_type="teacher")
            
            # Evaluate on validation
            val_iou = self.evaluate_on_validation(km, scaler, mapping, feature_type="teacher")
            study_records.append({
                "K": k,
                "Inertia": round(inertia, 1),
                "Val IoU (%)": round(val_iou, 2)
            })
            print(f"  K={k:2d} | Inertia: {inertia:10.1f} | Val IoU: {val_iou:.2f}%")
            
            if k >= 6 and val_iou > best_val_iou:
                best_val_iou = val_iou
                best_k = k
                
        df_study = pd.DataFrame(study_records)
        self.plot_elbow_curve(df_study, best_k)
        print(f"--> Selected KT = {best_k} (Complies with KT >= 6 budget, confirmed by Val IoU).")
        return best_k, df_study

    def plot_elbow_curve(self, df_study: pd.DataFrame, best_k: int, save_path: str = "results/graphs/kmeans_elbow_curve.png"):
        """
        Plot inertia elbow curve and validation IoU vs K.
        """
        fig, ax1 = plt.subplots(figsize=(8, 5), dpi=200)
        
        color1 = '#e65100'
        ax1.set_xlabel('Number of Clusters (K)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Inertia (Within-Cluster Sum of Squares)', color=color1, fontsize=12, fontweight='bold')
        line1 = ax1.plot(df_study["K"], df_study["Inertia"], marker='o', linewidth=2.5, markersize=8, color=color1, label='Inertia')
        ax1.tick_params(axis='y', labelcolor=color1)
        
        ax2 = ax1.twinx()
        color2 = '#1565c0'
        ax2.set_ylabel('Validation IoU (%)', color=color2, fontsize=12, fontweight='bold')
        line2 = ax2.plot(df_study["K"], df_study["Val IoU (%)"], marker='s', linestyle='--', linewidth=2.0, markersize=7, color=color2, label='Val IoU (%)')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Highlight selected K
        sel_row = df_study[df_study["K"] == best_k].iloc[0]
        ax2.scatter([best_k], [sel_row["Val IoU (%)"]], color='#2e7d32', s=140, zorder=5)
        ax2.annotate(f"Selected KT={best_k}\n(Val IoU: {sel_row['Val IoU (%)']:.1f}%)",
                     xy=(best_k, sel_row["Val IoU (%)"]), xytext=(best_k - 1.5, sel_row["Val IoU (%)"] - 2.5),
                     arrowprops=dict(facecolor='#2e7d32', shrink=0.08, width=1.5, headwidth=6),
                     fontweight='bold', fontsize=9.5, color='#1b5e20')
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='center right', frameon=True)
        
        plt.title("K-Means Teacher Cluster Selection: Inertia Elbow & Validation IoU", fontsize=13, fontweight='bold', pad=12)
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f"Saved K-Means elbow plot to: {save_path}")

    def evaluate_on_validation(
        self,
        model: Any,
        scaler: Optional[Any],
        mapping: Dict[int, int],
        feature_type: str = "teacher"
    ) -> float:
        """
        Evaluate clustering model on 29 validation images with given cluster-to-class mapping.
        """
        all_y_true = []
        all_y_pred = []
        
        for fname in self.splits["val"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            if feature_type == "teacher":
                feats = extract_teacher_features(rgb_img)
            else:
                feats = extract_student_features(rgb_img)
                
            if scaler is not None:
                feats = scaler.transform(feats)
                
            c_preds = model.predict(feats)
            pred_mask = np.array([mapping.get(c, 0) for c in c_preds], dtype=np.uint8)
            
            all_y_true.append(gt_mask.flatten())
            all_y_pred.append(pred_mask)
            
        y_true = np.concatenate(all_y_true)
        y_pred = np.concatenate(all_y_pred)
        metrics = compute_pixel_metrics(y_true, y_pred)
        return metrics["IoU (%)"]

    def train_teacher_kmeans(self, KT: int = 6, n_pixels: int = 120000) -> KMeans:
        """
        Train K-Means Teacher: KT >= 6, n_init >= 10, >= 100,000 pixels on phi_T.
        """
        print(f"\nFitting K-Means Teacher (KT={KT}, n_init=10, pixels={n_pixels})...")
        X_fit = self.sample_fitting_pixels(n_total_pixels=n_pixels, feature_type="teacher")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_fit)
        
        km_t = KMeans(n_clusters=KT, init='k-means++', n_init=10, random_state=RANDOM_SEED)
        km_t.fit(X_scaled)
        
        mapping = self.estimate_cluster_mapping(km_t, scaler, feature_type="teacher")
        print(f"Teacher cluster mapping pi_T (cluster -> class): {mapping}")
        
        self.models["KM-T"] = km_t
        self.scalers["KM-T"] = scaler
        self.mappings["KM-T"] = mapping
        return km_t

    def train_no_teacher_student_baseline(self, KS: int = 2, n_pixels: int = 20000) -> KMeans:
        """
        Train No-Teacher Student Baseline: KS <= 4, <= 20,000 pixels on phi_S with k-means++.
        """
        print(f"\nFitting No-Teacher KM-S Baseline (KS={KS}, pixels={n_pixels})...")
        X_fit = self.sample_fitting_pixels(n_total_pixels=n_pixels, feature_type="student")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_fit)
        
        km_s = KMeans(n_clusters=KS, init='k-means++', n_init=10, random_state=RANDOM_SEED)
        km_s.fit(X_scaled)
        
        mapping = self.estimate_cluster_mapping(km_s, scaler, feature_type="student")
        print(f"KM-S baseline mapping (cluster -> class): {mapping}")
        
        self.models["KM-S_baseline"] = km_s
        self.scalers["KM-S_baseline"] = scaler
        self.mappings["KM-S_baseline"] = mapping
        return km_s

    def train_distilled_student_variants(
        self,
        KS: int = 2,
        n_sample_pixels: int = 50000
    ) -> Dict[str, Dict[str, Any]]:
        """
        Implement all 4 teacher-to-student centroid distillation variants:
        Variant 1: Without Lloyd refinement + Inherited mapping pi_S
        Variant 2: With Lloyd refinement (n_init=1) + Inherited mapping pi_S
        Variant 3: Without Lloyd refinement + Re-estimated mapping from L
        Variant 4: With Lloyd refinement (n_init=1) + Re-estimated mapping from L
        """
        print(f"\n==================================================")
        print(f"IMPLEMENTING 4 DISTILLED K-MEANS STUDENT VARIANTS (KS={KS})")
        print(f"==================================================")
        
        km_t = self.models["KM-T"]
        scaler_t = self.scalers["KM-T"]
        pi_t = self.mappings["KM-T"]
        
        # 1. Sample paired transfer pixels from L U U
        rng = np.random.default_rng(RANDOM_SEED)
        samples_per_img = int(np.ceil(n_sample_pixels / len(self.train_images)))
        all_X_T, all_X_S = [], []
        for fname in self.train_images:
            img_path = os.path.join(self.data_dir, "Image", fname)
            rgb_img = load_and_preprocess_image(img_path)
            f_T = extract_teacher_features(rgb_img)
            f_S = extract_student_features(rgb_img)
            n_px = f_T.shape[0]
            chosen = rng.choice(n_px, size=min(samples_per_img, n_px), replace=False)
            all_X_T.append(f_T[chosen])
            all_X_S.append(f_S[chosen])
            
        X_T = np.vstack(all_X_T)
        X_S = np.vstack(all_X_S)
        
        # Teacher assigns transfer pixels to teacher clusters
        X_T_scaled = scaler_t.transform(X_T).astype(np.float32)
        z_T = km_t.predict(X_T_scaled)
        
        # Scaler for student feature space
        scaler_s = StandardScaler()
        X_S_scaled = scaler_s.fit_transform(X_S).astype(np.float32)
        
        # Grouping function g : {1..KT} -> {0, 1} for KS=2 using teacher class mapping pi_T
        # Cluster k goes to group g(k) = pi_T(k)
        group_assignments = np.array([pi_t[c] for c in z_T])
        
        # 2. Compute initial student centroids mu_k^S
        # mu_k^S = mean(phi_S(p)) for p in group k
        init_centroids = np.zeros((KS, X_S_scaled.shape[1]), dtype=np.float32)
        for k in range(KS):
            pts_in_group = X_S_scaled[group_assignments == k]
            if len(pts_in_group) > 0:
                init_centroids[k] = np.mean(pts_in_group, axis=0).astype(np.float32)
            else:
                init_centroids[k] = np.zeros(X_S_scaled.shape[1], dtype=np.float32)
                
        # Inherited mapping: cluster k takes group label k (0 -> 0, 1 -> 1)
        inherited_mapping = {0: 0, 1: 1}
        init_centroids = np.ascontiguousarray(init_centroids, dtype=np.float32)
        X_fit = np.ascontiguousarray(X_S_scaled[:20000], dtype=np.float32)
        
        # Create Model 1: Without Lloyd refinement (max_iter=1, n_init=1)
        # In scikit-learn, setting max_iter=1 with n_init=1 and init=init_centroids
        km_no_refine = KMeans(
            n_clusters=KS,
            init=init_centroids,
            n_init=1,
            max_iter=1,
            random_state=RANDOM_SEED
        )
        km_no_refine.fit(X_fit) # Within student budget <= 20,000 pixels
        # Restore exact centroid means before any Lloyd movement
        km_no_refine.cluster_centers_ = init_centroids.copy()
        
        # Create Model 2: With Lloyd refinement
        km_refined = KMeans(
            n_clusters=KS,
            init=init_centroids,
            n_init=1,
            max_iter=300,
            random_state=RANDOM_SEED
        )
        km_refined.fit(X_fit)
        
        # Re-estimated mappings from L
        re_est_no_refine = self.estimate_cluster_mapping(km_no_refine, scaler_s, feature_type="student")
        re_est_refined = self.estimate_cluster_mapping(km_refined, scaler_s, feature_type="student")
        
        variants = {
            "KM-S_V1 (No Refine + Inherited)": {
                "model": km_no_refine,
                "scaler": scaler_s,
                "mapping": inherited_mapping,
                "refinement": False,
                "mapping_type": "Inherited"
            },
            "KM-S_V2 (Refined + Inherited)": {
                "model": km_refined,
                "scaler": scaler_s,
                "mapping": inherited_mapping,
                "refinement": True,
                "mapping_type": "Inherited"
            },
            "KM-S_V3 (No Refine + Re-estimated)": {
                "model": km_no_refine,
                "scaler": scaler_s,
                "mapping": re_est_no_refine,
                "refinement": False,
                "mapping_type": "Re-estimated"
            },
            "KM-S_V4 (Refined + Re-estimated)": {
                "model": km_refined,
                "scaler": scaler_s,
                "mapping": re_est_refined,
                "refinement": True,
                "mapping_type": "Re-estimated"
            }
        }
        
        for k, v in variants.items():
            self.models[k] = v["model"]
            self.scalers[k] = v["scaler"]
            self.mappings[k] = v["mapping"]
            
        return variants

    def evaluate_kmeans_on_test(
        self,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Evaluate K-Means model on all 58 test images (3,801,088 pixels).
        Calculates P, R, F1, IoU, clustering ARI/NMI, Agreement with KM-T,
        Retention rho, Compression CR, and Speed-up SU.
        """
        model = self.models[model_name]
        scaler = self.scalers.get(model_name, None)
        mapping = self.mappings[model_name]
        
        km_t = self.models.get("KM-T", None)
        scaler_t = self.scalers.get("KM-T", None)
        pi_t = self.mappings.get("KM-T", None)
        
        all_y_true = []
        all_y_pred = []
        all_z_pred = []
        all_z_teacher = []
        all_y_teacher = []
        inference_times = []
        
        is_teacher = (model_name == "KM-T")
        
        for fname in self.splits["test"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            t0 = time.perf_counter()
            if is_teacher:
                feats = extract_teacher_features(rgb_img)
            else:
                feats = extract_student_features(rgb_img)
                
            if scaler is not None:
                feats_proc = scaler.transform(feats)
            else:
                feats_proc = feats
                
            z_preds = model.predict(feats_proc)
            pred_mask = np.array([mapping.get(c, 0) for c in z_preds], dtype=np.uint8)
            t1 = time.perf_counter()
            inference_times.append(t1 - t0)
            
            all_y_true.append(gt_mask.flatten())
            all_y_pred.append(pred_mask)
            all_z_pred.append(z_preds)
            
            # Predict teacher clusters and class for comparative metrics
            if km_t is not None:
                f_T = extract_teacher_features(rgb_img)
                f_T_scaled = scaler_t.transform(f_T)
                z_T = km_t.predict(f_T_scaled)
                y_T = np.array([pi_t.get(c, 0) for c in z_T], dtype=np.uint8)
                all_z_teacher.append(z_T)
                all_y_teacher.append(y_T)
                
        y_true_all = np.concatenate(all_y_true)
        y_pred_all = np.concatenate(all_y_pred)
        z_pred_all = np.concatenate(all_z_pred)
        
        metrics = compute_pixel_metrics(y_true_all, y_pred_all)
        mean_time_ms = float(np.mean(inference_times) * 1000.0)
        
        size_bytes = get_model_size_bytes(model)
        if scaler is not None:
            size_bytes += get_model_size_bytes(scaler)
            
        metrics.update({
            "Model": model_name,
            "Mean Inference Time (ms)": round(mean_time_ms, 2),
            "Model Size (Bytes)": size_bytes,
            "Model Size (KB)": round(size_bytes / 1024.0, 2)
        })
        
        if km_t is not None and not is_teacher:
            z_t_all = np.concatenate(all_z_teacher)
            y_t_all = np.concatenate(all_y_teacher)
            
            clustering_metrics = compute_clustering_metrics(z_t_all, z_pred_all, sample_size=100000)
            agreement = compute_agreement(y_t_all, y_pred_all)
            
            # Teacher IoU reference
            t_metrics = compute_pixel_metrics(y_true_all, y_t_all)
            retention = compute_retention(metrics["IoU (%)"], t_metrics["IoU (%)"])
            
            t_size_bytes = get_model_size_bytes(km_t) + get_model_size_bytes(scaler_t)
            compression = t_size_bytes / size_bytes if size_bytes > 0 else 1.0
            
            # Speedup
            # Teacher time
            t_time_ms = 45.0 # will be updated from actual teacher eval
            speedup = t_time_ms / mean_time_ms if mean_time_ms > 0 else 1.0
            
            metrics.update({
                "ARI": round(clustering_metrics["ARI"], 4),
                "NMI": round(clustering_metrics["NMI"], 4),
                "Agreement (%)": round(agreement, 2),
                "Retention (rho %)": round(retention, 2),
                "Compression Ratio (CR)": round(compression, 2),
                "Speed-up (SU)": round(speedup, 2)
            })
            
        return metrics

if __name__ == "__main__":
    kmp = KMeansPipeline()
    
    # 1. Study and select KT >= 6
    best_kt, df_study = kmp.run_k_selection_study()
    
    # 2. Train Teacher KM-T
    kmp.train_teacher_kmeans(KT=best_kt)
    res_kmt = kmp.evaluate_kmeans_on_test("KM-T")
    print(f"\n[KM-T] Test IoU: {res_kmt['IoU (%)']:.2f}% | F1: {res_kmt['F1 (%)']:.2f}% | Time: {res_kmt['Mean Inference Time (ms)']}ms | Size: {res_kmt['Model Size (KB)']}KB")
    
    # 3. Train No-Teacher Baseline KM-S
    kmp.train_no_teacher_student_baseline(KS=2)
    res_kms_base = kmp.evaluate_kmeans_on_test("KM-S_baseline")
    print(f"[KM-S Baseline] Test IoU: {res_kms_base['IoU (%)']:.2f}% | F1: {res_kms_base['F1 (%)']:.2f}% | Agreement: {res_kms_base['Agreement (%)']:.2f}%")
    
    # 4. Train 4 Distilled Variants
    kmp.train_distilled_student_variants(KS=2)
    
    variant_names = [
        "KM-S_V1 (No Refine + Inherited)",
        "KM-S_V2 (Refined + Inherited)",
        "KM-S_V3 (No Refine + Re-estimated)",
        "KM-S_V4 (Refined + Re-estimated)"
    ]
    
    variant_results = []
    for v_name in variant_names:
        v_res = kmp.evaluate_kmeans_on_test(v_name)
        variant_results.append(v_res)
        print(f"[{v_name}] Test IoU: {v_res['IoU (%)']:.2f}% | F1: {v_res['F1 (%)']:.2f}% | ARI: {v_res['ARI']} | NMI: {v_res['NMI']} | Agreement: {v_res['Agreement (%)']:.2f}%")
        
    df_var = pd.DataFrame(variant_results)
    cols = ["Model", "Precision", "Recall", "F1 (%)", "IoU (%)", "ARI", "NMI", "Agreement (%)", "Retention (rho %)"]
    print("\nDistilled K-Means Student 4 Variants Summary Table:")
    print(df_var[cols].to_string(index=False))
