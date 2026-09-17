"""Broad scientific sanity checks, not exact floating-point snapshots."""
import json
import sys

with open(sys.argv[1]) as handle:
    result = json.load(handle)
p = result['probes']
assert p['probe_test_accuracy'] > 0.95, p
assert 0.4 < p['random_label_test_accuracy'] < 0.6, p
assert p['target_predictions_changed'] == 0, p
assert p['test_samples_with_coordinate_changed'] == p['test_samples'], p
for run in result['superposition']['runs']:
    assert 0 <= run['relative_mse'] < 1, run
for run in result['sae']['runs']:
    assert 0 <= run['relative_error'] < 0.25, run
    assert 0 < run['mean_l0'] < result['sae']['sae_width'], run
print('Probe control, downstream invariance, reconstruction baselines and sparsity passed.')
