# -*- coding: utf-8 -*-
"""
Save production-ready trained models for the consumer web application:
1. Distilled RF Student (Fast, Compact Champion)
2. RF Teacher (Maximum Precision)
3. Distilled K-Means Student (Unsupervised Champion)
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import os, sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data_preprocessing import get_dataset_splits, load_and_preprocess_image, load_and_preprocess_mask
    from src.feature_extraction import extract_teacher_features, extract_student_features
except ImportError:
    from data_preprocessing import get_dataset_splits, load_and_preprocess_image, load_and_preprocess_mask
    from feature_extraction import extract_teacher_features, extract_student_features

def train_and_save_production_models():
    os.makedirs("results/models", exist_ok=True)
    splits = get_dataset_splits()
    L_files = splits["lab"]
    U_files = splits["unl"]

    print("--- 1. Training & Saving Supervised RF Teacher ---")
    # Sample 100k pixels from 40 L images
    X_T_list, y_list = [], []
    for f in L_files:
        img_p = os.path.join(splits["data_dir"], "Image", f)
        mask_p = os.path.join(splits["data_dir"], "Mask", os.path.splitext(f)[0] + ".png")
        img = load_and_preprocess_image(img_p)
        mask = load_and_preprocess_mask(mask_p)
        phi_T = extract_teacher_features(img)
        
        # sample 2,500 pixels per image (100k total)
        idx = np.random.RandomState(42).choice(256*256, 2500, replace=False)
        X_T_list.append(phi_T[idx])
        y_list.append(mask.flatten()[idx])
    
    X_T_train = np.vstack(X_T_list)
    y_train = np.concatenate(y_list)
    
    scaler_T = StandardScaler().fit(X_T_train)
    X_T_scaled = scaler_T.transform(X_T_train)
    
    rf_teacher = RandomForestClassifier(n_estimators=200, max_depth=None, random_state=42, n_jobs=-1)
    rf_teacher.fit(X_T_scaled, y_train)
    
    with open("results/models/rf_teacher.pkl", "wb") as f:
        pickle.dump({"model": rf_teacher, "scaler": scaler_T, "feature_type": "teacher", "name": "Random Forest Teacher (18-D)"}, f)
    print("Saved results/models/rf_teacher.pkl successfully!")

    print("--- 2. Training & Saving Distilled RF Student ---")
    # Generate confident pseudo-labels from RF teacher on L + U at tau=0.95
    X_S_list, y_pseudo_list = [], []
    sample_files = L_files + U_files[:40] # 80 images for high diversity
    
    for f in sample_files:
        img_p = os.path.join(splits["data_dir"], "Image", f)
        img = load_and_preprocess_image(img_p)
        phi_T = extract_teacher_features(img)
        phi_S = extract_student_features(img)
        
        # teacher predictions
        phi_T_scaled = scaler_T.transform(phi_T)
        probs = rf_teacher.predict_proba(phi_T_scaled)[:, 1]
        conf = np.maximum(probs, 1.0 - probs)
        
        # filter confident pixels tau >= 0.90
        mask_conf = conf >= 0.90
        if np.sum(mask_conf) > 0:
            idx = np.where(mask_conf)[0]
            if len(idx) > 500:
                idx = np.random.RandomState(42).choice(idx, 500, replace=False)
            X_S_list.append(phi_S[idx])
            y_pseudo_list.append((probs[idx] >= 0.5).astype(np.uint8))
            
    X_S_train = np.vstack(X_S_list)
    y_S_train = np.concatenate(y_pseudo_list)
    
    scaler_S = StandardScaler().fit(X_S_train)
    X_S_scaled = scaler_S.transform(X_S_train)
    
    rf_student = RandomForestClassifier(n_estimators=20, max_depth=8, random_state=42, n_jobs=-1)
    rf_student.fit(X_S_scaled, y_S_train)
    
    with open("results/models/distilled_rf_student.pkl", "wb") as f:
        pickle.dump({"model": rf_student, "scaler": scaler_S, "feature_type": "student", "name": "Distilled RF Student (6-D)"}, f)
    print("Saved results/models/distilled_rf_student.pkl successfully!")

    print("--- 3. Training & Saving Distilled K-Means Student ---")
    # 2 cluster student initialized from teacher centroids
    # Compute centroids from student features grouped by flood / non-flood
    centroid_flood = np.mean(X_S_scaled[y_S_train == 1], axis=0)
    centroid_dry = np.mean(X_S_scaled[y_S_train == 0], axis=0)
    init_centroids = np.ascontiguousarray(np.vstack([centroid_dry, centroid_flood]), dtype=np.float32)
    
    km_student = KMeans(n_clusters=2, init=init_centroids, n_init=1, random_state=42)
    km_student.fit(np.ascontiguousarray(X_S_scaled[:10000], dtype=np.float32))
    
    with open("results/models/distilled_km_student.pkl", "wb") as f:
        pickle.dump({
            "model": km_student,
            "scaler": scaler_S,
            "feature_type": "student",
            "cluster_map": {0: 0, 1: 1}, # 1 is flood
            "name": "Distilled K-Means Student (Unsupervised, 6-D)"
        }, f)
    print("Saved results/models/distilled_km_student.pkl successfully!")

if __name__ == "__main__":
    train_and_save_production_models()
