#!/usr/bin/env python3
"""
Advanced Model Training Framework
Prepares and configures 5 specialized models for 300k+ dataset
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# TRAINING DATA PREPARATION
# ============================================================================

class TrainingDataPreparator:
    """Prepares data for model training"""
    
    def __init__(self, data_dir: str = "data/datasets_100_percent"):
        self.data_dir = Path(data_dir)
        self.logger = logger
        self.training_splits = {}
    
    def load_all_datasets(self) -> Dict:
        """Load all datasets"""
        self.logger.info("Loading all datasets...")
        
        datasets = {}
        
        if (self.data_dir / "connections_50k.json").exists():
            with open(self.data_dir / "connections_50k.json") as f:
                datasets['connections'] = json.load(f)
        
        if (self.data_dir / "steel_sections_1800.json").exists():
            with open(self.data_dir / "steel_sections_1800.json") as f:
                datasets['sections'] = json.load(f)
        
        if (self.data_dir / "design_decisions_100k.json").exists():
            with open(self.data_dir / "design_decisions_100k.json") as f:
                datasets['decisions'] = json.load(f)
        
        if (self.data_dir / "clashes_100k.json").exists():
            with open(self.data_dir / "clashes_100k.json") as f:
                datasets['clashes'] = json.load(f)
        
        if (self.data_dir / "compliance_cases_1000.json").exists():
            with open(self.data_dir / "compliance_cases_1000.json") as f:
                datasets['compliance'] = json.load(f)
        
        if (self.data_dir / "fea_benchmarks_50k.json").exists():
            with open(self.data_dir / "fea_benchmarks_50k.json") as f:
                datasets['benchmarks'] = json.load(f)
        
        total = sum(len(v) for v in datasets.values())
        self.logger.info(f"✓ Loaded {len(datasets)} datasets with {total:,} total entries")
        
        return datasets
    
    def create_train_val_test_splits(self, data: List, train_ratio: float = 0.7, 
                                    val_ratio: float = 0.15) -> Tuple[List, List, List]:
        """Create train/validation/test splits"""
        
        n = len(data)
        train_size = int(n * train_ratio)
        val_size = int(n * val_ratio)
        
        train = data[:train_size]
        val = data[train_size:train_size + val_size]
        test = data[train_size + val_size:]
        
        return train, val, test
    
    def prepare_connection_data(self, connections: List) -> Dict:
        """Prepare connection data for training"""
        self.logger.info("Preparing connection training data...")
        
        train, val, test = self.create_train_val_test_splits(connections)
        
        split_info = {
            "dataset": "connections",
            "total_entries": len(connections),
            "train_size": len(train),
            "val_size": len(val),
            "test_size": len(test),
            "features": [
                "connection_type", "bolt_grade", "bolt_diameter", 
                "bolt_count", "capacity_kips", "slip_critical"
            ],
            "target": "connection_type",
            "classes": len(set(c.get('connection_type') for c in connections))
        }
        
        self.logger.info(f"  ✓ Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        return split_info
    
    def prepare_section_data(self, sections: List) -> Dict:
        """Prepare section data for training"""
        self.logger.info("Preparing section training data...")
        
        train, val, test = self.create_train_val_test_splits(sections)
        
        split_info = {
            "dataset": "sections",
            "total_entries": len(sections),
            "train_size": len(train),
            "val_size": len(val),
            "test_size": len(test),
            "features": [
                "depth", "width", "area", "weight", "ix", "iy"
            ],
            "target": "profile",
            "regression_targets": ["area", "weight", "ix", "iy"]
        }
        
        self.logger.info(f"  ✓ Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        return split_info
    
    def prepare_decision_data(self, decisions: List) -> Dict:
        """Prepare decision data for training"""
        self.logger.info("Preparing decision training data...")
        
        train, val, test = self.create_train_val_test_splits(decisions)
        
        split_info = {
            "dataset": "decisions",
            "total_entries": len(decisions),
            "train_size": len(train),
            "val_size": len(val),
            "test_size": len(test),
            "features": [
                "member_type", "span_feet", "tributary_load_psf",
                "project_year", "engineer_experience_years"
            ],
            "target": "selected_section",
            "reasons": list(set(d.get('selection_reason') for d in decisions))
        }
        
        self.logger.info(f"  ✓ Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        return split_info
    
    def prepare_clash_data(self, clashes: List) -> Dict:
        """Prepare clash data for training"""
        self.logger.info("Preparing clash training data...")
        
        train, val, test = self.create_train_val_test_splits(clashes)
        
        split_info = {
            "dataset": "clashes",
            "total_entries": len(clashes),
            "train_size": len(train),
            "val_size": len(val),
            "test_size": len(test),
            "features": [
                "member1_type", "member2_type", "minimum_distance_mm",
                "clash_type", "detected_in_phase"
            ],
            "target": "severity",
            "classes": list(set(c.get('severity') for c in clashes))
        }
        
        self.logger.info(f"  ✓ Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        return split_info
    
    def prepare_compliance_data(self, compliance: List) -> Dict:
        """Prepare compliance data for training"""
        self.logger.info("Preparing compliance training data...")
        
        train, val, test = self.create_train_val_test_splits(compliance)
        
        split_info = {
            "dataset": "compliance",
            "total_entries": len(compliance),
            "train_size": len(train),
            "val_size": len(val),
            "test_size": len(test),
            "features": [
                "code", "topic", "fy_ksi", "calculated_value",
                "limit_value", "utilization_ratio"
            ],
            "target": "passes",
            "positive_class_ratio": sum(1 for c in compliance if c.get('passes')) / len(compliance)
        }
        
        self.logger.info(f"  ✓ Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        return split_info
    
    def save_training_config(self, all_splits: Dict):
        """Save training configuration"""
        config = {
            "timestamp": datetime.now().isoformat(),
            "total_entries": sum(s.get('total_entries', 0) for s in all_splits.values()),
            "datasets_ready": len(all_splits),
            "splits": all_splits,
            "training_recommendations": {
                "connection_designer": {
                    "model_type": "CNN + Multi-head Attention",
                    "batch_size": 32,
                    "epochs": 50,
                    "learning_rate": 0.001,
                    "target_accuracy": 0.98
                },
                "section_optimizer": {
                    "model_type": "XGBoost + LightGBM Ensemble",
                    "batch_size": 64,
                    "iterations": 100,
                    "learning_rate": 0.1,
                    "target_accuracy": 0.97
                },
                "clash_detector": {
                    "model_type": "3D CNN + LSTM",
                    "batch_size": 16,
                    "epochs": 100,
                    "learning_rate": 0.0005,
                    "target_accuracy": 0.99
                },
                "compliance_checker": {
                    "model_type": "BERT + Rule Engine",
                    "batch_size": 32,
                    "epochs": 50,
                    "learning_rate": 0.00005,
                    "target_accuracy": 1.0
                },
                "risk_analyzer": {
                    "model_type": "Ensemble (RF + GB + SVM)",
                    "n_estimators": 500,
                    "max_depth": 10,
                    "target_accuracy": 0.95
                }
            }
        }
        
        output_path = self.data_dir / "training_configuration.json"
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"\n✓ Training configuration saved: {output_path}")
        return config

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class FeatureEngineer:
    """Extracts and engineers features from raw data"""
    
    def __init__(self):
        self.logger = logger
    
    def engineer_connection_features(self, connections: List) -> np.ndarray:
        """Engineer features from connection data"""
        self.logger.info("Engineering connection features...")
        
        features = []
        for conn in connections[:1000]:  # Sample for demonstration
            feat = [
                conn.get('bolt_diameter', 0),
                conn.get('bolt_count', 0),
                conn.get('capacity_kips', 0) / 1000,  # Scale to thousands
                1 if conn.get('slip_critical') else 0,
                1 if conn.get('prying_action') else 0
            ]
            features.append(feat)
        
        features_array = np.array(features, dtype=np.float32)
        self.logger.info(f"  ✓ Engineered {len(features)} connection feature vectors")
        return features_array
    
    def engineer_section_features(self, sections: List) -> np.ndarray:
        """Engineer features from section data"""
        self.logger.info("Engineering section features...")
        
        features = []
        for sect in sections[:1000]:
            feat = [
                sect.get('depth', 0),
                sect.get('width', 0),
                sect.get('area', 0),
                sect.get('weight', 0),
                sect.get('ix', 0) / 1000,  # Scale
                sect.get('iy', 0) / 1000
            ]
            features.append(feat)
        
        features_array = np.array(features, dtype=np.float32)
        self.logger.info(f"  ✓ Engineered {len(features)} section feature vectors")
        return features_array
    
    def engineer_clash_features(self, clashes: List) -> np.ndarray:
        """Engineer features from clash data"""
        self.logger.info("Engineering clash features...")
        
        features = []
        for clash in clashes[:1000]:
            distance = clash.get('minimum_distance_mm', 0)
            cost = clash.get('cost_impact_usd', 0)
            feat = [
                distance,
                cost / 1000,  # Scale
                clash.get('time_to_resolve_hours', 0),
                1 if clash.get('detected_by_ai') else 0
            ]
            features.append(feat)
        
        features_array = np.array(features, dtype=np.float32)
        self.logger.info(f"  ✓ Engineered {len(features)} clash feature vectors")
        return features_array

# ============================================================================
# MODEL TRAINING ORCHESTRATION
# ============================================================================

class ModelTrainingOrchestrator:
    """Orchestrates training of all 5 models"""
    
    def __init__(self, data_dir: str = "data/datasets_100_percent"):
        self.data_dir = data_dir
        self.logger = logger
        self.preparator = TrainingDataPreparator(data_dir)
        self.engineer = FeatureEngineer()
        self.training_report = {
            "timestamp": datetime.now().isoformat(),
            "total_entries_used": 0,
            "models": {}
        }
    
    def orchestrate_training(self) -> Dict:
        """Orchestrate complete training pipeline"""
        
        self.logger.info("="*80)
        self.logger.info("ADVANCED MODEL TRAINING ORCHESTRATION")
        self.logger.info("="*80)
        
        # Load data
        datasets = self.preparator.load_all_datasets()
        
        # Prepare training data for each model
        all_splits = {}
        
        if 'connections' in datasets:
            all_splits['connection_designer'] = self.preparator.prepare_connection_data(
                datasets['connections']
            )
        
        if 'sections' in datasets:
            all_splits['section_optimizer'] = self.preparator.prepare_section_data(
                datasets['sections']
            )
        
        if 'decisions' in datasets:
            all_splits['section_optimizer_decisions'] = self.preparator.prepare_decision_data(
                datasets['decisions']
            )
        
        if 'clashes' in datasets:
            all_splits['clash_detector'] = self.preparator.prepare_clash_data(
                datasets['clashes']
            )
        
        if 'compliance' in datasets:
            all_splits['compliance_checker'] = self.preparator.prepare_compliance_data(
                datasets['compliance']
            )
        
        # Save configuration
        config = self.preparator.save_training_config(all_splits)
        
        # Engineer features
        self.logger.info("\n" + "-"*80)
        self.logger.info("FEATURE ENGINEERING")
        self.logger.info("-"*80 + "\n")
        
        if 'connections' in datasets:
            conn_features = self.engineer.engineer_connection_features(datasets['connections'])
            self.training_report['models']['connection_designer'] = {
                "feature_vectors": conn_features.shape[0],
                "feature_dimension": conn_features.shape[1],
                "data_type": "float32"
            }
        
        if 'sections' in datasets:
            sect_features = self.engineer.engineer_section_features(datasets['sections'])
            self.training_report['models']['section_optimizer'] = {
                "feature_vectors": sect_features.shape[0],
                "feature_dimension": sect_features.shape[1],
                "data_type": "float32"
            }
        
        if 'clashes' in datasets:
            clash_features = self.engineer.engineer_clash_features(datasets['clashes'])
            self.training_report['models']['clash_detector'] = {
                "feature_vectors": clash_features.shape[0],
                "feature_dimension": clash_features.shape[1],
                "data_type": "float32"
            }
        
        # Print summary
        self.logger.info("\n" + "="*80)
        self.logger.info("TRAINING ORCHESTRATION COMPLETE")
        self.logger.info("="*80)
        
        self.logger.info(f"\nDatasets prepared: {len(all_splits)}")
        self.logger.info(f"Total entries: {config['total_entries']:,}")
        
        self.logger.info("\nModels ready for training:")
        for model_name, split in all_splits.items():
            self.logger.info(f"  • {model_name}")
            self.logger.info(f"    - Train: {split['train_size']:,}")
            self.logger.info(f"    - Val: {split['val_size']:,}")
            self.logger.info(f"    - Test: {split['test_size']:,}")
        
        self.training_report['total_entries_used'] = config['total_entries']
        
        return self.training_report
    
    def save_report(self):
        """Save training report"""
        output_path = Path(self.data_dir) / "training_orchestration_report.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.training_report, f, indent=2)
        
        self.logger.info(f"\n✓ Training report saved: {output_path}")

# ============================================================================

def main():
    """Main training orchestration"""
    
    orchestrator = ModelTrainingOrchestrator()
    report = orchestrator.orchestrate_training()
    orchestrator.save_report()
    
    print("\n" + "="*80)
    print("✓ ALL TRAINING DATA PREPARED")
    print("✓ MODELS READY FOR TRAINING ON GPU")
    print("="*80)

if __name__ == "__main__":
    main()
