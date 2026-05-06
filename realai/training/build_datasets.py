"""Dataset assembly helpers for the RealAI training pipeline."""

import json
from pathlib import Path

from .extract_from_agent_tools import extract_agent_tool_data


def _count_rows(path):
    with open(path, 'r', encoding='utf-8') as handle:
        return sum(1 for line in handle if line.strip())


def build_dataset_bundle(input_root='realai/datasets/raw', output_root='realai/datasets/processed'):
    """Build all training datasets and return a small manifest."""
    outputs = extract_agent_tool_data(input_root, output_root)
    manifest = {
        'input_root': str(Path(input_root)),
        'output_root': str(Path(output_root)),
        'datasets': {},
    }
    for name, path in outputs.items():
        manifest['datasets'][name] = {
            'path': path,
            'rows': _count_rows(path),
        }
    return manifest


def main(argv=None):
    """CLI entrypoint for dataset assembly."""
    manifest = build_dataset_bundle()
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return manifest


if __name__ == '__main__':
    main()
