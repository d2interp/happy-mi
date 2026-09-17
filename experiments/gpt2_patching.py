"""Small real-model exercise, not a replication of the complete IOI circuit.

Downloads pinned public GPT-2 weights. Patches the final token's residual at
each block output. Raw scores and self-patching controls are always retained.
"""

from datetime import datetime, timezone
import platform
import time

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from .common import recovery, save_json, seed_all

MODEL = 'openai-community/gpt2'
REVISION = '607a30d783dfa663caf39e06633721c8d4cfcd7e'
NAME_PAIRS = [('Mary', 'John'), ('Alice', 'Bob'), ('Sarah', 'James'), ('Anna', 'David')]


def unpack(output):
    return output[0] if isinstance(output, tuple) else output


def make_patch(source):
    def patch(module, inputs, output):
        hidden = unpack(output).clone()
        if hidden.shape != source.shape:
            raise ValueError('Source and target activations must be aligned')
        hidden[:, -1, :] = source[:, -1, :]
        return (hidden, *output[1:]) if isinstance(output, tuple) else hidden
    return patch


@torch.no_grad()
def cached_run(model, inputs):
    cache, handles = {}, []
    def saver(index):
        def save(module, args, output):
            cache[index] = unpack(output).detach().clone()
        return save
    try:
        for index, block in enumerate(model.transformer.h):
            handles.append(block.register_forward_hook(saver(index)))
        logits = model(**inputs, use_cache=False).logits[:, -1, :]
    finally:
        for handle in handles:
            handle.remove()
    return logits, cache


@torch.no_grad()
def patched_run(model, inputs, layer, source):
    handle = model.transformer.h[layer].register_forward_hook(make_patch(source))
    try:
        return model(**inputs, use_cache=False).logits[:, -1, :]
    finally:
        handle.remove()


def logit_difference(logits, correct, wrong):
    return (logits[0, correct] - logits[0, wrong]).item()


def main():
    start = time.perf_counter()
    seed_all(42)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, use_safetensors=True, attn_implementation='eager'
    ).eval()
    rows = []
    for io, subject in NAME_PAIRS:
        correct = tokenizer.encode(' ' + io, add_special_tokens=False)
        wrong = tokenizer.encode(' ' + subject, add_special_tokens=False)
        if len(correct) != 1 or len(wrong) != 1:
            raise ValueError(f'Names must be single tokens: {io}, {subject}')
        template = f'When {io} and {subject} went to the store, {{actor}} gave a drink to'
        clean_text, corrupt_text = template.format(actor=subject), template.format(actor=io)
        clean_inputs = tokenizer(clean_text, return_tensors='pt')
        corrupt_inputs = tokenizer(corrupt_text, return_tensors='pt')
        if clean_inputs['input_ids'].shape != corrupt_inputs['input_ids'].shape:
            raise ValueError('Token lengths must match')
        clean_logits, clean_cache = cached_run(model, clean_inputs)
        corrupt_logits, corrupt_cache = cached_run(model, corrupt_inputs)
        mc = logit_difference(clean_logits, correct[0], wrong[0])
        mr = logit_difference(corrupt_logits, correct[0], wrong[0])
        layers = []
        for layer in range(model.config.n_layer):
            patched = patched_run(model, corrupt_inputs, layer, clean_cache[layer])
            control = patched_run(model, corrupt_inputs, layer, corrupt_cache[layer])
            mp = logit_difference(patched, correct[0], wrong[0])
            error = (control - corrupt_logits).abs().max().item()
            if error > 1e-4:
                raise AssertionError(f'Self-patching changed logits: {error}')
            layers.append({'layer_zero_based': layer, 'patched_logit_difference': mp,
                           'recovery': recovery(mc, mr, mp) if abs(mc - mr) >= 1e-6 else None,
                           'self_patch_max_logit_error': error})
        # Last block / final token patch must reproduce the reference logits:
        # all subsequent operations are position-wise final LN and unembedding.
        final = patched_run(model, corrupt_inputs, model.config.n_layer - 1, clean_cache[model.config.n_layer - 1])
        final_error = (final - clean_logits).abs().max().item()
        if final_error > 1e-4:
            raise AssertionError(f'Final residual patch invariant failed: {final_error}')
        rows.append({'clean_text': clean_text, 'corrupted_text': corrupt_text,
                     'tokens': tokenizer.convert_ids_to_tokens(clean_inputs['input_ids'][0]),
                     'correct_token_id': correct[0], 'wrong_token_id': wrong[0],
                     'clean_logit_difference': mc, 'corrupted_logit_difference': mr,
                     'clean_prefers_io_over_subject': mc > 0,
                     'baseline_gap': mc - mr, 'final_patch_max_logit_error': final_error,
                     'layers': layers})
        print(f'{io}/{subject}: clean={mc:.3f}, corrupted={mr:.3f}', flush=True)
    mean_clean = sum(row['clean_logit_difference'] for row in rows) / len(rows)
    mean_corrupt = sum(row['corrupted_logit_difference'] for row in rows) / len(rows)
    aggregate = []
    for layer in range(model.config.n_layer):
        mean_patched = sum(row['layers'][layer]['patched_logit_difference'] for row in rows) / len(rows)
        aggregate.append({'layer_zero_based': layer, 'mean_patched_logit_difference': mean_patched,
                          'ratio_of_mean_differences': recovery(mean_clean, mean_corrupt, mean_patched)
                          if abs(mean_clean - mean_corrupt) >= 1e-6 else None})
    result = {'recorded_at': datetime.now(timezone.utc).isoformat(), 'kind': 'pretrained_residual_patching',
              'model': MODEL, 'revision': REVISION, 'device': 'cpu', 'dtype': 'float32',
              'python': platform.python_version(), 'torch': torch.__version__,
              'transformers': transformers.__version__, 'seed': 42,
              'patch_site': 'block output, last input token, entire residual vector',
              'scope': '4 name pairs, one template; exploratory teaching example',
              'mean_clean_logit_difference': mean_clean, 'mean_corrupted_logit_difference': mean_corrupt,
              'pairs': rows, 'aggregate': aggregate, 'elapsed_seconds': time.perf_counter() - start}
    print(f'Saved {save_json(result, "gpt2-patching.json")}')


if __name__ == '__main__':
    main()
