"""Build figures and a reader-facing report from measured JSON records.

Run intentionally when updating the published reference run. Normal CI does
not overwrite the publication with its own results.
"""
import json
from pathlib import Path
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[1]
target = root / 'docs' / 'public' / 'results'
target.mkdir(parents=True, exist_ok=True)
core = json.loads((root / 'artifacts/results.json').read_text())
gpt = json.loads((root / 'artifacts/gpt2-patching.json').read_text())
for name in ['results.json', 'gpt2-patching.json']:
    shutil.copyfile(root / 'artifacts' / name, target / name)

plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'svg.fonttype': 'none'})
fig, axes = plt.subplots(1, 3, figsize=(10, 3.4), constrained_layout=True)
colors = ['#2359a8', '#aa531c', '#21836a', '#7955a1', '#ba4265']
for ax, run in zip(axes, core['superposition']['runs']):
    weights = np.array(run['weights'])
    for i, (x, y) in enumerate(weights):
        ax.arrow(0, 0, x, y, color=colors[i], width=.008, head_width=.055, length_includes_head=True)
        ax.text(x * 1.14, y * 1.14, str(i + 1), color=colors[i], ha='center')
    ax.axhline(0, color='#cccccc', linewidth=.5)
    ax.axvline(0, color='#cccccc', linewidth=.5)
    ax.set(xlim=(-1.45, 1.45), ylim=(-1.45, 1.45), aspect='equal',
           title=f"P(active) = {run['probability']}", xlabel='Hidden coordinate 1', ylabel='Hidden coordinate 2')
fig.savefig(target / 'superposition.svg')
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 3.7), constrained_layout=True)
for pair in gpt['pairs']:
    ax.plot(range(12), [row['recovery'] for row in pair['layers']], alpha=.28, color='#2359a8')
ax.plot(range(12), [row['ratio_of_mean_differences'] for row in gpt['aggregate']],
        color='#2359a8', marker='o', label='Ratio of mean differences (4 pairs)')
ax.axhline(0, color='#888888', linewidth=.8)
ax.axhline(1, color='#888888', linewidth=.8, linestyle='--')
ax.set(xlabel='Block index (zero-based)', ylabel='Recovery ratio', xticks=range(12),
       title='GPT-2: final-position residual patching')
ax.legend(frameon=False)
fig.savefig(target / 'gpt2-patching.svg')
plt.close(fig)

for name in ['superposition.svg', 'gpt2-patching.svg']:
    svg = target / name
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')

p = core['probes']
rows = '\n'.join(f"| {r['probability']} | {r['test_mse_per_coordinate']:.5f} | {r['zero_baseline_mse']:.5f} | {r['relative_mse']:.3f} | {r['active_coordinate_mse']:.5f} |" for r in core['superposition']['runs'])
sae_rows = '\n'.join(f"| {r['lambda']} | {r['relative_error']:.4f} | {r['mean_l0']:.2f} | {r['dead_latents_on_test']} | {r['mean_best_positive_cosine']:.3f} |" for r in core['sae']['runs'])
gpt_rows = '\n'.join(f"| {pair['clean_text'].split()[1]} / {pair['clean_text'].split()[3]} | {pair['clean_logit_difference']:.3f} | {pair['corrupted_logit_difference']:.3f} | {pair['baseline_gap']:.3f} |" for pair in gpt['pairs'])
max_error = max(layer['self_patch_max_logit_error'] for pair in gpt['pairs'] for layer in pair['layers'])
page = f'''# 首版实测记录

本页由实际运行产生的 JSON 自动生成，非手工编造的示例输出。记录时间为 {core['recorded_at']}；随机种子为 42，设备为 CPU。它是一组参考运行，不是跨平台性能保证或统计研究结论。

环境：Python {core['environment']['python']}、PyTorch {core['environment']['torch']}、NumPy {core['environment']['numpy']}。平台：`{core['environment']['platform']}`。核心实验总运行时间约 {core['elapsed_seconds']:.1f} 秒，不含依赖安装与绘图。

下载原始记录：[核心实验 JSON](/results/results.json)、[GPT-2 JSON](/results/gpt2-patching.json)。完整命令见[实验手册](./index.md)。

## 探针：可读出但未被使用

正常标签探针的测试准确率为 {p['probe_test_accuracy']:.2%}；随机标签控制为 {p['random_label_test_accuracy']:.2%}；多数类基线为 {p['majority_test_accuracy']:.2%}。将第二坐标置零后，{p['test_samples_with_coordinate_changed']} 个样本的该坐标改变，下游预测改变了 {p['target_predictions_changed']} 个。

原因可以从构造直接检查：下游规则只使用第一坐标，探针读取第二坐标。这是已知机制的合成反例，不是语言模型的观测结论。

## 叠加：五个特征与二维瓶颈

![三个非零概率下，训练后五个特征在二维隐藏空间中的方向；颜色区分输入特征编号。](/results/superposition.svg)

每幅图展示五个输入特征对应的权重向量，颜色不表示语义。有限训练下的具体角度依赖种子，不能只凭形状命名概念。

| 非零概率 | 测试 MSE/坐标 | 零输出基线 | 相对 MSE | 活跃坐标 MSE |
| --- | --- | --- | --- | --- |
{rows}

稀疏度变化也改变零基线，因此不能直接把绝对误差更低解释为方法更强。每组均为 1500 步训练、4096 个独立测试样本。

## SAE：重构与稀疏性的折中

| λ | 相对均值基线误差 | 平均 L0 | 测试集死隐元 | 平均最佳正余弦 |
| --- | --- | --- | --- | --- |
{sae_rows}

数据来自 12 个真实方向、8 维激活；SAE 宽度 24，每组 1600 步。方向分数允许多对一匹配，仅作诊断。表中的数字不证明字典唯一性，也不表示对语言特征的恢复。

## GPT-2：真实残差修补

模型为 `{gpt['model']}`，固定版本 `{gpt['revision']}`，Transformers {gpt['transformers']}。该次运行约 {gpt['elapsed_seconds']:.1f} 秒（可能包含首次权重下载），不代表纯推理耗时。

| 名字对 | 参考 logit 差 | 对照 logit 差 | 差值 |
| --- | --- | --- | --- |
{gpt_rows}

![GPT-2 十二个 block 的最后位置残差修补恢复率；浅线为各名字对，深线为平均分数差的比率。](/results/gpt2-patching.svg)

横轴从 0 编号。浅线是单个名字对，深线是平均差值之比。全部自我修补检查的最大 logit 误差为 {max_error:.2g}。最后 block 的恢复接近 1 是计算结构预期，不是定位到独占机制的证据。

这里只有一个模板和四组名字，没有留出的新模板；因此这是探索性教学样例。真正的小项目应扩大输入分布并单独验证假设，不能从本图得出完整 IOI 回路结论。

## 如何更新此页

维护者先运行两套实验，再安装 `requirements-figures.txt` 并执行 `python scripts/publish-results.py`。此操作会明确更新已发布记录、图和本页；普通网站构建不会重新测量或替换它们。
'''
(root / 'docs/labs/results.md').write_text(page)
print('Published measured records, two SVG figures and results.md')
