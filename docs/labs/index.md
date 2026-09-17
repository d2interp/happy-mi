# 实验手册

核心实验都可以在 CPU 上运行，没有语言模型下载。请从仓库根目录执行命令，并先完成[环境准备](../guide/setup.md)。本页给出实验入口与观察要点，运行结果和图见[首版实测记录](./results.md)。

| 实验 | 命令 | 应该检查什么 |
| --- | --- | --- |
| 双节点干预 | `python -m experiments.first_intervention` | 两节点都记录输入，只有一个影响输出 |
| 线性探针 | `python -m experiments.probes` | 测试准确率、随机标签控制、下游预测是否改变 |
| 归纳复制规则 | `python -m experiments.induction` | 当前 token 匹配前驱信息，再读取后继 |
| 叠加小模型 | `python -m experiments.superposition` | 独立测试误差、零基线、方向几何 |
| 合成字典 SAE | `python -m experiments.sae` | 重构、稀疏度、死隐元、字典匹配 |

一次运行全部实验并保存记录：

```bash
python -m experiments.run_all
```

## Notebook 入口

每份 Notebook 都从相应 Python 源文件生成，包含解释、完整代码和观察问题。核心 Notebook 可以独立上传到 Colab，不需要先克隆仓库；依赖安装单元会联网安装固定版本。第一个实验只使用 Python 标准库。

- [01 第一个因果实验](https://colab.research.google.com/github/d2interp/happy-mi/blob/main/notebooks/01-first-intervention.ipynb)
- [02 线性探针](https://colab.research.google.com/github/d2interp/happy-mi/blob/main/notebooks/02-probes.ipynb)
- [03 归纳复制规则](https://colab.research.google.com/github/d2interp/happy-mi/blob/main/notebooks/03-induction.ipynb)
- [04 叠加小模型](https://colab.research.google.com/github/d2interp/happy-mi/blob/main/notebooks/04-superposition.ipynb)
- [05 稀疏自编码器](https://colab.research.google.com/github/d2interp/happy-mi/blob/main/notebooks/05-sae.ipynb)

## 如何记录一次改动

先保存默认参数的结果，再只改变一个条件。例如将叠加实验的非零概率从 0.1 改为 0.2；其他维度、样本数、种子与训练步数保持不变。解释的是这些具体条件下的差异，不应把一次结果当作普遍定律。

默认核心实验使用种子 42。要查看训练对初始化是否敏感，可以在 Notebook 中运行 `run(seed=7)`；归纳复制和双节点实验是确定性构造，没有训练随机性。

## 真实模型入口

[GPT-2 残差修补](./gpt2.md)需要额外依赖与预训练权重。它使用同一个模板下的四组名字，只是探索性教学样例；小项目中应增加独立模板、名字和对照。
