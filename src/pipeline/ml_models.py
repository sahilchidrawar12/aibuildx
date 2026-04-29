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
    """Train material classifier that maps (role, span_m, stress_type) -> material grade
    
    Features:
    - role_encoded: 0=beam, 1=column, 2=brace
    - span_m: member span in meters
    - stress_type: 0=compression, 1=bending, 2=tension, 3=combined
    
    Labels: 0=S235, 1=S355, 2=S450, 3=S460, 4=S275
    
    Engineering logic:
    - Long spans (>12m) → higher grades (S355, S450)
    - Columns under compression → S355, S450 for heavy loads
    - Braces under tension → S355 typical, S450 for critical
    - Beams bending → S355 for long spans, S235 for short
    - Short members (<5m) → S235 or S275 sufficient
    """
    np.random.seed(42)
    
    X_list = []
    y_list = []
    
    # Generate training samples based on engineering best practices
    
    # 1. BEAMS (role=0)
    for _ in range(300):
        span = np.random.uniform(3, 20)
        stress_type = 1  # bending
        if span < 6:
            # Short beams: S235 (60%), S275 (40%)
            material = np.random.choice([0, 4], p=[0.6, 0.4])
        elif span < 12:
            # Medium beams: S275 (30%), S355 (70%)
            material = np.random.choice([4, 1], p=[0.3, 0.7])
        else:
            # Long beams: S355 (70%), S450 (30%)
            material = np.random.choice([1, 2], p=[0.7, 0.3])
        X_list.append([0, span, stress_type])
        y_list.append(material)
    
    # 2. COLUMNS (role=1)
    for _ in range(300):
        span = np.random.uniform(2, 15)  # height
        stress_type = 0  # compression
        if span < 5:
            # Short columns: S275 (40%), S355 (60%)
            material = np.random.choice([4, 1], p=[0.4, 0.6])
        elif span < 10:
            # Medium columns: S355 (70%), S450 (30%)
            material = np.random.choice([1, 2], p=[0.7, 0.3])
        else:
            # Tall columns: S450 (60%), S460 (40%)
            material = np.random.choice([2, 3], p=[0.6, 0.4])
        X_list.append([1, span, stress_type])
        y_list.append(material)
    
    # 3. BRACES (role=2)
    for _ in range(300):
        span = np.random.uniform(2, 25)
        stress_type = np.random.choice([2, 3])  # tension or combined
        if span < 8:
            # Short braces: S235 (30%), S275 (30%), S355 (40%)
            material = np.random.choice([0, 4, 1], p=[0.3, 0.3, 0.4])
        elif span < 15:
            # Medium braces: S355 (80%), S450 (20%)
            material = np.random.choice([1, 2], p=[0.8, 0.2])
        else:
            # Long braces: S450 (60%), S460 (40%)
            material = np.random.choice([2, 3], p=[0.6, 0.4])
        X_list.append([2, span, stress_type])
        y_list.append(material)
    
    X = np.array(X_list)
    y = np.array(y_list)
    
    clf = DecisionTreeClassifier(max_depth=8, min_samples_split=10)
    clf.fit(X, y)
    
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
