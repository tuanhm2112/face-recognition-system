#!/usr/bin/env python3
"""
Benchmark & Cosine Similarity Tool for ArcFace Embeddings
Author: tuanhm2112
"""
import os
import sys
import time
import argparse
import cv2
import numpy as np

# Dynamically locate project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_WEIGHT_PATH = os.path.join(PROJECT_ROOT, "resources", "weights", "w600k_r50.onnx")


def load_model(weight_path=DEFAULT_WEIGHT_PATH, device="cuda"):
    """Load ArcFace model via InsightFace model zoo"""
    if not os.path.isfile(weight_path):
        print(f"[!] Model weight file not found at: {weight_path}")
        print("    Please check resources/weights/README.md or run scripts/download_weights.py")
        sys.exit(1)

    try:
        from insightface.model_zoo import get_model
    except ImportError:
        print("[!] 'insightface' is not installed. Run: pip install insightface onnxruntime")
        sys.exit(1)

    print(f"[*] Loading ArcFace model from: {weight_path}")
    ctx_id = 0 if device.lower() == "cuda" else -1
    model = get_model(weight_path)
    model.prepare(ctx_id=ctx_id)
    print(f"[+] Model loaded successfully (context_id: {ctx_id})")
    return model


def compute_similarity(model, img1_path, img2_path):
    """Compute cosine similarity between two face images"""
    if not os.path.exists(img1_path):
        print(f"[!] Error: Image 1 not found: {img1_path}")
        return None
    if not os.path.exists(img2_path):
        print(f"[!] Error: Image 2 not found: {img2_path}")
        return None

    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        print("[!] Error reading image files. Ensure valid image formats (jpg, png).")
        return None

    img1 = cv2.resize(img1, (112, 112))
    img2 = cv2.resize(img2, (112, 112))

    # Warmup
    for _ in range(3):
        model.get_feat(img1)

    start = time.time()
    emb1 = model.get_feat(img1).flatten()
    emb2 = model.get_feat(img2).flatten()
    end = time.time()

    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)

    if norm1 == 0 or norm2 == 0:
        print("[!] Zero-vector embedding encountered.")
        return None

    cos_sim = float(np.dot(emb1, emb2) / (norm1 * norm2))
    infer_time = (end - start) * 1000

    print(f"\n" + "=" * 45)
    print(f" Image 1: {os.path.basename(img1_path)}")
    print(f" Image 2: {os.path.basename(img2_path)}")
    print(f" Cosine Similarity: {cos_sim:.4f}")
    print(f" Inference Time:    {infer_time:.2f} ms")
    match_status = "MATCH (Same Person)" if cos_sim >= 0.50 else "DIFFERENT PERSON"
    print(f" Status (Threshold 0.50): {match_status}")
    print("=" * 45 + "\n")

    return cos_sim


def interactive_mode(model):
    """Interactive CLI loop"""
    print("\n[i] Running interactive comparison mode (type 'exit' to quit)\n")
    while True:
        try:
            path1 = input("Image 1 path: ").strip().strip('"\'')
            if path1.lower() in ("exit", "q", "quit"):
                break
            path2 = input("Image 2 path: ").strip().strip('"\'')
            if path2.lower() in ("exit", "q", "quit"):
                break
            compute_similarity(model, path1, path2)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break


def main():
    parser = argparse.ArgumentParser(description="ArcFace Cosine Similarity Benchmark")
    parser.add_argument("--img1", type=str, help="Path to first face image")
    parser.add_argument("--img2", type=str, help="Path to second face image")
    parser.add_argument("--weight", type=str, default=DEFAULT_WEIGHT_PATH, help="Path to ArcFace ONNX model")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu"], help="Inference device")
    args = parser.parse_args()

    model = load_model(args.weight, args.device)

    if args.img1 and args.img2:
        compute_similarity(model, args.img1, args.img2)
    else:
        interactive_mode(model)


if __name__ == "__main__":
    main()
