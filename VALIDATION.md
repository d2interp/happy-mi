# 首版验证范围

参考环境：macOS arm64、Python 3.11.15、PyTorch 2.8.0、NumPy 2.3.3、Node.js 22。发布记录来自实际运行，见 `docs/public/results/`。

## 已验证

- 5 个核心实验可运行；探针随机标签控制、下游不变性、重构基线与稀疏性检查。
- 6 项单元检查覆盖干预方向、未使用坐标、零分母、因果复制限制与解码器尺度。
- 5 份生成的 Notebook 在同一 CPU 环境顺序执行通过；安装单元由依赖安装覆盖，不重复联网安装。
- 真实 GPT-2，固定模型 revision，四组名字、同一模板；每层自我修补与最终残差修补完整性检查。
- 22 个页面的静态构建与本地 Markdown 链接。
- 桌面 1440px 与移动端 390px：交互、重置、导航、中文搜索、数学渲染、图片、横向溢出及深色模式。
- GitHub Actions 重新运行核心实验、Notebook、站点构建和浏览器检查，通过后部署。

## 没有据此声称的结果

- 没有完整复现 IOI 原论文的头级回路或路径实验。
- 没有在 GPT-2 激活上训练本书 SAE；SAE 实验使用合成字典。
- 没有验证多模型、跨语言、所有模板上的泛化。
- 没有独立的学术同行评审，也没有充分的零基础读者试学。
- Notebook 代码已本地执行，但未逐份在当前 Colab 托管环境中验证安装兼容性。

## 构建依赖

VitePress 固定为 1.6.4。对其传递依赖 `vite`、`esbuild` 和公式工具的 `@xmldom/xmldom` 使用修补版本覆盖，并重新验证构建与浏览器行为。发布的是静态 HTML/CSS/JS，不把开发服务器暴露为线上服务。

## 重复验证

```bash
npm ci
node scripts/build-notebooks.mjs
npm run check
npm run docs:build
npx playwright install chromium
npm run test:web
python -m unittest discover -s tests -v
python -m experiments.run_all
python scripts/check-results.py artifacts/results.json
python scripts/check-notebooks.py
```

真实模型实验单独执行 `python -m experiments.gpt2_patching`。图表通过 `python scripts/publish-results.py` 从测量文件生成；不要把改变后的参数结果与旧图混用。
