"""An exact counterexample: decodability does not imply downstream use."""

import json


def forward(x, replace=None):
    h = [float(x), float(x)]
    if replace is not None:
        node, value = replace
        h[node] = float(value)
    return h, 2 * h[0] - 1


def run():
    clean_h, clean = forward(1)
    _, corrupted = forward(0)
    return {
        'kind': 'hand_constructed',
        'clean': clean,
        'corrupted': corrupted,
        'ablate_h1': forward(1, (0, 0))[1],
        'ablate_h2': forward(1, (1, 0))[1],
        'patch_h1': forward(0, (0, clean_h[0]))[1],
        'patch_h2': forward(0, (1, clean_h[1]))[1],
    }


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
