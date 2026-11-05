"""
Visualization Utilities for Flood Area Segmentation
CS3103 Machine Learning Project - IIT Patna

Provides publication-quality plots:
- Preprocessing samples (RGB, Mask, Overlay)
- Feature map visualisations
- Pipeline architecture diagram
- Distillation confidence filtering (tau study)
- K-Means inertia elbow curve
- Qualitative 6-panel test segmentation comparisons
"""

import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Optional

# Set consistent matplotlib aesthetic
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def plot_preprocessing_samples(
    image_paths: List[str],
    mask_paths: List[str],
    save_path: str = "results/graphs/preprocessing_samples.png"
):
    """
    Plot sample images, their binary ground truth masks, and flood overlay.
    """
    n = len(image_paths)
    fig, axes = plt.subplots(n, 3, figsize=(10, 3.2 * n))
    if n == 1:
        axes = np.expand_dims(axes, 0)
        
    for i, (img_p, msk_p) in enumerate(zip(image_paths, mask_paths)):
        img_bgr = cv2.imread(img_p)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (256, 256), interpolation=cv2.INTER_LINEAR)
        
        raw_mask = cv2.imread(msk_p, cv2.IMREAD_GRAYSCALE)
        bin_mask = (raw_mask >= 128).astype(np.uint8)
        bin_mask_resized = cv2.resize(bin_mask, (256, 256), interpolation=cv2.INTER_NEAREST)
        
        # Create overlay: tint flood region cyan/blue
        overlay = img_resized.copy()
        flood_idx = (bin_mask_resized == 1)
        overlay[flood_idx, 0] = np.clip(overlay[flood_idx, 0] * 0.4, 0, 255)
        overlay[flood_idx, 1] = np.clip(overlay[flood_idx, 1] * 0.7 + 60, 0, 255)
        overlay[flood_idx, 2] = np.clip(overlay[flood_idx, 2] * 0.5 + 120, 0, 255)
        
        axes[i, 0].imshow(img_resized)
        axes[i, 0].set_title(f"Sample {i+1}: RGB Image (256x256)", fontsize=11, fontweight='bold')
        axes[i, 0].axis('off')
        
        axes[i, 1].imshow(bin_mask_resized, cmap='gray')
        flood_pct = (bin_mask_resized.sum() / bin_mask_resized.size) * 100
        axes[i, 1].set_title(f"Binary Mask (Flood: {flood_pct:.1f}%)", fontsize=11, fontweight='bold')
        axes[i, 1].axis('off')
        
        axes[i, 2].imshow(overlay)
        axes[i, 2].set_title("Ground Truth Overlay", fontsize=11, fontweight='bold')
        axes[i, 2].axis('off')
        
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved preprocessing samples to: {save_path}")

def plot_pipeline_diagram(save_path: str = "results/graphs/pipeline_diagram.png"):
    """
    Draw a clean, professional architecture diagram of the Teacher-Student segmentation pipeline.
    """
    fig, ax = plt.subplots(figsize=(14, 7), dpi=200)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Box styles
    teacher_color = '#e3f2fd'
    student_color = '#e8f5e9'
    data_color = '#fff3e0'
    eval_color = '#fce4ec'
    border_color = '#37474f'

    # Title
    ax.text(7, 7.5, "Flood Area Segmentation: Classical ML Teacher-Student Architecture", 
            ha='center', va='center', fontsize=14, fontweight='bold', color='#1a237e')

    # Helper function for drawing boxes
    def draw_box(x, y, w, h, text, title="", color='#ffffff'):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2",
                                     ec=border_color, fc=color, lw=1.5)
        ax.add_patch(box)
        if title:
            ax.text(x + w/2, y + h - 0.35, title, ha='center', va='center', 
                    fontweight='bold', fontsize=10, color='#004d40')
        ax.text(x + w/2, y + (h/2 if not title else h/2 - 0.2), text, 
                ha='center', va='center', fontsize=9, multialignment='center')

    # Data boxes
    draw_box(0.5, 4.8, 2.5, 1.8, "40 Images + GT Masks\n(Supervised Teachers Only)", "Labelled Set L", data_color)
    draw_box(0.5, 1.8, 2.5, 1.8, "163 Images Only\n(No GT Masks Loaded)", "Unlabelled Set U", data_color)

    # Feature boxes
    draw_box(3.8, 4.8, 2.6, 1.8, "RGB, HSV, Lab\nGaussian Blur, Texture\nSobel, Laplacian, Coords\n(dT = 18 dims)", "Rich Features (phi_T)", teacher_color)
    draw_box(3.8, 1.8, 2.6, 1.8, "RGB, Hue, Saturation,\nNormalized Y Position\nDirectly from Image\n(dS = 6 dims <= dT/2)", "Compact Features (phi_S)", student_color)

    # Model boxes
    draw_box(7.2, 4.8, 2.8, 1.8, "KNN-T (>= 20k pixels)\nRF-T (>= 200 trees)\nGNB-T (on phi_T)\nK-Means-T (K>=6, 100k px)", "High-Capacity Teachers", teacher_color)
    draw_box(7.2, 1.8, 2.8, 1.8, "KNN-S (<= 5k pixels)\nRF-S (<= 20 trees, depth<=8)\nGNB-S (on phi_S)\nK-Means-S (K<=4, init)", "Budget-Compliant Students", student_color)

    # Transfer arrow / Knowledge Distillation
    arrow = patches.FancyArrowPatch((8.6, 4.7), (8.6, 3.7), arrowstyle='->', 
                                    mutation_scale=20, lw=2.5, color='#d32f2f')
    ax.add_patch(arrow)
    ax.text(8.8, 4.2, "Distillation Transfer\n(qp, yp_hat, confidence cp >= tau)", 
            fontsize=8.5, fontweight='bold', color='#c62828', va='center')

    # Test & Evaluation
    draw_box(10.8, 3.2, 2.6, 2.2, "All 58 Test Images\n(3,801,088 pixels)\nMetrics: P, R, F1, IoU,\nARI, NMI, Agreement,\nRetention, Speedup, Z", "Final Evaluation", eval_color)

    # Connecting arrows
    def draw_arrow(x1, y1, x2, y2, label=""):
        arr = patches.FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='->',
                                      mutation_scale=15, lw=1.5, color='#37474f')
        ax.add_patch(arr)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.15, label, fontsize=8, ha='center', color='#37474f')

    draw_arrow(3.0, 5.7, 3.8, 5.7)
    draw_arrow(3.0, 2.7, 3.8, 2.7)
    draw_arrow(6.4, 5.7, 7.2, 5.7)
    draw_arrow(6.4, 2.7, 7.2, 2.7)
    draw_arrow(10.0, 2.7, 10.8, 3.8, "Inference")
    draw_arrow(10.0, 5.7, 10.8, 4.8, "Reference")

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"Saved pipeline architecture diagram to: {save_path}")

if __name__ == "__main__":
    try:
        from src.data_preprocessing import get_dataset_splits
    except ImportError:
        from data_preprocessing import get_dataset_splits
    splits = get_dataset_splits()
    data_dir = splits["data_dir"]
    sample_images = [os.path.join(data_dir, "Image", f) for f in splits["lab"][:4]]
    sample_masks = [os.path.join(data_dir, "Mask", f"{os.path.splitext(f)[0]}.png") for f in splits["lab"][:4]]
    plot_preprocessing_samples(sample_images, sample_masks)
    plot_pipeline_diagram()
