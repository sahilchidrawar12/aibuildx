import json
import os
from pathlib import Path
from typing import Dict, Optional

from .llm_orchestrator import LLMFineTuner
from ..utils.logging_setup import get_logger

logger = get_logger('llm_training_vault')


class LLMTrainingDataVault:
    """Stores user decisions for continuous fine-tuning."""

    def __init__(self, vault_path: Optional[str] = None, trigger_threshold: int = 10):
        self.vault_path = Path(vault_path or os.getenv('LLM_TRAINING_VAULT', str(Path(__file__).parent.parent.parent / 'data' / 'llm_training_data_vault.jsonl')))
        self.trigger_threshold = trigger_threshold
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        self.trigger_manifest = self.vault_path.with_name('llm_training_triggered.json')

    def append_example(self, example: Dict[str, any]) -> None:
        try:
            with self.vault_path.open('a', encoding='utf-8') as fh:
                fh.write(json.dumps(example) + '\n')
            logger.info('Appended training example to vault: %s', self.vault_path)
        except Exception as exc:
            logger.warning('Unable to append training example: %s', exc)

    def count_examples(self) -> int:
        if not self.vault_path.exists():
            return 0
        try:
            with self.vault_path.open('r', encoding='utf-8') as fh:
                return sum(1 for _ in fh)
        except Exception as exc:
            logger.warning('Unable to count training examples: %s', exc)
            return 0

    def should_trigger_fine_tune(self) -> bool:
        if self._triggered():
            return False
        return self.count_examples() >= self.trigger_threshold

    def _triggered(self) -> bool:
        return self.trigger_manifest.exists()

    def mark_triggered(self, details: Optional[Dict[str, any]] = None) -> None:
        try:
            with self.trigger_manifest.open('w', encoding='utf-8') as fh:
                json.dump(details or {'triggered': True, 'timestamp': str(Path.cwd())}, fh, indent=2)
        except Exception as exc:
            logger.warning('Unable to write fine-tune trigger manifest: %s', exc)

    def trigger_fine_tuning(self, backend: str, model_name: Optional[str] = None) -> Dict[str, str]:
        trainer = LLMFineTuner(training_file=str(self.vault_path), backend=backend, model_name=model_name)
        result = trainer.trigger()
        if result.get('status') == 'ok':
            self.mark_triggered(result)
        return result
