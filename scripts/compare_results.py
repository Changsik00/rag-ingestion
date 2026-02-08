#!/usr/bin/env python3
"""
Compare Reranker v1 vs v2 Results

Spec 069: Task 3-1
A/B 테스트 결과 비교 및 의사결정 지원

Usage:
    python scripts/compare_results.py results_v1.json results_v2.json
"""

import argparse
import json
import sys


def load_results(filepath: str) -> dict:
    """Load test results from JSON file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file: {filepath}")
        sys.exit(1)


def calculate_improvement(v1_value: float, v2_value: float) -> tuple[float, str]:
    """Calculate improvement percentage and emoji"""
    if v1_value == 0:
        return 0.0, "❓"
    
    improvement = ((v2_value - v1_value) / v1_value) * 100
    
    if improvement > 5:
        emoji = "✅"
    elif improvement > 0:
        emoji = "🟢"
    elif improvement > -5:
        emoji = "🟡"
    else:
        emoji = "❌"
    
    return improvement, emoji


def compare_results(v1_results: dict, v2_results: dict):
    """Compare v1 and v2 results and make decision"""
    print("\n" + "=" * 70)
    print("Reranker A/B Test Results Comparison")
    print("=" * 70)
    
    # Overall Metrics
    print("\n📊 Overall Metrics:")
    print(f"{'Metric':<20} {'v1':<15} {'v2':<15} {'Change':<20}")
    print("-" * 70)
    
    v1_recall = v1_results["avg_recall"]
    v2_recall = v2_results["avg_recall"]
    recall_imp, recall_emoji = calculate_improvement(v1_recall, v2_recall)
    print(f"{'Recall':<20} {v1_recall:<15.3f} {v2_recall:<15.3f} {recall_emoji} {recall_imp:+.1f}%")
    
    v1_precision = v1_results["avg_precision"]
    v2_precision = v2_results["avg_precision"]
    precision_imp, precision_emoji = calculate_improvement(v1_precision, v2_precision)
    print(f"{'Precision':<20} {v1_precision:<15.3f} {v2_precision:<15.3f} {precision_emoji} {precision_imp:+.1f}%")
    
    v1_f1 = v1_results["f1_score"]
    v2_f1 = v2_results["f1_score"]
    f1_imp, f1_emoji = calculate_improvement(v1_f1, v2_f1)
    print(f"{'F1 Score':<20} {v1_f1:<15.3f} {v2_f1:<15.3f} {f1_emoji} {f1_imp:+.1f}%")
    
    # Category Breakdown
    print("\n📈 Performance by Category:")
    print(f"{'Category':<25} {'v1 Recall':<12} {'v2 Recall':<12} {'Change':<15}")
    print("-" * 70)
    
    categories = {}
    for result in v1_results["results"]:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"v1": [], "v2": []}
        categories[cat]["v1"].append(result["recall"])
    
    for result in v2_results["results"]:
        cat = result["category"]
        categories[cat]["v2"].append(result["recall"])
    
    for cat, data in categories.items():
        v1_avg = sum(data["v1"]) / len(data["v1"])
        v2_avg = sum(data["v2"]) / len(data["v2"])
        cat_imp, cat_emoji = calculate_improvement(v1_avg, v2_avg)
        print(f"{cat:<25} {v1_avg:<12.3f} {v2_avg:<12.3f} {cat_emoji} {cat_imp:+.1f}%")
    
    # Decision Logic
    print("\n" + "=" * 70)
    print("🎯 Decision Analysis")
    print("=" * 70)
    
    criteria_met = []
    criteria_failed = []
    
    # Criterion 1: Recall +10% or more
    if recall_imp >= 10:
        criteria_met.append(f"✅ Recall improved by {recall_imp:.1f}% (>= +10% target)")
    else:
        criteria_failed.append(f"❌ Recall improved by {recall_imp:.1f}% (< +10% target)")
    
    # Criterion 2: Precision within -5%
    if precision_imp >= -5:
        criteria_met.append(f"✅ Precision changed by {precision_imp:.1f}% (>= -5% acceptable)")
    else:
        criteria_failed.append(f"❌ Precision dropped by {precision_imp:.1f}% (< -5% threshold)")
    
    print("\nCriteria Check:")
    for criterion in criteria_met:
        print(f"  {criterion}")
    for criterion in criteria_failed:
        print(f"  {criterion}")
    
    # Final Decision
    print("\n" + "=" * 70)
    if len(criteria_failed) == 0:
        print("🎉 DECISION: ✅ ADOPT v2")
        print("\nv2 meets all criteria:")
        print("  - Recall improvement >= +10%")
        print("  - Precision maintained (>= -5%)")
        print("\nRecommendation:")
        print("  1. Update .env: RERANKER_VERSION=v2")
        print("  2. Restart backend")
        print("  3. Monitor production metrics")
    else:
        print("🔄 DECISION: ❌ KEEP v1")
        print("\nv2 does not meet criteria:")
        for criterion in criteria_failed:
            print(f"  {criterion}")
        print("\nRecommendation:")
        print("  1. Keep RERANKER_VERSION=v1")
        print("  2. Analyze failed categories")
        print("  3. Refine v2 prompt and re-test")
    
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Compare Reranker Test Results")
    parser.add_argument("v1_results", help="v1 results JSON file")
    parser.add_argument("v2_results", help="v2 results JSON file")
    
    args = parser.parse_args()
    
    v1_results = load_results(args.v1_results)
    v2_results = load_results(args.v2_results)
    
    compare_results(v1_results, v2_results)


if __name__ == "__main__":
    main()
