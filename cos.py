#!/usr/bin/env python3
"""
Backward compatibility wrapper for scripts/benchmark_similarity.py
"""
import sys
import os

if __name__ == "__main__":
    from scripts.benchmark_similarity import main
    main()