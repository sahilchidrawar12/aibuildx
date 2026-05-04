#!/usr/bin/env python3
"""
Phase 1 Material Classifier Test Script
Tests the enhanced material selection with high-strength materials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pipeline.material_classifier import classify_material
from src.pipeline.profile_db import MATERIAL_CATALOG

def test_material_classifier():
    """Test the Phase 1 material classifier implementation."""

    # Test entities for different scenarios
    test_entities = [
        {'id': 'beam1', 'role': 'primary_beam', 'span': 15.0, 'stress_type': 'bending', 'seismic_zone': 'high', 'environment': 'exposed'},
        {'id': 'column1', 'role': 'column', 'span': 5.0, 'stress_type': 'compression', 'seismic_zone': 'moderate', 'environment': 'enclosed'},
        {'id': 'brace1', 'role': 'diagonal_brace', 'span': 20.0, 'stress_type': 'tension', 'seismic_zone': 'very_high', 'environment': 'weathering'}
    ]

    print('Testing Phase 1 Material Classifier with High-Strength Materials:')
    print('=' * 60)

    for entity in test_entities:
        try:
            material = classify_material(entity)
            print(f'Entity: {entity["id"]} ({entity["role"]})')
            print(f'  Conditions: span={entity.get("span", "N/A")}, seismic={entity.get("seismic_zone", "N/A")}, env={entity.get("environment", "N/A")}')
            print(f'  Selected Material: {material["name"]} (Yield: {material.get("yield_strength", "N/A")})')
            print()
        except Exception as e:
            print(f'Error testing entity {entity["id"]}: {e}')
            print()

    print('Available Materials in Catalog:')
    for name, props in MATERIAL_CATALOG.items():
        print(f'  {name}: Yield={props.get("yield_strength", "N/A")}, Ultimate={props.get("ultimate_strength", "N/A")}')

if __name__ == '__main__':
    test_material_classifier()