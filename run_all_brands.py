#!/usr/bin/env python3
"""
CREATIVEIQ · Batch Test Runner for Person 2
===========================================
Executes all 3 test brands, asserts output validity, and generates all Person 3 blueprints.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from run_creative_director import run_glowify, run_ecoglow, run_horizon, list_outputs


def run_all():
    print("\n" + "=" * 70)
    print("  CREATIVEIQ (PERSON 2) — 3-BRAND COMPLETE BATCH EXECUTION")
    print("=" * 70)

    print("\n[BRAND 1/3] GLOWIFY (CLEAN SKINCARE)")
    g = run_glowify()
    assert g.brand_name == "Glowify"
    assert len(g.generated_concepts) == 3
    assert len(g.concept_evaluations) == 3

    print("\n[BRAND 2/3] ECOGLOW (SMART HYDRATION IOT)")
    e = run_ecoglow()
    assert e.brand_name == "EcoGlow"
    assert len(e.generated_concepts) == 3
    assert len(e.concept_evaluations) == 3

    print("\n[BRAND 3/3] HORIZON AI (ENTERPRISE B2B SAAS)")
    h = run_horizon()
    assert h.brand_name == "Horizon AI"
    assert len(h.generated_concepts) == 3
    assert len(h.concept_evaluations) == 3

    print("\n" + "=" * 70)
    print("  ALL 3 BRANDS COMPLETED & VERIFIED SUCCESSFULLY!")
    print("=" * 70)
    list_outputs()


if __name__ == "__main__":
    run_all()
