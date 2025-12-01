"""Train example ML models used by the pipeline (tiny synthetic models).

This trains a placeholder member-type classifier and saves it under `models/`.
"""
from src.pipeline.ml_models import train_member_type_classifier, train_section_selector


if __name__ == '__main__':
    print('Training member type classifier (synthetic data)...')
    clf = train_member_type_classifier(save=True)
    print('Saved model to models/member_type_clf.pkl')
    print('Training section selector (synthetic data)...')
    sec = train_section_selector(save=True)
    print('Saved model to models/section_selector.pkl')
