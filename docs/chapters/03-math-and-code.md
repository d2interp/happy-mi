# 3. 够用的数学与代码

在双节点实验里，激活只是两个数字。在语言模型里，激活往往是成百上千个数字。我们需要一种紧凑的方式组织和计算它们。本章只学习后面会反复使用的工具；不需要先修完一门线性代数课程。

本章目标：理解向量、矩阵乘法、点积、softmax 和梯度；能看懂批量张量的形状。

## 3.1 Python 中的最少约定

变量保存值，列表保存一组值，函数把一组输入变成输出。

```python
values = [1.0, 2.0, 3.0]

def twice(x):
    return 2 * x

for value in values:
    print(twice(value))
```

`values[0]` 是第一个元素，`values[-1]` 是最后一个，`values[:2]` 是前两个。缩进决定函数和循环的范围。后面的模型代码经常使用 `x[:, -1, :]`，意思是取所有样本、最后一个位置、所有特征。

## 3.2 向量、长度和方向

向量是一组按顺序排列的数，如 $x=(2,1)$。既可以把它理解成两个测量值，也可以理解成平面上的箭头。向量的长度是 $\|x\|_2=\sqrt{2^2+1^2}=\sqrt 5$。

两个向量的点积把对应位置相乘后求和：

$$x\cdot w=\sum_i x_iw_i.$$

若 $w=(1,-1)$，则 $x\cdot w=1$。一个线性分类器就可以计算 $s=x\cdot w+b$，再用分数的正负分类。这里 $w$ 规定读取哪个方向，$b$ 是偏置。

把 $w$ 归一化为单位向量 $u=w/\|w\|_2$ 后，$x\cdot u$ 是沿该方向的有符号投影长度。余弦相似度则是 $(x\cdot w)/(\|x\|_2\|w\|_2)$；零向量没有定义良好的方向，不应直接代入。

## 3.3 矩阵是一组线性读取

本书使用**行向量**约定。一个样本 $x\in\mathbb R^d$ 右乘矩阵 $W\in\mathbb R^{d\times m}$，得到 $m$ 个输出。矩阵的每一列是一个读取方向。

$$y=xW+b.$$

例如 $x=[2,1]$，$W=\begin{bmatrix}1&-1&0\\0&2&1\end{bmatrix}$，那么 $y=[2,0,1]$。把两个样本叠成 $X\in\mathbb R^{2\times2}$，同一条公式可以同时处理两个样本。

```python
import torch

X = torch.tensor([[2., 1.], [0., 3.]])
W = torch.tensor([[1., -1., 0.], [0., 2., 1.]])
Y = X @ W
print(Y)        # tensor([[2., 0., 1.], [0., 6., 3.]])
print(Y.shape)  # torch.Size([2, 3])
```

`@` 是矩阵乘法，`*` 通常是逐元素乘法。把它们混淆会产生形状错误，或者更危险地得到形状正确但意义错误的结果。

## 3.4 张量的维度是语义标签

张量是多维数组。语言模型中的残差激活通常有形状 `[batch, position, d_model]`。

| 轴 | 含义 | 小例子 |
| --- | --- | --- |
| batch | 一次处理多少段输入 | 2 段句子 |
| position | 每段输入有多少个 token | 每段 5 个 |
| d_model | 每个 token 有多少个内部坐标 | 32 维 |

`x.shape == (2, 5, 32)` 并不意味着第 32 维是 32 种人类概念。它只是网络使用的数值坐标。执行 `x.mean(dim=1)` 会平均 token 位置，得到 `(2, 32)`；执行 `x[:, -1, :]` 会取最后位置，也得到 `(2, 32)`，但两者含义不同。

形状相同不保证语义相同。做干预时，来源和目标位置不仅要形状兼容，还要有清楚的对应关系。

## 3.5 非线性与概率

ReLU 将负数变为零：$\operatorname{ReLU}(z)=\max(0,z)$。多个纯线性层可以合并成一个线性变换；加入非线性后，模型能够表示更复杂的函数。

语言模型最后输出词表中每个 token 的分数，称为 **logit**。softmax 把这些分数转换为概率：

$$p_i=\frac{e^{\ell_i}}{\sum_j e^{\ell_j}}.$$

所有 logits 同时加上一个常数，概率不变。两个候选的对数概率比为 $\log(p_a/p_b)=\ell_a-\ell_b$，这解释了后面为什么常用 logit 差作为指标。

```python
logits = torch.tensor([2., 1., 0.])
print(torch.softmax(logits, dim=-1))
# 约为 tensor([0.6652, 0.2447, 0.0900])
```

实现时直接调用 `softmax`，不要手动计算巨大指数。交叉熵损失衡量模型对正确答案的预测：单个样本的损失为 $-\log p_y$。训练使这个损失降低，但不会自动使网络内部变得容易理解。

## 3.6 导数、梯度与训练

导数描述很小的输入变化怎样改变输出。对 $f(x)=x^2$，在 $x=3$ 处的导数是 6。多变量函数对每个坐标的导数组成梯度。

```python
x = torch.tensor(3., requires_grad=True)
y = x ** 2
y.backward()
print(x.grad)  # tensor(6.)
```

训练中，我们用梯度更新权重以降低损失。一个基本循环是：计算输出、计算损失、清空旧梯度、反向传播、更新参数。解释模型时则常常冻结权重，只观察或替换激活；这与重新训练模型是不同的操作。

```python
layer = torch.nn.Linear(2, 1)
optimizer = torch.optim.Adam(layer.parameters(), lr=0.01)
inputs = torch.tensor([[0., 1.], [1., 0.]])
targets = torch.tensor([[1.], [0.]])
for _ in range(100):
    loss = ((layer(inputs) - targets) ** 2).mean()
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

PyTorch 的 `Linear` 将权重存为 `[out_features, in_features]`，内部实际计算 `x @ weight.T + bias`；本书公式中的 $W$ 对应 `weight.T`。核对转置可以避免很多错误。

::: warning 这个方法会怎样误导我们
梯度描述局部小变化，未必预测大幅干预。对 $f(x)=x^2$，在 $x=0$ 的梯度为零，但把 $x$ 改成 2 会让输出变成 4。“梯度很小”不能直接推出“大幅替换没有影响”。
:::

## 小结

向量表示状态，矩阵读写方向，非线性允许更复杂的计算。张量的每个轴都有语义；在开始理解机制之前，先确保自己知道计算发生在哪个样本、哪个位置、哪个坐标上。

## 练习

1. **基础**：手算 $[1,2]\begin{bmatrix}2&0\\1&3\end{bmatrix}$，再用 PyTorch 检查。
2. **基础**：形状为 `(4, 6, 8)` 的 `x`，`x[:, -1, :]` 和 `x.mean(dim=0)` 的形状分别是什么？
3. **进阶**：给所有 logits 加 100，检查 softmax 是否不变；再只给一个 logit 加 1，观察变化。

## 一手文献与文档

- [PyTorch：Tensors](https://pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html)：张量形状与索引的官方入门。
- [PyTorch：Automatic Differentiation](https://pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html)：自动求导的官方说明。
- [Vaswani et al., Attention Is All You Need](https://arxiv.org/abs/1706.03762)：第四章将使用本章的矩阵、softmax 和加法解释其中的注意力计算。
