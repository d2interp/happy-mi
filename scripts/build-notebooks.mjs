import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const seedCode = `import random\nimport numpy as np\nimport torch\n\ndef seed_all(seed=42):\n    random.seed(seed)\n    np.random.seed(seed)\n    torch.manual_seed(seed)\n    torch.set_num_threads(1)\n`
const labs = [
  ['01-first-intervention', 'first_intervention', '第一个因果实验', '手工构造网络，不是语言模型实测。先预测：分别把 h1、h2 置零会发生什么？', false, '将输出改为 2 * h[1] - 1，再预测并运行。'],
  ['02-probes', 'probes', '线性探针', '合成数据中，下游只使用第一个坐标，探针读取第二个坐标。先预测探针准确率与干预效应是否一致。', true, '运行 run(seed=7)，比较随机标签控制与正常标签的测试准确率。'],
  ['03-induction', 'induction', '归纳复制规则', '手工编写的离散复制规则，并非训练得到的注意力头。先写出 A B C D A 的匹配位置。', false, "运行 predict(['A', 'B', 'A', 'C', 'A'])，讨论最近匹配这一人为约定。"],
  ['04-superposition', 'superposition', '叠加小模型', '训练五个稀疏输入特征经过二维瓶颈重构。先预测降低共同激活概率会改变什么。', true, '运行 run(seed=7)，比较方向、零基线与活跃特征误差。不要只看绝对 MSE。'],
  ['05-sae', 'sae', '稀疏自编码器', '在已知合成字典生成的数据上训练 ReLU-L1 SAE。真实字典只用于评估，不提供给训练器。', true, '比较两个 lambda 的重构、L0 与字典匹配；再更换随机种子。']
]
const md = text => ({ cell_type: 'markdown', metadata: {}, source: text.split('\n').map((s, i, a) => s + (i < a.length - 1 ? '\n' : '')) })
const code = (text, metadata = {}) => ({ cell_type: 'code', metadata, execution_count: null, outputs: [], source: text.split('\n').map((s, i, a) => s + (i < a.length - 1 ? '\n' : '')) })
mkdirSync(path.join(root, 'notebooks'), { recursive: true })
for (const [file, module, title, intro, needsTorch, question] of labs) {
  let source = readFileSync(path.join(root, 'experiments', module + '.py'), 'utf8')
    .replace('from .common import seed_all\n', '')
    .replace(/\nif __name__ == '__main__':[\s\S]*$/, '')
  const cells = [md(`# ${title}\n\nHappy MI：动手学机制可解释性\n\n${intro}\n\n正文与图示 CC BY-NC-SA 4.0；代码 MIT。实现由 experiments/${module}.py 自动生成。`)]
  if (needsTorch) {
    cells.push(md('## 环境\n\n以下单元会联网安装固定教学依赖。如果运行时提示重启，请重启后从下一节开始。推荐 Python 3.11。'))
    cells.push(code('import subprocess, sys\nsubprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==2.3.3", "torch==2.8.0"])', { tags: ['installation'] }))
    cells.push(code(seedCode))
  }
  cells.push(md('## 看懂实现\n\n先读函数，标出输入、被观察或替换的变量、评价指标。此单元只定义函数。'))
  cells.push(code(source))
  cells.push(md('## 运行并检查\n\n保留原始结果，不只保留符合预期的部分。'))
  cells.push(code('result = run()\nprint(json.dumps(result, ensure_ascii=False, indent=2))'))
  cells.push(md(`## 练习\n\n${question}\n\n写下：哪些结果支持你的预测？哪些不支持？这个实验不能说明什么？`))
  const notebook = { cells, metadata: { kernelspec: { display_name: 'Python 3', language: 'python', name: 'python3' }, language_info: { name: 'python', version: '3.11' } }, nbformat: 4, nbformat_minor: 5 }
  // Stable cell ids make regenerated diffs readable.
  notebook.cells.forEach((cell, index) => cell.id = `${file}-${index}`)
  writeFileSync(path.join(root, 'notebooks', file + '.ipynb'), JSON.stringify(notebook, null, 2) + '\n')
}
console.log(`Generated ${labs.length} notebooks from experiment sources.`)
