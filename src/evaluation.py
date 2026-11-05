"""
Evaluation Metrics Module for Flood Area Segmentation
CS3103 Machine Learning Project - IIT Patna

Implements exact metric formulations required by assignment Page 8 & Page 11:
- Micro-averaged pixel-wise metrics over all 58 test images (3,801,088 pixels):
  Precision (P) = TP / (TP + FP)
  Recall (R)    = TP / (TP + FN)
  F1 Score (F1) = 2*TP / (2*TP + FP + FN)
  IoU (Jaccard) = TP / (TP + FP + FN)

- Teacher-Student Comparative Metrics:
  Agreement (A)      = (1/N) * sum(I[y_S == y_T])
  Retention (rho)    = 100 * (IoU_S / IoU_T)
  Compression (CR)   = size_T / size_S  (model size via len(pickle.dumps(model)))
  Speed-up (SU)      = t_T / t_S        (mean test inference time per image incl. features)
  Efficiency Score Z = 0.6 * F1_S(%) + 0.4 * IoU_S(%)

- Clustering Metrics (Track U):
  Adjusted Rand Index (ARI)
  Normalized Mutual Information (NMI)
"""

import pickle
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

def compute_pixel_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Compute binary pixel-wise classification metrics.
    y_true, y_pred: 1D numpy arrays of binary labels {0, 1}.
    Flood (1) is the positive class.
    """
    y_true_bool = (y_true == 1)
    y_pred_bool = (y_pred == 1)
    
    tp = np.logical_and(y_true_bool, y_pred_bool).sum()
    fp = np.logical_and(~y_true_bool, y_pred_bool).sum()
    fn = np.logical_and(y_true_bool, ~y_pred_bool).sum()
    tn = np.logical_and(~y_true_bool, ~y_pred_bool).sum()
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * tp) / (2.0 * tp + fp + fn) if (2.0 * tp + fp + fn) > 0 else 0.0
    iou = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0
    accuracy = (tp + tn) / (tp + fp + fn + tn) if (tp + fp + fn + tn) > 0 else 0.0
    
    return {
        "TP": int(tp),
        "FP": int(fp),
        "FN": int(fn),
        "TN": int(tn),
        "Precision": float(precision),
        "Recall": float(recall),
        "F1": float(f1),
        "IoU": float(iou),
        "Accuracy": float(accuracy),
        "F1 (%)": float(f1 * 100.0),
        "IoU (%)": float(iou * 100.0)
    }

def compute_agreement(y_pred_teacher: np.ndarray, y_pred_student: np.ndarray) -> float:
    """
    Compute pixel agreement percentage between teacher and student predictions.
    Agreement A = (1/N) * sum(I[y_S == y_T])
    """
    matches = (y_pred_teacher == y_pred_student).sum()
    total = y_pred_teacher.size
    return float((matches / total) * 100.0)

def compute_retention(iou_student: float, iou_teacher: float) -> float:
    """
    Retention rho = 100 * IoU_S / IoU_T
    """
    if iou_teacher == 0:
        return 0.0
    return float(100.0 * (iou_student / iou_teacher))

def get_model_size_bytes(model: Any) -> int:
    """
    Compute model memory size in bytes using len(pickle.dumps(model)) as specified in assignment.
    """
    return len(pickle.dumps(model))

def compute_efficiency_score(f1_pct: float, iou_pct: float) -> float:
    """
    Efficiency Score Z = 0.6 * F1_S(%) + 0.4 * IoU_S(%)
    """
    return float(0.6 * f1_pct + 0.4 * iou_pct)

def compute_clustering_metrics(z_teacher: np.ndarray, z_student: np.ndarray, sample_size: int = 100000) -> Dict[str, float]:
    """
    Compute Adjusted Rand Index (ARI) and Normalized Mutual Information (NMI).
    To handle 3.8M test pixels efficiently without quadratic memory spikes, sub-sample uniformly if requested.
    """
    if z_teacher.size > sample_size:
        rng = np.random.default_rng(42)
        idx = rng.choice(z_teacher.size, size=sample_size, replace=False)
        z_t_sub = z_teacher[idx]
        z_s_sub = z_student[idx]
    else:
        z_t_sub = z_teacher
        z_s_sub = z_student
        
    ari = adjusted_rand_score(z_t_sub, z_s_sub)
    nmi = normalized_mutual_info_score(z_t_sub, z_s_sub)
    return {
        "ARI": float(ari),
        "NMI": float(nmi)
    }

