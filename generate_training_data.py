#!/usr/bin/env python3
"""
Generate and save 100K+ training dataset for connection design ML models
"""

import json
import sys
import os
sys.path.insert(0, '/Users/sahil/Documents/aibuildx')

from src.pipeline.production_connection_designer import ConnectionTrainingDataGenerator

print("\n" + "="*70)
print("GENERATING 100K TRAINING DATASET FOR CONNECTION DESIGN")
print("="*70)

# Generate dataset
dataset = ConnectionTrainingDataGenerator.generate_dataset(100000)

# Save to JSON
output_path = '/Users/sahil/Documents/aibuildx/data/connection_training_data_100k.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

print(f"\nSaving to: {output_path}")
with open(output_path, 'w') as f:
    json.dump(dataset, f, indent=0)

print(f"✓ Saved {len(dataset)} training samples")
print(f"✓ File size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")

# Print statistics
print("\n" + "-"*70)
print("DATASET STATISTICS")
print("-"*70)

# Count by connection type
connection_types = {}
for sample in dataset:
    ct = sample['connection_type']
    connection_types[ct] = connection_types.get(ct, 0) + 1

print("\nConnection Types Distribution:")
for ct, count in sorted(connection_types.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(dataset)) * 100
    print(f"  {ct:.<40} {count:>6} ({pct:>5.1f}%)")

# Bolt grades
bolt_grades = {}
for sample in dataset:
    bg = sample['connection_design'].get('bolt_grade')
    bolt_grades[bg] = bolt_grades.get(bg, 0) + 1

print("\nBolt Grades Distribution:")
for bg, count in sorted(bolt_grades.items(), key=lambda x: x[1], reverse=True):
    pct = (count / len(dataset)) * 100
    print(f"  {bg:.<40} {count:>6} ({pct:>5.1f}%)")

# Feasibility
feasible = sum(1 for s in dataset if s['feasibility']['is_feasible'])
unfeasible = len(dataset) - feasible
print(f"\nFeasibility:")
print(f"  Feasible designs:      {feasible:>6} ({feasible/len(dataset)*100:>5.1f}%)")
print(f"  Unfeasible designs:    {unfeasible:>6} ({unfeasible/len(dataset)*100:>5.1f}%)")

# Load ranges
shear_loads = [s['design_loads']['shear_kn'] for s in dataset]
tension_loads = [s['design_loads']['tension_kn'] for s in dataset]
moment_loads = [s['design_loads']['moment_knm'] for s in dataset]

print(f"\nLoad Ranges:")
print(f"  Shear:     {min(shear_loads):>8.1f} - {max(shear_loads):>8.1f} kN")
print(f"  Tension:   {min(tension_loads):>8.1f} - {max(tension_loads):>8.1f} kN")
print(f"  Moment:    {min(moment_loads):>8.1f} - {max(moment_loads):>8.1f} kN·m")

print("\n" + "="*70)
print("✓ TRAINING DATASET READY FOR ML MODEL TRAINING")
print("="*70 + "\n")
