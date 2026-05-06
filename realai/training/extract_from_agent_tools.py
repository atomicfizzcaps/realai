"""Extract supervised training datasets from agent-tool artifacts."""

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, List

_DATASET_FILENAMES = {
    'instructions': 'instructions.jsonl',
    'code_pairs': 'code_pairs.jsonl',
    'memory_pairs': 'memory_pairs.jsonl',
}


def _load_json_records(path):
    suffix = path.suffix.lower()
    if suffix == '.jsonl':
        records = []
        with path.open('r', encoding='utf-8') as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
        return records
    if suffix == '.json':
        with path.open('r', encoding='utf-8') as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            return payload
        return [payload]
    if suffix in ('.patch', '.diff', '.txt'):
        return [{'content': path.read_text(encoding='utf-8')}]
    return []


def _collect_records(input_root):
    categories = {
        'logs': [],
        'memory': [],
        'traces': [],
        'diffs': [],
    }
    patterns = {
        'logs': ('**/*log*.json', '**/*log*.jsonl'),
        'memory': ('**/*memory*.json', '**/*memory*.jsonl'),
        'traces': ('**/*trace*.json', '**/*trace*.jsonl'),
        'diffs': ('**/*.diff', '**/*.patch', '**/*diff*.txt'),
    }
    for category, globs in patterns.items():
        for pattern in globs:
            for path in sorted(input_root.glob(pattern)):
                categories[category].extend(_load_json_records(path))
    return categories


def _instruction_examples(records):
    examples = []
    for item in records.get('logs', []) + records.get('traces', []):
        prompt = item.get('prompt') or item.get('task') or item.get('query') or item.get('input')
        response = item.get('response') or item.get('output') or item.get('result')
        if not prompt or not response:
            continue
        examples.append({
            'messages': [
                {'role': 'user', 'content': str(prompt)},
                {'role': 'assistant', 'content': str(response)},
            ],
            'source': item.get('source', 'agent-tools'),
        })
    return examples


def _code_examples(records):
    examples = []
    for item in records.get('diffs', []):
        diff_text = item.get('content', '').strip()
        if not diff_text:
            continue
        examples.append({
            'instruction': 'Apply the following code change faithfully.',
            'input': diff_text,
            'output': diff_text,
            'source': 'code-diff',
        })
    return examples


def _memory_examples(records):
    examples = []
    for item in records.get('memory', []):
        raw_content = item.get('content') or item.get('memory') or item.get('summary') or item.get('input')
        summary = item.get('summary') or item.get('output') or item.get('result')
        if not raw_content or not summary:
            continue
        examples.append({
            'input': str(raw_content),
            'summary': str(summary),
            'source': item.get('source', 'memory'),
        })
    return examples


def _write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + '\n')


def extract_agent_tool_data(input_root, output_root):
    """Extract dataset files from agent-tool exports.

    Args:
        input_root: Directory containing logs, traces, memories, and diffs.
        output_root: Directory that will receive processed JSONL files.

    Returns:
        Dict[str, str]: Mapping of dataset name to file path.
    """
    input_root = Path(input_root)
    output_root = Path(output_root)
    records = _collect_records(input_root)

    instructions = _instruction_examples(records)
    code_pairs = _code_examples(records)
    memory_pairs = _memory_examples(records)

    outputs = {
        'instructions': output_root / _DATASET_FILENAMES['instructions'],
        'code_pairs': output_root / _DATASET_FILENAMES['code_pairs'],
        'memory_pairs': output_root / _DATASET_FILENAMES['memory_pairs'],
    }
    _write_jsonl(outputs['instructions'], instructions)
    _write_jsonl(outputs['code_pairs'], code_pairs)
    _write_jsonl(outputs['memory_pairs'], memory_pairs)
    return dict((name, str(path)) for name, path in outputs.items())


def main(argv=None):
    """CLI entrypoint for dataset extraction."""
    parser = argparse.ArgumentParser(description='Extract training datasets from agent-tool artifacts.')
    parser.add_argument('--input-root', default='realai/datasets/raw', help='Directory containing raw exports.')
    parser.add_argument('--output-root', default='realai/datasets/processed', help='Directory for processed JSONL datasets.')
    args = parser.parse_args(argv)
    outputs = extract_agent_tool_data(args.input_root, args.output_root)
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return outputs


if __name__ == '__main__':
    main()
