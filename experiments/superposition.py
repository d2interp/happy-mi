"""Train the tied-weight ReLU toy model on independent sparse features."""

import json
import torch
from .common import seed_all


class ToyModel(torch.nn.Module):
    def __init__(self, features=5, hidden=2):
        super().__init__()
        self.W = torch.nn.Parameter(torch.randn(features, hidden) * 0.2)
        self.bias = torch.nn.Parameter(torch.zeros(features))

    def forward(self, x):
        return torch.relu((x @ self.W) @ self.W.T + self.bias)


def sparse_batch(batch, features, probability, generator=None):
    values = torch.rand(batch, features, generator=generator)
    active = torch.rand(batch, features, generator=generator) < probability
    return values * active


def train_one(probability, seed=42, steps=1500):
    seed_all(seed)
    model = ToyModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    for _ in range(steps):
        x = sparse_batch(256, 5, probability)
        loss = ((model(x) - x) ** 2).sum(dim=-1).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    # Independent stream: test data must not depend on training step count.
    test_generator = torch.Generator().manual_seed(seed + 10000)
    with torch.no_grad():
        test = sparse_batch(4096, 5, probability, test_generator)
        error = (model(test) - test) ** 2
        mse, baseline = error.mean().item(), test.square().mean().item()
        unit = torch.nn.functional.normalize(model.W, dim=-1)
        return {
            'probability': probability, 'seed': seed, 'steps': steps,
            'test_mse_per_coordinate': mse, 'zero_baseline_mse': baseline,
            'relative_mse': mse / baseline,
            'active_coordinate_mse': error[test > 0].mean().item(),
            'weights': model.W.tolist(), 'bias': model.bias.tolist(),
            'norms': model.W.norm(dim=-1).tolist(),
            'cosine_matrix': (unit @ unit.T).tolist(),
        }


def run(seed=42):
    return {'kind': 'trained_synthetic', 'features': 5, 'hidden': 2,
            'runs': [train_one(p, seed) for p in [0.5, 0.1, 0.03]]}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
