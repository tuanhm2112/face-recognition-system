#!/usr/bin/env python3
"""
Model Weights Verification & Downloader Script
Author: tuanhm2112
"""
import os
import sys
import urllib.request

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEIGHTS_DIR = os.path.join(PROJECT_ROOT, "resources", "weights")

MODELS = {
    "yolov8m-face-lindevs.pt": {
        "description": "YOLOv8m Face Detection model",
        "expected_min_bytes": 50 * 1024 * 1024,  # ~52MB
        "url": "https://github.com/lindevs/yolov8-face/releases/download/v0.0.1/yolov8m-face.pt",
        "alt_urls": [
            "https://huggingface.co/arnabdhar/YOLOv8-Face-Detection/resolve/main/model.pt"
        ]
    },
    "w600k_r50.onnx": {
        "description": "ArcFace ResNet50 (Glint360k) Feature Extractor",
        "expected_min_bytes": 150 * 1024 * 1024, # ~174MB
        "url": "https://github.com/deepinsight/insightface/releases/download/v0.7/w600k_r50.onnx",
        "alt_urls": [
            "https://huggingface.co/public-data/insightface/resolve/main/models/buffalo_l/w600k_r50.onnx"
        ]
    }
}


def check_status():
    """Check existence and size of required weight files"""
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    all_ready = True
    print("\n" + "=" * 60)
    print("      Face Recognition System - Model Weights Status")
    print("=" * 60)

    for filename, info in MODELS.items():
        file_path = os.path.join(WEIGHTS_DIR, filename)
        if os.path.exists(file_path):
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"[OK] {filename}")
            print(f"     Description : {info['description']}")
            print(f"     Path        : {file_path}")
            print(f"     Size        : {size_mb:.2f} MB\n")
        else:
            all_ready = False
            print(f"[MISSING] {filename}")
            print(f"     Description : {info['description']}")
            print(f"     Target Path : {file_path}")
            print(f"     Download    : {info['url']}\n")

    print("=" * 60)
    return all_ready


def download_file(url, target_path):
    """Download file with progress report"""
    print(f"[*] Downloading {os.path.basename(target_path)} from: {url}")
    
    def reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded * 100 / total_size
            speed_mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  -> Progress: {percent:5.1f}% [{speed_mb:.1f}MB / {total_mb:.1f}MB]")
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, target_path, reporthook)
        print("\n[+] Download complete!")
        return True
    except Exception as e:
        print(f"\n[!] Failed to download from {url}: {e}")
        return False


def main():
    os.makedirs(WEIGHTS_DIR, exist_ok=True)
    if check_status():
        print("[+] All required model weights are present. Ready to run!\n")
        return

    print("[!] Some model weights are missing.")
    choice = input("Do you want to attempt downloading missing models automatically? [y/N]: ").strip().lower()
    if choice == 'y':
        for filename, info in MODELS.items():
            target_path = os.path.join(WEIGHTS_DIR, filename)
            if not os.path.exists(target_path):
                success = download_file(info["url"], target_path)
                if not success and "alt_urls" in info:
                    for alt in info["alt_urls"]:
                        print(f"[*] Trying mirror: {alt}")
                        if download_file(alt, target_path):
                            break
        check_status()
    else:
        print("\n[i] Please download the models manually and place them in 'resources/weights/'.")
        print("    Refer to resources/weights/README.md for details.\n")


if __name__ == "__main__":
    main()
