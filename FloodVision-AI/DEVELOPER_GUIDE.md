# FloodVision-AI Developer & Integration Guide

This guide is intended for machine learning engineers, DevOps developers, and evaluators running, testing, or modifying the FloodVision-AI system.

---

## 🛠️ System Prerequisites
* **Operating System**: Windows 10/11, macOS, or Ubuntu Linux
* **Python**: Version 3.10 to 3.14 (64-bit)
* **Node.js**: Version 18.0+ (Tested on v24.14.0, npm v11.9.0)

---

## ⚙️ Local Development Setup

### 1. Clone & Workspace Navigation
```bash
cd FloodVision-AI
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in both `backend/` and `frontend/` if custom hostnames or ports are desired:
```bash
cp .env.example backend/.env
```

### 3. Backend Setup & Run
```bash
cd backend
pip install -r requirements.txt
python main.py
```
* The FastAPI server will initialize on `http://127.0.0.1:8000`.
* Pre-trained models in `models/` will be lazily loaded and cached into RAM upon first invocation.
* You can verify the health endpoint:
  ```bash
  curl http://127.0.0.1:8000/api/health
  ```

### 4. Frontend Setup & Run
Open a separate terminal:
```bash
cd FloodVision-AI/frontend
npm install
npm run dev
```
* Vite will launch the development server at `http://127.0.0.1:3000`.
* Requests to `/api/*` are automatically proxied to `http://127.0.0.1:8000`.

---

## 🧪 Testing the API via Command Line

### Segment an Image using `curl`:
```bash
curl -X POST "http://127.0.0.1:8000/api/segment" \
     -F "image=@../frontend/public/samples/sample1.jpg" \
     -F "model_choice=rf_student" \
     -F "threshold=0.50"
```

### Run Automated Unit Test Script (Python):
```python
import requests

url = "http://127.0.0.1:8000/api/segment"
files = {"image": open("frontend/public/samples/sample1.jpg", "rb")}
data = {"model_choice": "rf_student", "threshold": 0.50}

response = requests.post(url, files=files, data=data)
res = response.json()

print(f"Status: {res['success']}")
print(f"Submerged Percentage: {res['analytics']['flood_percentage']}%")
print(f"Inference Latency: {res['analytics']['performance']['total_latency_ms']} ms")
```

---

## 📦 Production Build (Frontend)
To compile an optimized static distribution of the React frontend:
```bash
cd frontend
npm run build
```
The output will be generated in `frontend/dist/` and can be served via NGINX, AWS S3, or directly through FastAPI via `StaticFiles`.

