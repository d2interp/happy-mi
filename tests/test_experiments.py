"""Invariants and controls that catch misleading experiment implementations."""

import unittest
import torch
from experiments.common import recovery
from experiments.first_intervention import forward
from experiments.induction import induction_pattern, predict
from experiments.sae import SparseAutoencoder
from experiments.superposition import sparse_batch


class ExperimentChecks(unittest.TestCase):
    def test_unused_coordinate_is_really_unused(self):
        for x in (0, 1):
            for value in (-100, 0, 100):
                self.assertEqual(forward(x)[1], forward(x, (1, value))[1])

    def test_patch_transfers_reference(self):
        cache, score = forward(1)
        self.assertEqual(forward(0, (0, cache[0]))[1], score)
        self.assertNotEqual(forward(0, (1, cache[1]))[1], score)

    def test_recovery_is_not_a_clipped_probability(self):
        self.assertAlmostEqual(recovery(4, -2, 1), 0.5)
        self.assertGreater(recovery(4, -2, 5), 1)
        self.assertLess(recovery(4, -2, -3), 0)
        with self.assertRaises(ValueError):
            recovery(1, 1, 2)

    def test_induction_cannot_read_future(self):
        tokens = ['A', 'B', 'A', 'C', 'A']
        for t, row in enumerate(induction_pattern(tokens)):
            self.assertTrue(all(value == 0 for value in row[t + 1:]))
        self.assertEqual(predict(['P', 'Q', 'R', 'P']), 'Q')
        self.assertEqual(predict(tokens), 'C')
        self.assertIsNone(predict(['A', 'B', 'C']))

    def test_sparse_data_extremes(self):
        self.assertEqual(sparse_batch(10, 5, 0).count_nonzero().item(), 0)
        self.assertTrue(torch.all(sparse_batch(10, 5, 1) >= 0))

    def test_sae_dictionary_scale_constraint(self):
        model = SparseAutoencoder()
        with torch.no_grad():
            model.decoder.mul_(8)
        model.normalize_decoder()
        self.assertTrue(torch.allclose(model.decoder.norm(dim=-1), torch.ones(24), atol=1e-6))
        reconstructed, z = model(torch.randn(4, 8))
        self.assertEqual(reconstructed.shape, (4, 8))
        self.assertTrue(torch.all(z >= 0))


if __name__ == '__main__':
    unittest.main()
