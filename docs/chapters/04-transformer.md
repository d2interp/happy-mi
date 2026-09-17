# 4. 从预测词到 Transformer

“When Mary and John went to the store, John gave a drink to” 后面应该接什么？我们可能回答 “Mary”。语言模型做的事情更具体：给词表中的每个下一个 token 分配概率。

本章沿着一次前向计算走完 decoder-only Transformer。目标不是记住所有架构变体，而是知道以后要观察和干预的变量在哪里。

## 4.1 从文字到 token

分词器把字符串转换为整数序列。token 可以是完整单词、词的一部分、标点或空格组合；一个汉字也不保证对应一个 token。词表大小记为 $V$。

嵌入矩阵 $W_E\in\mathbb R^{V\times d}$ 为每个 token 提供一个 $d$ 维向量。对于 GPT-2，还会加入学习到的位置向量：

$$r_t^{(0)}=W_E[\mathrm{token}_t]+W_{\mathrm{pos}}[t].$$

位置 $t$ 的向量承载了当前 token 与位置的信息。把所有位置叠在一起，得到 $R^{(0)}\in\mathbb R^{T\times d}$。这里先省略 batch 轴。

::: tip 先检查分词
比较两个名字时，要验证它们是否都是带前导空格的单 token。`"Mary"` 与 `" Mary"` 可能对应不同 token。后面的实验会实际检查，而不是凭肉眼假定。
:::

## 4.2 残差流：组件读写的公共状态

GPT-2 风格的 pre-LayerNorm 块可以写成：

$$
R_{\mathrm{mid}}^{(l)}=R^{(l)}+\operatorname{Attn}^{(l)}(\operatorname{LN}_1(R^{(l)})),
$$

$$
R^{(l+1)}=R_{\mathrm{mid}}^{(l)}+
\operatorname{MLP}^{(l)}(\operatorname{LN}_2(R_{\mathrm{mid}}^{(l)})).
$$

我们把 $R$ 称为**残差流**（residual stream）。每个组件读取归一化后的状态，并把自己的输出加回去。这个视角便于问：“这个头向残差流写入了什么？”

加法并不意味着每个组件互不影响。后一个组件的输入包含前一个组件写入的内容；它们通过残差流相互作用。

## 4.3 注意力：从哪里读取，读取什么

设归一化后的输入为 $X\in\mathbb R^{T\times d}$。一个头生成查询、键和值：

$$Q=XW_Q,\quad K=XW_K,\quad V_h=XW_V.$$

三者形状都是 $T\times d_h$。查询和键的相似程度决定注意力分数：

$$A=\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_h}}+M\right).$$

softmax 沿每一行计算。$A_{ts}$ 表示目标位置 $t$ 从源位置 $s$ 读取的权重。因果掩码 $M_{ts}$ 在 $s>t$ 时为负无穷，其他位置为零，防止当前位置看到未来。

头输出为：

$$O=AV_hW_O,\qquad W_O\in\mathbb R^{d_h\times d}.$$

这里有两个不同问题：$A$ 决定从哪里读取，$W_VW_O$ 决定把读取的内容转换为什么。只看 $A$，还没有看完整个头。

```python
import math
import torch

torch.manual_seed(0)
T, d, dh = 4, 8, 4
X = torch.randn(T, d)
Wq, Wk, Wv = [torch.randn(d, dh) / math.sqrt(d) for _ in range(3)]
Wo = torch.randn(dh, d) / math.sqrt(dh)
scores = (X @ Wq) @ (X @ Wk).T / math.sqrt(dh)
future = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
A = scores.masked_fill(future, float('-inf')).softmax(dim=-1)
O = A @ (X @ Wv) @ Wo
assert O.shape == X.shape
assert torch.allclose(A.sum(dim=-1), torch.ones(T))
```

这段随机权重代码用于验证形状和掩码，不代表一个已经学会语言的注意力头。

## 4.4 QK 与 OV 的分工

把投影合并后，注意力分数中的双线性部分为：

$$QK^\top=X\underbrace{W_QW_K^\top}_{W_{QK}}X^\top.$$

头写入的内容可以写成：

$$O=AX\underbrace{W_VW_O}_{W_{OV}}.$$

QK 与 OV 分解让我们分别研究匹配规则与内容搬运规则。这里省略了偏置；实际 GPT-2 有偏置，精确数值分析时应使用完整前向实现。位置编码和 LayerNorm 也不能在真实计算中随意删去。

多个头的输出投影可以分块写成各头贡献之和，再加输出偏置。这是一种有用的代数重写，并不证明头之间在统计上或功能上独立。

## 4.5 MLP：每个位置上的非线性计算

MLP 对每个 token 位置分别应用同一个函数：

$$\operatorname{MLP}(x)=\phi(xW_{\mathrm{in}}+b_{\mathrm{in}})W_{\mathrm{out}}+b_{\mathrm{out}}.$$

$W_{\mathrm{in}}$ 把 $d$ 维输入映射到更多隐藏坐标；非线性函数 $\phi$ 在 GPT-2 中为 GELU；$W_{\mathrm{out}}$ 再写回 $d$ 维。单个隐藏神经元可看成“读一个方向，经非线性后，沿另一个方向写入”。但神经元可能响应多个模式，不能先验地给每个神经元分配一个单独概念。

注意力负责跨位置混合；MLP 在单个位置上变换已经汇集的信息。这是架构上的区别，不意味着某项人类概念只由一种组件实现。

## 4.6 LayerNorm 与最终输出

LayerNorm 对一个位置的向量做中心化、缩放和可学习的仿射变换：

$$\operatorname{LN}(x)=\gamma\odot\frac{x-\mu(x)}{\sqrt{\sigma^2(x)+\epsilon}}+\beta.$$

其中均值和方差沿特征维计算。因为分母依赖 $x$，LayerNorm 不是一个固定的线性矩阵。把残差贡献分别归一化再相加，通常不等于把总残差归一化。

最终输出是：

$$\ell_t=\operatorname{LN}_{f}(r_t^{(L)})W_U+b_U,\qquad W_U\in\mathbb R^{d\times V}.$$

用最后一个输入位置的 logits 预测下一个 token。训练时在很多位置同时预测各自的下一个 token，这就是自回归语言建模。

::: warning 这个方法会怎样误导我们
本章的具体公式以 GPT-2 风格结构为例。采用 RoPE、RMSNorm、门控 MLP 或分组查询注意力的模型需要调整实现。残差流视角仍有帮助，但不能把 GPT-2 的头编号、位置编码或归一化规则直接移植过去。
:::

## 小结

一次前向计算从 token 嵌入出发，经过注意力和 MLP 的反复读写，最后映射到词表分数。之后的解释工具，会在这个计算图中缓存、读取或替换变量。先画清变量所在位置，才能解释一次实验到底改了什么。

## 练习

1. **基础**：序列长 6、残差宽度 32、头宽度 8 时，$QK^\top$、$A$、$W_{OV}$ 的形状各是什么？
2. **基础**：在示例代码中检查 `A[0]`。为什么它只能关注第一个位置？
3. **进阶**：让 `Wo` 全为零，重新观察注意力图和头输出。为什么注意力图看起来正常，却没有任何写入？

## 一手文献

- [Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762)，第 3 节：注意力和多头结构。
- [Elhage et al., A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)：残差流、QK/OV 和头组合的来源。
- [Radford et al., Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)：GPT-2 的模型背景。
