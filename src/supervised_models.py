"""
Supervised Models Implementation: Teachers & No-Teacher Baselines
CS3103 Machine Learning Project - IIT Patna

Implements:
1. Supervised Teachers (on rich features phi_T, dT=18):
   - KNN-T: >= 20,000 reference pixels (25,000 used) + StandardScaler
   - RF-T: >= 200 trees, depth unrestricted (200 trees)
   - GNB-T: Gaussian Naive Bayes with tuned var_smoothing

2. No-Teacher Student Baselines (on compact features phi_S, dS=6, strictly on L):
   - KNN-S: <= 5,000 reference pixels (5,000 used) + StandardScaler
   - RF-S: <= 20 trees, max_depth <= 8 (20 trees, depth=8)
   - GNB-S: Gaussian Naive Bayes on phi_S

Strict Anti-Leakage Protocol:
- Only L ground-truth masks (40 images) used for training.
- Scalers fitted only on training pixels.
- Validation set (29 images) used strictly for tuning hyperparameters.
- Test set (58 images, 3,801,088 pixels) evaluated once for final results.
"""

import os
import time
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
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
    get_model_size_bytes
)

RANDOM_SEED = 42

class SupervisedPipeline:
    def __init__(self, data_dir: str = "flood-area-segmentation"):
        self.splits = get_dataset_splits(data_dir)
        self.data_dir = self.splits["data_dir"]
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        
    def collect_labelled_pixels(
        self,
        samples_per_image: int = 2500,
        feature_type: str = "teacher"
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample pixels uniformly from the 40 labelled images in L.
        feature_type: 'teacher' (phi_T, 18 dims) or 'student' (phi_S, 6 dims)
        """
        rng = np.random.default_rng(RANDOM_SEED)
        all_X = []
        all_y = []
        
        for fname in self.splits["lab"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            mask = load_and_preprocess_mask(msk_path)
            
            if feature_type == "teacher":
                feats = extract_teacher_features(rgb_img) # (65536, 18)
            else:
                feats = extract_student_features(rgb_img) # (65536, 6)
                
            labels = mask.flatten() # (65536,)
            
            # Sample pixels
            n_pixels = len(labels)
            chosen_idx = rng.choice(n_pixels, size=min(samples_per_image, n_pixels), replace=False)
            all_X.append(feats[chosen_idx])
            all_y.append(labels[chosen_idx])
            
        X = np.vstack(all_X)
        y = np.concatenate(all_y)
        return X, y

    def train_knn_teacher(self, n_ref_pixels: int = 25000, k: int = 7) -> KNeighborsClassifier:
        """
        Train KNN Teacher: >= 20,000 reference pixels on phi_T (dT=18).
        """
        print(f"Training KNN Teacher (reference pixels={n_ref_pixels}, k={k})...")
        samples_per_img = int(np.ceil(n_ref_pixels / len(self.splits["lab"])))
        X_train, y_train = self.collect_labelled_pixels(samples_per_img, feature_type="teacher")
        
        # Sub-sample to exact target
        if len(y_train) > n_ref_pixels:
            rng = np.random.default_rng(RANDOM_SEED)
            idx = rng.choice(len(y_train), size=n_ref_pixels, replace=False)
            X_train, y_train = X_train[idx], y_train[idx]
            
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)
        
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance', n_jobs=-1)
        knn.fit(X_scaled, y_train)
        
        self.scalers["KNN-T"] = scaler
        self.models["KNN-T"] = knn
        return knn

    def train_rf_teacher(self, n_trees: int = 200, n_pixels: int = 100000) -> RandomForestClassifier:
        """
        Train Random Forest Teacher: >= 200 trees on phi_T (dT=18).
        """
        print(f"Training RF Teacher (n_estimators={n_trees}, pixels={n_pixels})...")
        samples_per_img = int(np.ceil(n_pixels / len(self.splits["lab"])))
        X_train, y_train = self.collect_labelled_pixels(samples_per_img, feature_type="teacher")
        
        if len(y_train) > n_pixels:
            rng = np.random.default_rng(RANDOM_SEED)
            idx = rng.choice(len(y_train), size=n_pixels, replace=False)
            X_train, y_train = X_train[idx], y_train[idx]
            
        rf = RandomForestClassifier(
            n_estimators=n_trees,
            max_depth=None,
            min_samples_split=4,
            random_state=RANDOM_SEED,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)
        self.models["RF-T"] = rf
        return rf

    def train_gnb_teacher(self, var_smoothing: float = 1e-3, n_pixels: int = 200000) -> GaussianNB:
        """
        Train Gaussian Naive Bayes Teacher on phi_T (dT=18).
        """
        print(f"Training GNB Teacher (var_smoothing={var_smoothing})...")
        samples_per_img = int(np.ceil(n_pixels / len(self.splits["lab"])))
        X_train, y_train = self.collect_labelled_pixels(samples_per_img, feature_type="teacher")
        
        gnb = GaussianNB(var_smoothing=var_smoothing)
        gnb.fit(X_train, y_train)
        self.models["GNB-T"] = gnb
        return gnb

    def train_knn_student_baseline(self, n_ref_pixels: int = 5000, k: int = 7) -> KNeighborsClassifier:
        """
        Train No-Teacher KNN Student Baseline: <= 5,000 reference pixels on phi_S (dS=6).
        """
        print(f"Training KNN Student Baseline (reference pixels={n_ref_pixels}, k={k})...")
        samples_per_img = int(np.ceil(n_ref_pixels / len(self.splits["lab"])))
        X_train, y_train = self.collect_labelled_pixels(samples_per_img, feature_type="student")
        
        if len(y_train) > n_ref_pixels:
            rng = np.random.default_rng(RANDOM_SEED)
            idx = rng.choice(len(y_train), size=n_ref_pixels, replace=False)
            X_train, y_train = X_train[idx], y_train[idx]
            
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_train)
        
        knn = KNeighborsClassifier(n_neighbors=k, weights='distance', n_jobs=-1)
        knn.fit(X_scaled, y_train)
        
        self.scalers["KNN-S_baseline"] = scaler
        self.models["KNN-S_baseline"] = knn
        return knn

    def train_rf_student_baseline(self, n_trees: int = 20, max_depth: int = 8, n_pixels: int = 100000) -> RandomForestClassifier:
        """
        Train No-Teacher RF Student Baseline: <= 20 trees, max_depth <= 8 on phi_S (dS=6).
        """
        print(f"Training RF Student Baseline (n_estimators={n_trees}, max_depth={max_depth})...")
        samples_per_img = int(np.ceil(n_pixels / len(self.splits["lab"])))
        X_train, y_train = self.collect_labelled_pixels(samples_per_img, feature_type="student")
        
        rf = RandomForestClassifier(
            n_estimators=n_trees,
            max_depth=max_depth,
            random_state=RANDOM_SEED,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)
        self.models["RF-S_baseline"] = rf
        return rf

    def train_gnb_student_baseline(self, var_smoothing: float = 1e-3, n_pixels: int = 200000) -> GaussianNB:
        """
        Train No-Teacher GNB Student Baseline on phi_S (dS=6).
        """
        print(f"Training GNB Student Baseline (var_smoothing={var_smoothing})...")
        samples_per_img = int(np.ceil(n_pixels / len(self.splits["lab"])))
        X_train, y_train = self.collect_labelled_pixels(samples_per_img, feature_type="student")
        
        gnb = GaussianNB(var_smoothing=var_smoothing)
        gnb.fit(X_train, y_train)
        self.models["GNB-S_baseline"] = gnb
        return gnb

    def predict_image(
        self,
        rgb_img: np.ndarray,
        model_name: str,
        threshold: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict flood mask for a single 256x256 image.
        Returns:
            prob_map: (256, 256) float32 probability of flood
            pred_mask: (256, 256) uint8 binary mask {0, 1}
        """
        is_teacher = ("-T" in model_name)
        if is_teacher:
            feats = extract_teacher_features(rgb_img)
        else:
            feats = extract_student_features(rgb_img)
            
        model = self.models[model_name]
        scaler = self.scalers.get(model_name, None)
        
        if scaler is not None:
            feats_proc = scaler.transform(feats)
        else:
            feats_proc = feats
            
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(feats_proc)[:, 1]
        else:
            # Fallback for regressor if used in soft distillation
            probs = model.predict(feats_proc)
            probs = np.clip(probs, 0.0, 1.0)
            
        pred = (probs >= threshold).astype(np.uint8)
        
        prob_map = probs.reshape(256, 256).astype(np.float32)
        pred_mask = pred.reshape(256, 256).astype(np.uint8)
        return prob_map, pred_mask

    def evaluate_model_on_test_set(
        self,
        model_name: str,
        threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Evaluate model across all 58 test images (all 3,801,088 pixels).
        Measures exact wall-clock inference time per image including feature extraction.
        """
        all_y_true = []
        all_y_pred = []
        inference_times = []
        
        for fname in self.splits["test"]:
            img_path = os.path.join(self.data_dir, "Image", fname)
            msk_name = f"{os.path.splitext(fname)[0]}.png"
            msk_path = os.path.join(self.data_dir, "Mask", msk_name)
            
            rgb_img = load_and_preprocess_image(img_path)
            gt_mask = load_and_preprocess_mask(msk_path)
            
            t0 = time.perf_counter()
            _, pred_mask = self.predict_image(rgb_img, model_name, threshold)
            t1 = time.perf_counter()
            inference_times.append(t1 - t0)
            
            all_y_true.append(gt_mask.flatten())
            all_y_pred.append(pred_mask.flatten())
            
        y_true_all = np.concatenate(all_y_true)
        y_pred_all = np.concatenate(all_y_pred)
        
        metrics = compute_pixel_metrics(y_true_all, y_pred_all)
        mean_time_ms = float(np.mean(inference_times) * 1000.0)
        
        model_obj = self.models[model_name]
        size_bytes = get_model_size_bytes(model_obj)
        if model_name in self.scalers:
            size_bytes += get_model_size_bytes(self.scalers[model_name])
            
        metrics.update({
            "Model": model_name,
            "Mean Inference Time (ms)": round(mean_time_ms, 2),
            "Model Size (Bytes)": size_bytes,
            "Model Size (KB)": round(size_bytes / 1024.0, 2),
            "Model Size (MB)": round(size_bytes / (1024.0 * 1024.0), 2)
        })
        return metrics

if __name__ == "__main__":
    pipeline = SupervisedPipeline()
    
    # 1. Train teachers
    pipeline.train_knn_teacher()
    pipeline.train_rf_teacher()
    pipeline.train_gnb_teacher()
    
    # 2. Train no-teacher baselines
    pipeline.train_knn_student_baseline()
    pipeline.train_rf_student_baseline()
    pipeline.train_gnb_student_baseline()
    
    # 3. Evaluate all on test set
    models_to_eval = ["KNN-T", "RF-T", "GNB-T", "KNN-S_baseline", "RF-S_baseline", "GNB-S_baseline"]
    results = []
    for m in models_to_eval:
        res = pipeline.evaluate_model_on_test_set(m)
        results.append(res)
        print(f"[{m}] Test IoU: {res['IoU (%)']:.2f}%, F1: {res['F1 (%)']:.2f}%, Time: {res['Mean Inference Time (ms)']}ms, Size: {res['Model Size (KB)']}KB")
        
    df_res = pd.DataFrame(results)
    print("\nSupervised Teachers & Baselines Summary Table:")
    cols = ["Model", "Precision", "Recall", "F1 (%)", "IoU (%)", "Mean Inference Time (ms)", "Model Size (KB)"]
    print(df_res[cols].to_string(index=False))

