# GPT-2：一次真实的残差修补

这份实验把第七章的方法应用到预训练 GPT-2。目标很具体：在 IOI 风格句子上，比较两个候选名字的分数，并逐层把参考运行最后位置的残差搬入对照运行。

::: info 实验范围
这是四组名字、一个模板的教学实验。它没有复现 IOI 论文的完整头级回路，也没有验证新模板泛化。后层修补恢复率接近 1 是预期现象，不能据此认定后层是唯一原因。
:::

## 安装与运行

```bash
python -m pip install -r requirements-gpt2.txt
python -m experiments.gpt2_patching
```

首次运行从 Hugging Face 下载 `openai-community/gpt2` 的固定版本 `607a30d783dfa663caf39e06633721c8d4cfcd7e`，需要几百 MB 下载空间和可访问的网络。实验使用 CPU、float32、eager attention，不要求 GPU。结果保存到 `artifacts/gpt2-patching.json`。

固定的模型与依赖方便复现；仓库不会附带模型权重，使用权重应遵循模型来源的条款。

## 输入与指标

参考句为：

```text
When Mary and John went to the store, John gave a drink to
```

对照句只把后面的 John 换成 Mary。两次都使用同一个指标：`logit(" Mary") - logit(" John")`。程序验证名字是带空格的单 token，且两句 token 长度相等。

名字对是 Mary/John、Alice/Bob、Sarah/James、Anna/David。它们是预先列出的教学样例；程序保留所有结果，不删除与预期不符的样本。

## 替换位置

对每个 block，缓存参考和对照的输出。对照运行重做时，替换 `hidden[:, -1, :]`，即最后输入位置的完整残差向量。

```python
hidden = output[0].clone()
hidden[:, -1, :] = clean_cache[layer][:, -1, :]
return (hidden, *output[1:])
```

完整实现也兼容输出为单个张量的情况，并在 `finally` 中移除 hook。不要在输入端或最终 LayerNorm 后混用同一个位置名称；报告明确使用 block 输出。

## 两个必须通过的检查

**自我修补。** 把对照激活放回同一对照运行。整个词表的 logits 最大误差应接近零。若不成立，优先检查 dropout、缓存与 hook，而不是解释热图。

**最后一层检查。** 把最后 block、最后位置的参考残差放入对照运行。后面只剩逐位置的最终 LayerNorm 和反嵌入，因此这个位置的所有 logits 都应接近参考值。它检查了管线是否正确，不是一个新的机制发现。

## 阅读结果

先看每对输入的参考分数、对照分数和二者之差。然后看每层的原始修补分数。最后再看恢复率，并确认分母没有接近零。

聚合结果用“平均差值之比”，不是“每例比率的平均”。四组名字不构成充分的统计样本，不提供总体置信保证。实际测量值与图放在[首版实测记录](./results.md)。

## 下一步练习

把一个新模板完全留作测试，先用旧模板选候选层，再在新模板检验。还可以比较参考→对照和对照→参考两个干预方向。每次新增条件时，继续保存原始分数与无效案例。

## 文档与来源

- [Transformers 4.56.2 的 GPT-2 文档](https://huggingface.co/docs/transformers/v4.56.2/en/model_doc/gpt2)：本实验所用架构接口。
- [IOI 原论文](https://arxiv.org/abs/2211.00593)：任务背景；本实验不声称复现其完整分析。
