"""ML helpers for the pipeline.

This module provides a tiny example of a member-type classifier trained on
synthetic data so the `engineer_standardize` agent can optionally use a
learned model. The training is intentionally tiny and intended as a placeholder
for a real dataset and model.
"""
import os
import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'member_type_clf.pkl')

def _ensure_model_dir():
    os.makedirs(MODEL_DIR, exist_ok=True)

def train_member_type_classifier(save=True):
    """Train a tiny classifier on synthetic features.

    Features: span, angle_deg
    Labels: 0=beam,1=column,2=brace
    """
    # synthetic samples: beams long/horizontal, columns short/vertical, braces angled
    spans = np.concatenate([np.random.normal(6, 1, 200), np.random.normal(3,0.5,200), np.random.normal(5,1.5,200)])
    angles = np.concatenate([np.random.normal(5,3,200), np.random.normal(85,3,200), np.random.normal(35,5,200)])
    X = np.vstack([spans, angles]).T
    y = np.concatenate([np.zeros(200), np.ones(200), np.full(200,2)])
    clf = DecisionTreeClassifier(max_depth=5)
    clf.fit(X, y)
    if save:
        _ensure_model_dir()
        joblib.dump(clf, MODEL_PATH)
    return clf

def load_member_type_classifier():
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


SECTION_MODEL_PATH = os.path.join(MODEL_DIR, 'section_selector.pkl')


def train_section_selector(save=True):
    """Train a tiny selector that maps (axial_N, moment_Nmm, span_m) -> section index
    This is synthetic and intended as a placeholder. Uses SECTION_CATALOG names from pipeline module.
    """
    # avoid importing pipeline (circular) — define small local catalog
    catalog = [
        {'name': 'W8x10', 'area': 0.013, 'Ixx': 8e-5, 'weight_kg_per_m': 12.0},
        {'name': 'W10x12', 'area': 0.020, 'Ixx': 2.0e-4, 'weight_kg_per_m': 17.0},
        {'name': 'HSS100x100x6', 'area': 0.018, 'Ixx': 1.6e-4, 'weight_kg_per_m': 15.5},
    ]
    # generate synthetic samples: for each section, sample axial and moment demands it can handle
    X_list = []
    y_list = []
    for idx, s in enumerate(catalog):
        # create demands up to ~80% capacity
        axial_cap = s['area'] * 250e6 * 0.6
        moments = np.random.uniform(0, s['Ixx'] * 250e6 * 0.6 * 2.0, 300)
        axials = np.random.uniform(0, axial_cap * 0.8, 300)
        spans = np.random.uniform(1.0, 8.0, 300)
        for a, m, sp in zip(axials, moments, spans):
            X_list.append([a, m, sp])
            y_list.append(idx)
    X = np.array(X_list)
    y = np.array(y_list)
    clf = DecisionTreeClassifier(max_depth=6)
    clf.fit(X, y)
    if save:
        _ensure_model_dir()
        joblib.dump(clf, SECTION_MODEL_PATH)
    return clf


def load_section_selector():
    try:
        return joblib.load(SECTION_MODEL_PATH)
    except Exception:
        return None


MATERIAL_MODEL_PATH = os.path.join(MODEL_DIR, 'material_classifier.pkl')


