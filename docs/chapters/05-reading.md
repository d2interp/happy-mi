# 5. 观察模型的中间计算

我们已经知道 Transformer 会不断更新残差流。现在的问题是：**这些中间状态透露了什么，哪些东西又不能仅靠观察得知？**

本章介绍三种观察方式：缓存激活、查看注意力、把残差向量投影到词表。它们用于提出假设，不能单独完成因果解释。

## 5.1 权重与激活不是一回事

权重是在训练中学到的参数。对于固定模型，换一个输入，权重一般不变；激活则是模型在这次输入上计算得到的中间数值。

研究某个头时，我们可能看它的 $W_Q,W_K,W_V,W_O$，也可能看某句话上的注意力矩阵和输出。权重告诉我们它能实现怎样的变换，激活告诉我们这次运行实际发生了什么。

缓存激活时通常使用 `detach().clone()`：`detach` 不保留用于反向传播的计算关系，`clone` 创建独立副本。只保存一个引用，之后的原地修改可能悄悄改变缓存。

## 5.2 用 hook 观察一个模块

PyTorch 的 forward hook 可以在模块完成前向计算时取得输出。以下是一个独立运行的小例子：

```python
import torch

model = torch.nn.Sequential(torch.nn.Linear(2, 3), torch.nn.ReLU(), torch.nn.Linear(3, 1))
cache = {}

def save_activation(module, inputs, output):
    cache['hidden'] = output.detach().clone()

handle = model[1].register_forward_hook(save_activation)
try:
    with torch.no_grad():
        prediction = model(torch.tensor([[1., 0.]]))
finally:
    handle.remove()

print(cache['hidden'].shape)  # torch.Size([1, 3])
```

`model.eval()` 用于切换 dropout 等模块的运行模式，`torch.no_grad()` 用于停止记录梯度；两者用途不同。在真实模型实验中通常两个都要用。hook 用完后应移除，否则后续运行可能继续受到旧 hook 影响。

## 5.3 注意力图能告诉我们什么

一张注意力图的行对应目标位置，列对应源位置。某一行在前文名字处很亮，说明这个头给那个位置较高的读取权重。

但头输出还取决于值向量和输出投影。第四章的练习把 $W_O$ 设为零后，注意力图不变，写入却全部消失。这是一个明确反例：关注某位置，并不等于该位置对输出有很大因果贡献。

更好的做法是同时记录输入 token、注意力权重、头写入的向量与下游指标。把热图视为寻找候选机制的工具，然后设计干预实验。

## 5.4 Logit lens：借用模型的输出词表

模型最终用反嵌入矩阵 $W_U$ 把残差向量变成词表分数。**Logit lens** 的想法是把同一个读出器提前用在中间残差上：

$$\ell_t^{(l)}=\operatorname{LN}_f(r_t^{(l)})W_U+b_U.$$

这样，我们可以逐层查看某位置的最高分 token，或比较目标 token 的分数变化。它方便的地方在于读出器已经存在，不用另外训练探针。

但中间层未必处在最终读出器最适合解释的表示空间。早期层的奇怪预测不意味着该层没有信息；某个词提前得到高分，也不意味着模型已经按人类意义“决定了答案”。Tuned lens 通过训练各层的仿射变换改善读出，但它仍然是一个观察工具。

## 5.5 直接 logit 归因

先暂时省略最终 LayerNorm。假设最终残差分解为嵌入与多个组件输出之和：$r=e+\sum_j c_j$。对于候选 token $a,b$，设 $u=W_U[:,a]-W_U[:,b]$，则

$$\ell_a-\ell_b=e\cdot u+\sum_j c_j\cdot u+(b_{U,a}-b_{U,b}).$$

每个 $c_j\cdot u$ 是组件对最终分数差的直接线性项。这个代数分解常称为直接 logit 归因（direct logit attribution，DLA）。

实际模型含有最终 LayerNorm。精确分解需要把该次运行总残差的归一化尺度固定，并正确处理中心化、缩放与偏置。不能把每个 $c_j$ 各自送进 LayerNorm 后求和，宣称得到了同一个恒等式。

更关键的是，DLA 描述的是既有运行的直接读出项。移除早期组件后，后续层会重新计算，因此真实输出变化未必等于这个直接项。

## 5.6 一个纸笔检查

令 $u=(1,-1)$，两个组件输出 $c_1=(3,1)$、$c_2=(-1,2)$，没有偏置和归一化。第一项贡献是 2，第二项是 −3，总分数差是 −1。

第二个组件的范数并不比第一个大很多，但它沿着我们关心的读出方向抵消了前者。单看激活的绝对大小无法判断它对这个指标的方向性贡献。

::: warning 这个方法会怎样误导我们
“这一层预测出了正确词”“这个头关注名字”“这个组件直接贡献为正”是三个不同的观察。它们都不自动等于“删除它会让模型答错”。保留原始输入与指标，下一章和第七章会进一步检验这些假设。
:::

## 小结

缓存让中间计算可见，注意力图展示读取模式，logit lens 提供词表视角，DLA 分解既定运行的直接读出贡献。每一种图和分数都有自己的定义；理解定义比给图起一个吸引人的解释更重要。

## 练习

1. **基础**：解释为什么保存激活时常用 `detach().clone()`。
2. **基础**：在本章纸笔例子里，把 $c_2$ 改为 $(1,2)$，重新计算总分数差。
3. **进阶**：构造一个后续层会抵消早期写入的例子，解释 DLA 为什么不等于消融效应。

## 一手文献

- [nostalgebraist, Interpreting GPT: the logit lens](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens)：原始方法介绍。
- [Belrose et al., Eliciting Latent Predictions from Transformers with the Tuned Lens](https://arxiv.org/abs/2303.08112)：学习读出器的改进与评估。
- [Jain & Wallace, Attention is not Explanation](https://aclanthology.org/N19-1357/)：注意力权重与解释之间的关系。结论应连同其任务与模型设定阅读，不能概括为所有注意力研究都无效。
