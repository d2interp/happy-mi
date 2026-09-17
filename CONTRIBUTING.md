# 参与 Happy MI

欢迎以勘误、读者反馈、代码修复、实验复核或正文改进的方式参与。可以先提交 Issue 描述问题；小修正可直接提交 Pull Request。

## 教学原则

1. 先提具体问题，再引入解决它所需的概念；首次出现术语给中英对照。
2. 主线选择经典且有清楚证据的方法；新论文通常放延伸阅读。
3. 每章有小结、练习、一手文献和方法边界；不要把相关性、读出与因果作用混为一谈。
4. 示例必须标明是手工构造、合成训练还是真实模型实验。
5. 公式采用行向量右乘约定，并说明张量形状。
6. 不粘贴未获得合适许可的他人图片或代码；引用应指向支持论断的一手来源。

## 修改代码与正文

正文在 `docs/`，核心代码在 `experiments/`。修改 Python 后用 `node scripts/build-notebooks.mjs` 更新 Notebook。生成文件保留可读文字和完整实现，避免正文与实验漂移。

```bash
npm run check
npm run docs:build
python -m unittest discover -s tests -v
python -m experiments.run_all
```

修改网页交互时额外执行 `npm run test:web`；首次需要 `npx playwright install chromium`。涉及真实 GPT-2 实验时按实验手册单独验证，并记录模型与依赖版本。

不要用新的实验结果静默覆盖 `docs/public/results/` 中已发布的记录；需要明确更新日期、参数、图和说明。CI 会重新运行核心实验，但不要求跨平台每一位浮点数相同。

## 提交说明

说明修改解决什么读者问题、涉及哪些章节、如何验证。研究结论的修正附原始来源或反例；实验问题附环境、命令与结果。较大的新章节先讨论教学位置和先修知识。

## 许可

贡献正文、Notebook 文字与原创图示时，同意以 CC BY-NC-SA 4.0 发布；贡献可执行代码时，同意以 MIT 发布。你应拥有贡献内容的相关权利，并保留第三方署名与许可说明。详细范围见 `LICENSE` 与 `LICENSE-CODE`。
