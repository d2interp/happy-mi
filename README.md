# Happy MI：动手学机制可解释性

从一个能亲手拆开的小网络出发，理解神经网络怎样计算。

**[在线阅读](https://d2interp.github.io/happy-mi/)** · [开始学习](https://d2interp.github.io/happy-mi/guide/start.html) · [实验手册](https://d2interp.github.io/happy-mi/labs/) · [提交勘误](https://github.com/d2interp/happy-mi/issues/new/choose)

Happy MI 是面向机制可解释性零基础读者的中文教程。基础篇选择经典问题和方法，将直觉、数学、代码、实验与方法局限连在一起。前两章无需编程，第三章补数学和张量操作；核心实验使用 CPU，不下载大模型。

当前为 **基础篇 v0.1**：12 章正文、5 份核心实验 Notebook、1 个真实 GPT-2 残差修补实验、习题与参考答案。属于持续审阅中的教学初版，不宣称完整复现各篇论文。

## 内容导航

| 部分 | 章节 |
| --- | --- |
| 从问题出发 | [1 我们想解释什么](docs/chapters/01-question.md) · [2 第一个因果实验](docs/chapters/02-first-experiment.md) · [3 数学与代码](docs/chapters/03-math-and-code.md) |
| 读懂计算 | [4 Transformer](docs/chapters/04-transformer.md) · [5 中间计算](docs/chapters/05-reading.md) · [6 线性探针](docs/chapters/06-probes.md) |
| 检验机制 | [7 激活修补](docs/chapters/07-patching.md) · [8 归纳头](docs/chapters/08-induction.md) · [9 IOI 回路](docs/chapters/09-ioi.md) |
| 理解特征 | [10 叠加](docs/chapters/10-superposition.md) · [11 SAE](docs/chapters/11-sae.md) · [12 小项目](docs/chapters/12-project.md) |

配套：[阅读路线](docs/guide/start.md) · [环境准备](docs/guide/setup.md) · [术语表](docs/reference/glossary.md) · [一手文献导读](docs/reference/reading.md) · [习题答案](docs/reference/answers.md)。

## 运行实验

Python 3.11，推荐独立虚拟环境：

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m experiments.run_all
python -m unittest discover -s tests -v
```

结果写入 `artifacts/results.json`。真实 GPT-2 实验需额外安装 `requirements-gpt2.txt` 并下载固定版本权重，见[实验说明](docs/labs/gpt2.md)。

Notebook 位于 `notebooks/`，可独立上传 Colab。它们由 `node scripts/build-notebooks.mjs` 从 Python 实现生成，不手工维护第二份代码。

## 本地阅读与构建

Node.js 22：

```bash
npm ci
npm run docs:dev
# 提交前检查
npm run check
npm run docs:build
```

网站采用 VitePress，默认路径 `/happy-mi/`。部署到其他路径可设 `SITE_BASE`。公式在构建时渲染，搜索索引随站点提供，不依赖第三方搜索服务。

## 参与建设

欢迎报告读不懂的段落、公式错误、实验失败和反例。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。新增材料优先完善已有证据链；前沿论文通常先进入延伸阅读。首版验证范围见 [VALIDATION.md](VALIDATION.md)。

## 致谢与许可

参考 [D2L](https://d2l.ai/)、[Happy LLM](https://github.com/datawhalechina/happy-llm)、[Learn Mechanistic Interpretability](https://github.com/FlyingPumba/learn-mech-interp) 的教材与导航组织，以及 [Neel Nanda Quickstart](https://www.neelnanda.io/mechanistic-interpretability/quickstart-old) 从具体问题出发的学习方式。原始学术来源列在各章。

正文、Notebook 文字与原创图示采用 **[CC BY-NC-SA 4.0](LICENSE)**；可执行代码采用 **[MIT](LICENSE-CODE)**。适用范围见 [LICENSES.md](LICENSES.md)，引用的第三方材料保留各自许可。
