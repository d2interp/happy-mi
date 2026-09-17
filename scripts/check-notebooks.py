"""Execute checked-in notebook code on CPU, skipping only dependency installs."""
import contextlib
import io
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for path in sorted((root / 'notebooks').glob('*.ipynb')):
    notebook = json.loads(path.read_text())
    namespace = {'__name__': '__notebook__'}
    for index, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code' or 'installation' in cell['metadata'].get('tags', []):
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(''.join(cell['source']), f'{path.name}:cell{index}', 'exec'), namespace)
    assert 'result' in namespace
    print(f'Executed {path.name}')
