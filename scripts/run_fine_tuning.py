#!/usr/bin/env python3
"""
Fine-tuning Runner for Llama-3-70B Structural Engineering Model
Uses accumulated training data from the learning vault
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Configuration
    vault_path = Path("./data/training_vault.jsonl")
    model_name = "meta-llama/Meta-Llama-3-70B-Instruct"
    output_dir = Path("./data/fine_tuned_models") / f"llama_3_70b_structural_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Check if training data exists
    if not vault_path.exists():
        logger.error(f"Training vault not found: {vault_path}")
        logger.info("No training data available. Run the application to collect user feedback first.")
        return 1

    # Count training examples
    with open(vault_path, 'r') as f:
        training_examples = [json.loads(line) for line in f if line.strip()]

    if len(training_examples) < 10:
        logger.warning(f"Only {len(training_examples)} training examples found. Minimum recommended: 10")
        logger.info("Continuing with available data...")

    logger.info(f"Found {len(training_examples)} training examples")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare training data in the format expected by transformers
    training_file = output_dir / "training_data.jsonl"

    with open(training_file, 'w') as f:
        for example in training_examples:
            # Format for instruction tuning
            formatted_example = {
                "instruction": example.get("prompt", ""),
                "input": example.get("context", ""),
                "output": example.get("response", "")
            }
            f.write(json.dumps(formatted_example) + '\n')

    logger.info(f"Prepared training data: {training_file}")

    # Fine-tuning configuration
    training_config = {
        "model_name_or_path": model_name,
        "train_file": str(training_file),
        "output_dir": str(output_dir),
        "num_train_epochs": 3,
        "per_device_train_batch_size": 1,  # Very small batch size for 70B model
        "gradient_accumulation_steps": 16,
        "learning_rate": 2e-5,
        "warmup_steps": 100,
        "logging_steps": 10,
        "save_steps": 500,
        "save_total_limit": 2,
        "fp16": True,
        "deepspeed": "ds_config.json",  # DeepSpeed config for memory optimization
        "lora": True,  # Use LoRA for efficient fine-tuning
        "lora_r": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05,
        "lora_target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"]
    }

    # Save training config
    config_file = output_dir / "training_config.json"
    with open(config_file, 'w') as f:
        json.dump(training_config, f, indent=2)

    logger.info(f"Saved training config: {config_file}")

    # Create DeepSpeed config for memory optimization
    deepspeed_config = {
        "fp16": {
            "enabled": True
        },
        "zero_optimization": {
            "stage": 3,
            "offload_optimizer": {
                "device": "cpu",
                "pin_memory": True
            },
            "offload_param": {
                "device": "cpu",
                "pin_memory": True
            },
            "overlap_comm": True,
            "contiguous_gradients": True,
            "reduce_bucket_size": "auto",
            "stage3_prefetch_bucket_size": "auto",
            "stage3_param_persistence_threshold": "auto",
            "sub_group_size": 1e9,
            "stage3_max_live_parameters": 1e9,
            "stage3_max_reuse_distance": 1e9
        },
        "gradient_accumulation_steps": 16,
        "train_micro_batch_size_per_gpu": 1,
        "gradient_clipping": 1.0,
        "steps_per_print": 100
    }

    ds_config_file = output_dir / "ds_config.json"
    with open(ds_config_file, 'w') as f:
        json.dump(deepspeed_config, f, indent=2)

    logger.info(f"Created DeepSpeed config: {ds_config_file}")

    # Run fine-tuning
    logger.info("Starting fine-tuning process...")

    cmd = f"""
python3 -m torch.distributed.launch \
    --nproc_per_node=1 \
    --master_port=12345 \
    fine_tune_llama.py \
    --config_file {config_file}
"""

    logger.info(f"Running command: {cmd}")

    # Note: This would require a separate fine_tune_llama.py script
    # For now, we'll just log the command
    logger.info("Fine-tuning command prepared. To run manually:")
    logger.info(cmd)

    # Mark vault as processed
    processed_vault = vault_path.with_suffix('.processed')
    vault_path.rename(processed_vault)
    logger.info(f"Renamed vault to: {processed_vault}")

    logger.info("Fine-tuning setup complete!")
    logger.info(f"Output directory: {output_dir}")
    logger.info("Run the generated command to start training")

    return 0

if __name__ == "__main__":
    sys.exit(main())