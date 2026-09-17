# 一手文献导读

基础篇选材以可教学、可检验的经典工作为主。阅读顺序服务于理解，不等于论文的历史顺序。每次精读先回答：它研究什么行为？哪些证据支持机制？哪些部分仍是解释或假说？

## 核心路径

| 阅读阶段 | 原始材料 | 建议关注 |
| --- | --- | --- |
| 开始提问 | [Olah et al., Zoom In (2020)](https://distill.pub/2020/circuits/zoom-in/) | 特征、组件和组合关系 |
| 理解架构 | [Vaswani et al. (2017)](https://arxiv.org/abs/1706.03762) | 注意力公式与掩码 |
| 理解回路框架 | [Elhage et al. (2021)](https://transformer-circuits.pub/2021/framework/index.html) | 残差流、QK/OV、头组合 |
| 学会读出 | [Hewitt & Liang (2019)](https://aclanthology.org/D19-1275/) | 控制任务为什么必要 |
| 学会干预 | [Zhang & Nanda (2023/2024)](https://arxiv.org/abs/2309.16042) | 输入扰动、指标和实验结论 |
| 理解修补 | [Heimersheim & Nanda (2024)](https://arxiv.org/abs/2404.15255) | noising/denoising 与 AND/OR |
| 经典算法 | [Olsson et al. (2022)](https://arxiv.org/abs/2209.11895) | 归纳头的证据链 |
| 经典语言回路 | [Wang et al. (2022/2023)](https://arxiv.org/abs/2211.00593) | IOI 回路与评估 |
| 理解表示容量 | [Elhage et al. (2022)](https://arxiv.org/abs/2209.10652) | 叠加、稀疏性和干扰 |
| 学习字典 | [Bricken et al. (2023)](https://transformer-circuits.pub/2023/monosemantic-features/index.html) | 稀疏字典与特征解释 |

括号中的双年份表示预印本与会议版本的时间，不代表两篇不同论文。正文只使用与教学目标有关的部分；原论文的实验条件应以原文为准。

## 学完基础篇后的四个分支

**更精细的回路。** 从 [Conmy et al., Towards Automated Circuit Discovery (2023)](https://arxiv.org/abs/2304.14997) 理解自动选择组件的目标。随后比较不同基线与评估指标，而不是把自动生成的图视为最终答案。

**训练中形成的算法。** [Nanda et al., Progress measures for grokking via mechanistic interpretability (2023)](https://arxiv.org/abs/2301.05217) 在模加法任务中分析学习到的计算。它适合已经熟悉基础线性代数、愿意进一步学习傅里叶视角的读者。

**SAE 的训练与评价。** 阅读 [Gao et al. (2024)](https://arxiv.org/abs/2406.04093) 的 TopK 与评价方法，再读 [Rajamanoharan et al. (2024)](https://arxiv.org/abs/2407.14435) 的 JumpReLU。不要只比较重构误差，需同时比较稀疏度与行为影响。

**从特征到更大计算图。** [Circuit Tracing (2025)](https://transformer-circuits.pub/2025/attribution-graphs/methods.html) 是了解替换模型和归因图的延伸材料。它不属于基础篇必修内容，阅读时特别注意替换误差与分析时的近似。

## 配合学习的资源

[Neel Nanda 的 Quickstart](https://www.neelnanda.io/mechanistic-interpretability/quickstart-old)适合选择一个具体问题后随时回看。[Learn Mechanistic Interpretability](https://learnmechinterp.com/)提供更广的主题导航。[D2L](https://d2l.ai/)可以补深度学习基础，[Happy LLM](https://github.com/datawhalechina/happy-llm)可以补中文语言模型背景。

这些资源的章节范围和工具版本会变化。本教程的可复现环境以仓库依赖文件为准，不把旧教程里的安装命令当作当前工具 API 的保证。
