# FloodVision-AI Architecture & Technical Specification

## 1. System Overview
FloodVision-AI is an enterprise-grade semantic segmentation and flood risk intelligence platform. It couples classical machine learning with teacher-student knowledge distillation to deliver real-time, low-power inference for edge devices (drones, field microcontrollers) and web clients.

```
                      +-----------------------------+
                      |     Input Aerial / Ground   |
                      |        Photograph           |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     Bilinear Preprocessing  |
                      |      (256 x 256, RGB)       |
                      +--------------+--------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
           v                                                   v
+-----------------------+                           +-----------------------+
|   Compact Feature     |                           |     Rich Feature      |
|    Extractor (phi_S)  |                           |   Extractor (phi_T)   |
|     6 Dimensions      |                           |     18 Dimensions     |
+----------+------------+                           +-----------+-----------+
           |                                                    |
           v                                                    v
+-----------------------+                           +-----------------------+
|  Distilled Students   |                           |    Teacher Ensembles  |
| - RF-S (20 trees)     |                           | - RF-T (200 trees)    |
| - KM-S (K=2 clusters) |                           | - KM-T (9 clusters)   |
+----------+------------+                           +-----------+-----------+
           |                                                    |
           +-------------------------+--------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Confidence Filtering &   |
                      |   Thresholding (tau in [0,1])|
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Median Spatial Filtering  |
                      |          (3 x 3)            |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |  Risk Engine & Base64 AR    |
                      |      Visual Rendering       |
                      +-----------------------------+
```

---

## 2. Feature Space Formulations

### Rich Teacher Representation ($\phi_T \in \mathbb{R}^{18}$)
1. **Spectral Normalized RGB** ($3$ dims): $R, G, B \in [0, 1]$
2. **Perceptual Chrominance** ($6$ dims): HSV ($H, S, V$) + CIE-Lab ($L^*, a^*, b^*$)
3. **Neighborhood Multi-Scale Context** ($3$ dims): Gaussian-smoothed RGB ($\sigma = 1.0$)
4. **Local Structural Statistics** ($2$ dims): Local mean ($5 \times 5$), Local standard deviation ($5 \times 5$ texture variance)
5. **Edge & Curvature Descriptors** ($2$ dims): Sobel gradient magnitude, Laplacian of Gaussian
6. **Physical Gravity Prior** ($2$ dims): Normalized spatial coordinates $x/W, y/H \in [0, 1]$

### Compact Student Representation ($\phi_S \in \mathbb{R}^6$)
1. **Raw Spectral Channels** ($3$ dims): $R, G, B \in [0, 1]$
2. **Fast Context Window** ($1$ dim): Local grayscale mean ($3 \times 3$ box filter)
3. **Edge Localization** ($1$ dim): Sobel gradient magnitude
4. **Vertical Gravity Prior** ($1$ dim): Normalized row position $y/H \in [0, 1]$

---

## 3. Knowledge Distillation Protocol

### Track S: Supervised Transfer
* **Teacher ($f_T$)**: Trained on $L$ (40 ground-truth masks) with rich $18$-D features.
* **Pseudo-Label Generation**: Teacher computes posterior class probabilities $q_p = P_T(y=1|\phi_T(p))$ over transfer pool $L \cup U$ ($203$ images).
* **Confidence Filtering**: Retain pixel $p$ if $c_p = \max(q_p, 1 - q_p) \ge \tau$.
* **Student Optimization**: Compact student ($f_S$) trained on $D_\tau$ using $6$-D features $\phi_S$.

### Track U: Unsupervised K-Means Transfer
* **Teacher ($KM_T$)**: $K_T = 9$ clusters in $18$-D space fitted without masks on $100\text{k}$ pixels.
* **Centroid Projection**: Project $9$ teacher clusters into $K_S = 2$ student centroids by grouping according to teacher cluster mapping $\pi_T$.
* **Invariant Mapping**: Student centroids inherit binary class definitions directly from teacher groups without Lloyd refinement drift.

---

## 4. API Service Contract

### Endpoint: `POST /api/segment`
* **Request**:
  * `image`: Multipart file buffer
  * `sample_id`: Pre-loaded test scene ID (`sample1` ... `sample4`)
  * `model_choice`: `'rf_student'` | `'rf_teacher'` | `'km_student'`
  * `threshold`: Decision threshold float (`0.20` to `0.80`, default `0.50`)
* **Response**:
  * `images`: Object containing base64 data URIs for `original`, `mask`, and `overlay`
  * `analytics`: Numerical coverage percentages, pixel counts, hazard classification, latency telemetry, and model parameters.

