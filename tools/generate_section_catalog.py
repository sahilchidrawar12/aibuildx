#!/usr/bin/env python3
"""Generate an expanded synthetic section catalog CSV from a seed CSV.
Usage:
    python tools/generate_section_catalog.py --seed data/section_catalog.csv --out data/section_catalog_full.csv --mult 5
"""
import csv
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('--seed', default='data/section_catalog.csv')
parser.add_argument('--out', default='data/section_catalog_full.csv')
parser.add_argument('--mult', type=int, default=5)
args = parser.parse_args()

rows = []
with open(args.seed, newline='') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

if not rows:
    raise SystemExit('Seed CSV empty or not found')

fields = reader.fieldnames
with open(args.out, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for _ in range(args.mult):
        for r in rows:
            nr = r.copy()
            # mutate dimensions slightly
            if 'depth_mm' in r and r['depth_mm'].isdigit():
                d = int(r['depth_mm'])
                d = max(10, int(d * random.uniform(0.9, 1.1)))
                nr['depth_mm'] = str(d)
            if 'width_mm' in r and r['width_mm'].isdigit():
                w = int(r['width_mm'])
                w = max(10, int(w * random.uniform(0.9, 1.1)))
                nr['width_mm'] = str(w)
            writer.writerow(nr)

print('Wrote', args.out)
