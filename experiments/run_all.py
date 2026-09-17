"""Run the CPU teaching suite and preserve actual measurements."""

from datetime import datetime, timezone
import json
import platform
import time

import numpy as np
import torch
from . import first_intervention, induction, probes, sae, superposition
from .common import save_json


def main():
    started = time.perf_counter()
    result = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'environment': {'python': platform.python_version(), 'torch': torch.__version__,
                        'numpy': np.__version__, 'platform': platform.platform(), 'device': 'cpu'},
    }
    for name, module in [('first_intervention', first_intervention), ('induction', induction),
                         ('probes', probes), ('superposition', superposition), ('sae', sae)]:
        print(f'Running {name} ...', flush=True)
        result[name] = module.run()
    result['elapsed_seconds'] = time.perf_counter() - started
    path = save_json(result, 'results.json')
    print(json.dumps({'saved': str(path), 'elapsed_seconds': result['elapsed_seconds'],
                      'probe_accuracy': result['probes']['probe_test_accuracy'],
                      'sae_relative_errors': [r['relative_error'] for r in result['sae']['runs']]}, indent=2))


if __name__ == '__main__':
    main()