def train_material_classifier(save=True):
    """Enhanced material classifier training with high-strength materials (Phase 1)

    Features:
    - role_encoded: 0=beam, 1=column, 2=brace, 3=connection_plate, 4=truss_member
    - span_m: member span in meters
    - stress_type: 0=compression, 1=bending, 2=tension, 3=combined, 4=shear
    - seismic_zone: 0=low, 1=moderate, 2=high, 3=very_high
    - environment: 0=enclosed, 1=exposed, 2=weathering

    Labels: Updated for high-strength materials
    0=ASTM A36, 1=ASTM A572 Gr50, 2=ASTM A992, 3=ASTM A913 Gr65, 4=ASTM A572 Gr65,
    5=ASTM A709 Gr70W, 6=Q460, 7=ASTM A852 Gr70

    Engineering logic for optimal material selection:
    - Seismic zones + long spans → ultra-high strength (Q460, A913 Gr65)
    - Exposed/weather conditions → weathering steels (A709 Gr70W)
    - Critical tension members → quenched & tempered (A852 Gr70)
    - Standard applications → cost-effective high-strength (A992, A572 Gr65)
    """
    np.random.seed(42)

    X_list = []
    y_list = []

    # Load training data from JSON file
    try:
        import json
        with open('/Users/sahil/Documents/aibuildx/data/detailing_training_datasets/materials_training.json', 'r') as f:
            training_data = json.load(f)

        # Material mapping for labels - updated for high-strength materials
        material_map = {
            "ASTM A36": 0, "ASTM A572 Gr50": 1, "ASTM A992": 2, "ASTM A913 Gr65": 3,
            "ASTM A572 Gr65": 4, "ASTM A709 Gr70W": 5, "Q460": 6, "ASTM A852 Gr70": 7
        }

        # Role mapping
        role_map = {
            "primary_beam": 0, "column": 1, "diagonal_brace": 2, "connection_plate": 3,
            "truss_member": 4, "secondary_beam": 0, "brace": 2, "cantilever_beam": 0,
            "stadium_roof_beam": 0
        }

        # Stress category mapping
        stress_map = {
            "compression": 0, "bending": 1, "axial": 2, "tension": 2, "combined": 3,
            "shear": 4, "bearing": 4, "bending_compression": 3, "axial_tension": 2
        }

        # Seismic zone mapping
        seismic_map = {"low": 0, "moderate": 1, "high": 2, "very_high": 3}

        # Environment mapping
        env_map = {"enclosed": 0, "exposed": 1, "weathering": 2}

        # Process training data
        for item in training_data:
            role = role_map.get(item["member_role"], 0)
            span = item["span_m"]
            stress = stress_map.get(item["stress_category"], 1)
            seismic = seismic_map.get(item["seismic_zone"], 1)
            env = env_map.get(item["environment"], 0)

            material_idx = material_map.get(item["optimal_material"], 1)  # default to S355

            X_list.append([role, span, stress, seismic, env])
            y_list.append(material_idx)

        logger.info(f"Loaded {len(training_data)} training samples from JSON")

    except Exception as e:
        logger.warning(f"Could not load training data: {e}, using generated samples")

    # Generate additional synthetic training samples for robustness
    for _ in range(500):
        role = np.random.choice([0, 1, 2, 3, 4])
        span = np.random.uniform(2, 50)
        stress = np.random.choice([0, 1, 2, 3, 4])
        seismic = np.random.choice([0, 1, 2, 3])
        env = np.random.choice([0, 1, 2])

        # Intelligent material selection logic
        if seismic >= 2 and span > 20:  # High seismic + long span
            material = np.random.choice([3, 4, 6, 7], p=[0.3, 0.3, 0.2, 0.2])  # Ultra-high strength
        elif env == 2:  # Weathering environment
            material = np.random.choice([5, 2], p=[0.7, 0.3])  # Weathering steels
        elif role == 1 and span > 10:  # Tall columns
            material = np.random.choice([3, 4, 6], p=[0.4, 0.4, 0.2])
        elif stress == 2 and seismic >= 2:  # Tension in seismic
            material = np.random.choice([7, 3], p=[0.6, 0.4])  # Q&T steel
        else:  # Standard cases
            material = np.random.choice([1, 2, 4], p=[0.4, 0.4, 0.2])  # High-strength standards

        X_list.append([role, span, stress, seismic, env])
        y_list.append(material)

    X = np.array(X_list)
    y = np.array(y_list)

    # Train model with enhanced features
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)

    if save:
        os.makedirs(os.path.dirname(MATERIAL_MODEL_PATH), exist_ok=True)
        joblib.dump(model, MATERIAL_MODEL_PATH)
        logger.info(f"Material classifier saved to {MATERIAL_MODEL_PATH}")

    # Log training statistics
    material_names = ["S235", "S355", "ASTM A992", "ASTM A913 Gr65", "ASTM A572 Gr65",
                     "ASTM A709 Gr70W", "Q460", "ASTM A852 Gr70"]
    unique, counts = np.unique(y, return_counts=True)
    for mat_idx, count in zip(unique, counts):
        logger.info(f"Training samples for {material_names[mat_idx]}: {count}")

    return model
    
    if save:
        _ensure_model_dir()
        joblib.dump(clf, MATERIAL_MODEL_PATH)
    
    return clf


def load_material_classifier():
    """Load trained material classifier model."""
    try:
        return joblib.load(MATERIAL_MODEL_PATH)
    except Exception:
        return None
