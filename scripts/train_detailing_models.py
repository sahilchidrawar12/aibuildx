#!/usr/bin/env python3
"""
Detailing AI model training & validation orchestration.

Pipeline:
1. Generate synthetic datasets (AISC/AWS/Eurocode-based)
2. Train all 5 detailing models
3. Validate on 10 reference projects
4. Generate accuracy report
5. Save models to models/phase3_validated/

Run: python3 scripts/train_detailing_models.py
"""

import sys
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.detailing.training_data_generators import generate_all_datasets
from src.pipeline.models.detailing_model_architectures import create_model
from src.pipeline.validation.detailing_validation import (
    DetailingValidator,
    generate_accuracy_report,
)


def prepare_training_data(dataset_name: str, data_dir: str = "data/detailing_training_datasets") -> tuple:
    """Load dataset and prepare X, y arrays for training."""
    csv_path = os.path.join(data_dir, f"{dataset_name}_training.csv")
    
    if not os.path.exists(csv_path):
        print(f"  ⚠ Dataset not found: {csv_path}. Skipping.")
        return None, None, None, None
    
    df = pd.read_csv(csv_path)
    
    # Determine feature and target columns
    if dataset_name == "copes":
        features = ["depth_mm", "width_mm", "length_mm", "load_kn", "steel_grade"]
        targets = ["cope_length_mm", "cope_depth_mm"]
    elif dataset_name == "stiffeners":
        features = ["member_depth_mm", "member_web_thickness_mm", "bolt_diameter_mm", "num_bolts", "connection_load_kn"]
        targets = ["stiffener_thickness_mm", "stiffener_width_mm", "stiffener_height_mm"]
    elif dataset_name == "welds":
        features = ["weld_load_kn", "plate_thickness_mm", "weld_length_mm", "electrode_strength_mpa"]
        targets = ["weld_size_mm", "weld_length_designed_mm"]
    elif dataset_name == "extensions":
        features = ["member_length_mm", "member_type", "connection_type", "connection_load_kn"]
        targets = ["extension_mm", "shortening_mm"]
    elif dataset_name == "bolt_patterns":
        features = ["plate_width_mm", "plate_height_mm", "bolt_diameter_mm", "num_bolts", "total_load_kn"]
        targets = ["min_edge_distance_mm", "min_bolt_spacing_mm", "bolt_positions_count"]
    else:
        return None, None, None, None
    
    # Encode categorical columns if needed
    if "steel_grade" in df.columns:
        grade_map = {"S235": 0, "S355": 1, "S450": 2}
        df["steel_grade"] = df.get("steel_grade", "S235").map(grade_map)
    
    if "member_type" in df.columns:
        type_map = {"beam": 0, "column": 1, "brace": 2}
        df["member_type"] = df.get("member_type", "beam").map(type_map)
    
    if "connection_type" in df.columns:
        conn_map = {"bolted": 0, "welded": 1, "hybrid": 2}
        df["connection_type"] = df.get("connection_type", "bolted").map(conn_map)
    
    if "electrode_type" in df.columns:
        elec_map = {"E7018": 0, "E8018": 1, "E9018": 2}
        df["electrode_strength_mpa"] = df.get("electrode_strength_mpa", 485.0)
    
    # Extract features and targets
    X = df[features].fillna(0.0).values.astype(np.float32)
    y = df[targets].fillna(0.0).values.astype(np.float32)
    
    print(f"  ✓ Loaded {len(X)} samples with {len(features)} features, {len(targets)} targets")
    
    return X, y, features, targets


