# 环境准备

如果你只是阅读正文和使用网页中的交互实验，无需安装任何软件。要运行 Python 实验，再完成下面的准备。

## 推荐环境

核心实验使用 Python 3.11、NumPy 2.3.3 和 PyTorch 2.8.0，默认在 CPU 上运行，不下载语言模型。我们固定教学版本以便复现；这些版本不代表最新版本。不同硬件和线程数仍可能带来细微数值差异。

安装 [Python 3.11](https://www.python.org/downloads/) 和 [Git](https://git-scm.com/downloads) 后，在终端执行：

```bash
git clone https://github.com/d2interp/happy-mi.git
cd happy-mi
python3.11 -m venv .venv
```

macOS / Linux 激活环境：

```bash
source .venv/bin/activate
```

Windows PowerShell 创建、激活环境：

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

然后安装核心依赖并运行第一个实验：

```bash
python -m pip install -r requirements.txt
python -m experiments.first_intervention
```

你应当看到原始、消融和修补三种结果。原始输入 `x=1` 的分数为 `1`；将第一个节点置零得到 `-1`，将第二个节点置零仍得到 `1`。详细解释见[第二章](../chapters/02-first-experiment.md)。

## 运行完整核心实验

```bash
python -m experiments.run_all
python -m unittest discover -s tests -v
```

实验会把结果写入 `artifacts/results.json`，包括随机种子、依赖版本、测量值和运行时间。文件可保留在本地；它默认不会被提交到 Git。网页不会在浏览器里训练 PyTorch 模型。

`experiments/` 中的 Python 文件是实现来源，Notebook 提供按步骤学习的入口。先理解每个单元，再修改一个参数比较结果。运行时间依赖机器，以自己的计时为准，不能把作者机器上的时间当作保证。

## Notebook 与 Colab

仓库 `notebooks/` 提供入门 Notebook。可以在本地 Jupyter 中打开，也可以在 [Colab](https://colab.research.google.com/) 选择“文件 → 打开笔记本 → GitHub”，填入 `d2interp/happy-mi`。Notebook 自带完整代码，无需克隆仓库；涉及 PyTorch 的安装单元会联网安装固定版本依赖。

Colab 的 Python 和预装库会变化；安装后如提示需要重启，请先重启运行时再从实验单元开始。核心实验不需要切换 GPU。如果访问 GitHub 或模型源失败，先把报错中的域名和网络问题定位清楚，避免反复重装整个环境。

## 真实 GPT-2 实验

这个实验额外下载预训练权重，需要网络、磁盘空间和比核心实验更多的内存。先完成第七章，再按 [GPT-2 实验手册](../labs/gpt2.md)运行。它不属于每次网站构建都执行的核心检查。

```bash
python -m pip install -r requirements-gpt2.txt
python -m experiments.gpt2_patching
```

## 为网站贡献内容

只修改和预览正文时，不需要 Python 环境。安装 Node.js 22 后：

```bash
npm ci
npm run docs:dev
```

打开终端显示的 `/happy-mi/` 地址。提交前运行 `npm run check` 和 `npm run docs:build`，检查正文结构与静态构建。发布到 GitHub Pages 由仓库工作流完成。

## 常见问题

**提示找不到 torch。** 用 `python -m pip --version` 检查安装器是否属于 `.venv`；不要混用系统 Python 与虚拟环境。

**没有可用 GPU。** 核心实验本来就使用 CPU。不要为运行本书的小矩阵实验购买算力。

**结果与示例略有不同。** 先比对随机种子、版本、训练步数和数据划分。优化器的有限步训练不保证每次得到同一个几何排列。

**想用更新的库。** 可以在独立环境尝试，并记录版本。若发现兼容问题，请附最短复现、操作系统和完整报错。
