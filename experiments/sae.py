"""ReLU-L1 SAE on a known synthetic dictionary, with held-out evaluation."""

import json
import torch
from .common import seed_all


class SparseAutoencoder(torch.nn.Module):
    def __init__(self, d=8, width=24):
        super().__init__()
        self.encoder = torch.nn.Linear(d, width)
        self.decoder = torch.nn.Parameter(torch.randn(width, d))
        self.bias = torch.nn.Parameter(torch.zeros(d))
        self.normalize_decoder()
        with torch.no_grad():
            self.encoder.weight.copy_(self.decoder)
            self.encoder.bias.fill_(-0.1)

    @torch.no_grad()
    def normalize_decoder(self):
        self.decoder.copy_(torch.nn.functional.normalize(self.decoder, dim=-1))

    def forward(self, h):
        z = torch.relu(self.encoder(h - self.bias))
        return z @ self.decoder + self.bias, z


def generate_data(dictionary, count, generator):
    n = dictionary.shape[0]
    values = torch.rand(count, n, generator=generator)
    active = torch.rand(count, n, generator=generator) < 0.1
    return (values * active) @ dictionary


def run(seed=42, steps=1600):
    seed_all(seed)
    truth = torch.nn.functional.normalize(torch.randn(12, 8), dim=-1)
    train = generate_data(truth, 8192, torch.Generator().manual_seed(seed + 10))
    test = generate_data(truth, 2048, torch.Generator().manual_seed(seed + 20))
    baseline = ((test - train.mean(dim=0)) ** 2).sum(dim=-1).mean().item()
    runs = []
    for penalty in [0.02, 0.1]:
        # Same initialization and minibatch stream for a controlled comparison.
        seed_all(seed + 1)
        model = SparseAutoencoder()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.003)
        for _ in range(steps):
            h = train[torch.randint(len(train), (128,))]
            reconstructed, z = model(h)
            loss = ((h - reconstructed) ** 2).sum(dim=-1).mean() + penalty * z.sum(dim=-1).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            model.normalize_decoder()
        with torch.no_grad():
            reconstructed, z = model(test)
            mse = ((test - reconstructed) ** 2).sum(dim=-1).mean().item()
            active = z > 1e-6
            # Positive matching, many-to-one; explicitly not a recovery proof.
            matching = (truth @ model.decoder.T).max(dim=1).values
            runs.append({
                'lambda': penalty, 'steps': steps, 'test_squared_error_per_sample': mse,
                'mean_baseline_squared_error': baseline, 'relative_error': mse / baseline,
                'mean_l0': active.sum(dim=-1).float().mean().item(),
                'dead_latents_on_test': (~active.any(dim=0)).sum().item(),
                'activation_threshold': 1e-6,
                'mean_best_positive_cosine': matching.mean().item(),
                'best_positive_cosines': matching.tolist(),
            })
    return {'kind': 'trained_synthetic_dictionary', 'seed': seed, 'd': 8,
            'true_features': 12, 'sae_width': 24, 'train_samples': len(train),
            'test_samples': len(test), 'runs': runs}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
