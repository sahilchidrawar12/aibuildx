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
