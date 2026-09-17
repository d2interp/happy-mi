"""Train a probe for a variable explicitly unused by the target model."""

import json
import torch
from .common import seed_all


def fit_probe(h, labels, steps=200):
    probe = torch.nn.Linear(h.shape[1], 1)
    optimizer = torch.optim.Adam(probe.parameters(), lr=0.05)
    for _ in range(steps):
        logits = probe(h).squeeze(-1)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    return probe


@torch.no_grad()
def accuracy(probe, h, labels):
    return ((probe(h).squeeze(-1) > 0) == labels.bool()).float().mean().item()


def run(seed=42):
    seed_all(seed)
    train = torch.randn(2048, 3)
    test = torch.randn(2048, 3)
    y_train, y_test = (train[:, 1] > 0).float(), (test[:, 1] > 0).float()
    probe = fit_probe(train, y_train)
    shuffled_train = y_train[torch.randperm(len(y_train))]
    shuffled_test = y_test[torch.randperm(len(y_test))]
    control = fit_probe(train, shuffled_train)
    modified = test.clone()
    modified[:, 1] = 0
    # The target uses coordinate 0 only; the probe reads coordinate 1.
    target_before, target_after = test[:, 0] > 0, modified[:, 0] > 0
    return {
        'kind': 'synthetic_known_mechanism', 'seed': seed,
        'train_samples': len(train), 'test_samples': len(test),
        'probe_train_accuracy': accuracy(probe, train, y_train),
        'probe_test_accuracy': accuracy(probe, test, y_test),
        'random_label_train_accuracy': accuracy(control, train, shuffled_train),
        'random_label_test_accuracy': accuracy(control, test, shuffled_test),
        'majority_test_accuracy': max(y_test.mean().item(), 1 - y_test.mean().item()),
        'target_predictions_changed': (target_before != target_after).sum().item(),
        'test_samples_with_coordinate_changed': (test[:, 1] != modified[:, 1]).sum().item(),
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
