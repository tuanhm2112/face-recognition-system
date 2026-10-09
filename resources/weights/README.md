# Model Weights Directory

This directory stores deep learning pre-trained weights used for face detection, tracking, and feature recognition.

> **Note:** Due to GitHub's file size limit (maximum 100 MB per file), binary weight files are excluded from Git version control via `.gitignore`.

---

## Required Models

| Model File | Purpose | Size | Source / Architecture |
| :--- | :--- | :--- | :--- |
| **`yolov8m-face-lindevs.pt`** | Real-time Face Detection & Bounding Box Extraction | ~52 MB | YOLOv8-medium fine-tuned on WIDER Face |
| **`w600k_r50.onnx`** | High-precision Face Feature Extraction (512-d embeddings) | ~174 MB | ArcFace ResNet-50 trained on Glint360k (InsightFace) |

---

## How to Obtain Weights

### Option 1: Automatic Download Script
Run the helper script from the repository root:
```bash
python scripts/download_weights.py
```

### Option 2: Manual Download
1. Download `yolov8m-face-lindevs.pt`:
   - [Hugging Face Mirror](https://huggingface.co/arnabdhar/YOLOv8-Face-Detection/resolve/main/model.pt) (rename to `yolov8m-face-lindevs.pt`)
   - Or [GitHub Release lindevs/yolov8-face](https://github.com/lindevs/yolov8-face/releases)
2. Download `w600k_r50.onnx`:
   - [InsightFace Buffalo_l release](https://github.com/deepinsight/insightface/releases)
   - [Hugging Face Mirror](https://huggingface.co/public-data/insightface/resolve/main/models/buffalo_l/w600k_r50.onnx)
3. Place both files directly into `resources/weights/`.

### Directory Structure Verification
```text
resources/weights/
├── .gitkeep
├── README.md
├── w600k_r50.onnx
└── yolov8m-face-lindevs.pt
```
