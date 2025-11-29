#!/usr/bin/env python3
"""Extract Batch 1 of Shakespeare plays"""
from extract_all_plays import main

if __name__ == "__main__":
    print("\n" + "="*70)
    print("BATCH 1: Comedies (Part 1)")
    print("="*70 + "\n")
    main(batch_number=1)