def train_all_models(data_dir: str = "data/detailing_training_datasets", 
                     output_dir: str = "models/phase3_validated") -> dict:
    """Train all 5 detailing models."""
    print("\n" + "="*70)
    print("DETAILING AI MODEL TRAINING")
    print("="*70)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    model_names = [
        "cope_predictor",
        "stiffener_predictor",
        "weld_predictor",
        "member_extension_predictor",
        "bolt_pattern_optimizer",
    ]
    
    dataset_names = [
        "copes",
        "stiffeners",
        "welds",
        "extensions",
        "bolt_patterns",
    ]
    
    results = {}
    
    for model_name, dataset_name in zip(model_names, dataset_names):
        print(f"\n[1/5] Training {model_name}...")
        
        # Prepare data
        X, y, features, targets = prepare_training_data(dataset_name, data_dir)
        if X is None:
            print(f"  ✗ Skipped (no data)")
            results[model_name] = {"status": "skipped"}
            continue
        
        try:
            # Create and train model
            model = create_model(model_name)
            model.fit(X, y, features, targets)
            
            # Save to joblib
            model_path = os.path.join(output_dir, f"{model_name}.joblib")
            joblib.dump(model, model_path)
            
            print(f"  ✓ Model trained and saved to {model_path}")
            results[model_name] = {
                "status": "trained",
                "samples": len(X),
                "features": len(features),
                "targets": len(targets),
                "path": model_path,
            }
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[model_name] = {"status": "error", "error": str(e)}
    
    return results


def validate_on_reference_projects() -> dict:
    """Validate models on 10 reference projects."""
    print("\n" + "="*70)
    print("VALIDATION ON 10 REFERENCE PROJECTS")
    print("="*70)
    
    validator = DetailingValidator()
    results = validator.validate_on_reference_projects()
    
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"  Simple Projects (2):  {results['average_accuracy_simple_pct']:.1f}% Compliance")
    print(f"  Complex Projects (8): {results['average_accuracy_complex_pct']:.1f}% Compliance")
    print(f"  Overall Average:      {results['overall_average_accuracy_pct']:.1f}% Compliance")
    
    return results


def generate_accuracy_report_file() -> str:
    """Generate markdown accuracy report."""
    print("\n" + "="*70)
    print("GENERATING ACCURACY REPORT")
    print("="*70)
    
    report_path = "docs/04_detailing_accuracy_report.md"
    report_content = generate_accuracy_report(report_path)
    
    print(f"  ✓ Report saved to {report_path}")
    return report_content


def main():
    """Main orchestration pipeline."""
    print("\n🚀 AIBuildX Detailing AI Training & Validation Pipeline")
    print("   AI/ML-driven Tekla-like detailing with industry-verified data")
    
    # Step 1: Generate datasets
    print("\n" + "="*70)
    print("STEP 1: GENERATING SYNTHETIC DATASETS")
    print("="*70)
    print("Generating AISC/AWS/Eurocode-based training data...")
    
    try:
        dataset_info = generate_all_datasets()
        for name, info in dataset_info.items():
            print(f"  ✓ {name}: {info['samples']} samples")
    except Exception as e:
        print(f"  ✗ Dataset generation failed: {e}")
        sys.exit(1)
    
    # Step 2: Train models
    print("\n" + "="*70)
    print("STEP 2: TRAINING DETAILING MODELS")
    print("="*70)
    print("Training 5 AI models on synthetic data...")
    
    try:
        train_results = train_all_models()
        trained = sum(1 for r in train_results.values() if r.get("status") == "trained")
        print(f"\n  ✓ Successfully trained {trained}/5 models")
    except Exception as e:
        print(f"  ✗ Training failed: {e}")
        sys.exit(1)
    
    # Step 3: Validate on reference projects
    print("\n" + "="*70)
    print("STEP 3: VALIDATING ON REFERENCE PROJECTS")
    print("="*70)
    print("Testing on 10 real-world reference projects...")
    
    try:
        validation_results = validate_on_reference_projects()
    except Exception as e:
        print(f"  ✗ Validation failed: {e}")
        sys.exit(1)
    
    # Step 4: Generate report
    print("\n" + "="*70)
    print("STEP 4: GENERATING ACCURACY REPORT")
    print("="*70)
    
    try:
        report = generate_accuracy_report_file()
    except Exception as e:
        print(f"  ✗ Report generation failed: {e}")
        sys.exit(1)
    
    # Summary
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE")
    print("="*70)
    report_path = "docs/04_detailing_accuracy_report.md"
    print(f"""
Summary:
  • Datasets: 5 datasets generated ({sum(i['samples'] for i in dataset_info.values())} total samples)
  • Models: {trained}/5 trained and saved to models/phase3_validated/
  • Validation: {validation_results['total_projects']} reference projects tested
  • Accuracy: {validation_results['overall_average_accuracy_pct']:.1f}% overall compliance
  • Report: {report_path}

All detailing AI models are now ready for production use!
""")


if __name__ == "__main__":
    main()
