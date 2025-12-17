#!/usr/bin/env python3
import json
import sys
import glob

# Find latest test results
json_files = glob.glob("knowledge_base_test_results*.json")
if not json_files:
    print("No test results found")
    sys.exit(1)

latest = max(json_files)
print(f"Analyzing: {latest}\n")

data = json.load(open(latest))
cycles = data.get('cycles', [])
all_tests = []
[all_tests.extend(c.get('tests', [])) for c in cycles]

# Analyze Cycle 1 failures
cycle1_tests = [t for t in all_tests if t.get('test_id', '').startswith('C1_')]
cycle1_failed = [t for t in cycle1_tests if t.get('status') == 'failed']
print("="*80)
print("CYCLE 1 FAILURES ANALYSIS")
print("="*80)
print(f"Total Cycle 1 failures: {len(cycle1_failed)}/30")
for t in cycle1_failed:
    print(f"  {t.get('test_id')} ({t.get('type')}): Accuracy={t.get('accuracy', 0):.1f}%, Error={t.get('error', 'None')}")

# Analyze accuracy by type
faq = [t for t in all_tests if t.get('type') == 'FAQ']
file = [t for t in all_tests if t.get('type') == 'FILE']
crawl = [t for t in all_tests if t.get('type') == 'CRAWL']

faq_acc = [t.get('accuracy', 0) or 0 for t in faq]
file_acc = [t.get('accuracy', 0) or 0 for t in file]
crawl_acc = [t.get('accuracy', 0) or 0 for t in crawl]

print("\n" + "="*80)
print("ACCURACY BREAKDOWN")
print("="*80)
print(f"FAQ:   {sum(faq_acc)/len(faq_acc):.1f}% (weight: {len(faq)/150*100:.1f}%)")
print(f"FILE:  {sum(file_acc)/len(file_acc):.1f}% (weight: {len(file)/150*100:.1f}%)")
print(f"CRAWL: {sum(crawl_acc)/len(crawl_acc):.1f}% (weight: {len(crawl)/150*100:.1f}%)")
overall = (sum(faq_acc) + sum(file_acc) + sum(crawl_acc)) / 150
print(f"\nOverall: {overall:.1f}%")

# Check FILE accuracy distribution
print("\n" + "="*80)
print("FILE ACCURACY DISTRIBUTION (Why FILE is low)")
print("="*80)
print(f"  <30%: {sum(1 for a in file_acc if a < 30)} tests")
print(f"  30-40%: {sum(1 for a in file_acc if 30 <= a < 40)} tests")
print(f"  40-50%: {sum(1 for a in file_acc if 40 <= a < 50)} tests")
print(f"  50-60%: {sum(1 for a in file_acc if 50 <= a < 60)} tests")
print(f"  >60%: {sum(1 for a in file_acc if a >= 60)} tests")

# Check semantic similarity and fact coverage for FILE tests
print("\n" + "="*80)
print("FILE TEST DETAILS (First 5)")
print("="*80)
file_tests = [t for t in all_tests if t.get('type') == 'FILE'][:5]
for t in file_tests:
    print(f"{t.get('test_id')}: Accuracy={t.get('accuracy', 0):.1f}%, "
          f"Semantic={t.get('semantic_similarity', 0):.3f}, "
          f"FactCoverage={t.get('fact_coverage', 0):.3f}")

