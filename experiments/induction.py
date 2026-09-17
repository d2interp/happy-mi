"""A discrete induction rule, NOT a learned attention head."""

import json


def induction_pattern(tokens):
    pattern = []
    for t, token in enumerate(tokens):
        matches = [j for j in range(1, t + 1) if tokens[j - 1] == token]
        row = [0.0] * len(tokens)
        if matches:
            row[matches[-1]] = 1.0
        pattern.append(row)
    return pattern


def predict(tokens):
    if not tokens:
        raise ValueError('Need at least one token')
    row = induction_pattern(tokens)[-1]
    return tokens[row.index(1.0)] if 1.0 in row else None


def run():
    tokens = ['A', 'B', 'C', 'D', 'A']
    return {'kind': 'hand_constructed_rule', 'tokens': tokens,
            'pattern': induction_pattern(tokens), 'prediction': predict(tokens),
            'tie_break': 'most recent matching predecessor; a teaching convention'}


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
