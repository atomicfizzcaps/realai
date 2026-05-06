"""Fine-tuning plan builder for RealAI."""

import argparse
import json


def build_finetune_plan(base_model='realai-1.0', dataset_path='realai/datasets/processed/instructions.jsonl', backend='hf'):
    """Return a lightweight fine-tuning plan without starting training."""
    command = {
        'hf': ['python', '-m', 'trl', 'sft', '--model_name', base_model, '--dataset', dataset_path],
        'axolotl': ['axolotl', 'train', 'configs/axolotl.yml'],
    }.get(backend, ['python', 'finetune.py'])
    return {
        'status': 'ready',
        'backend': backend,
        'base_model': base_model,
        'dataset_path': dataset_path,
        'command': command,
        'note': 'Review the generated command and install the matching optional tooling before training.',
    }


def main(argv=None):
    """CLI entrypoint for fine-tuning plan generation."""
    parser = argparse.ArgumentParser(description='Build a fine-tuning plan for RealAI.')
    parser.add_argument('--base-model', default='realai-1.0')
    parser.add_argument('--dataset-path', default='realai/datasets/processed/instructions.jsonl')
    parser.add_argument('--backend', default='hf')
    args = parser.parse_args(argv)
    plan = build_finetune_plan(args.base_model, args.dataset_path, args.backend)
    print(json.dumps(plan, indent=2, sort_keys=True))
    return plan


if __name__ == '__main__':
    main()
