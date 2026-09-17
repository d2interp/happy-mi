import { readdirSync, readFileSync, existsSync } from 'node:fs'
import path from 'node:path'

const root = process.cwd()
function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(e => e.name.startsWith('.') ? [] : e.isDirectory() ? walk(path.join(dir, e.name)) : [path.join(dir, e.name)])
}
const files = walk(path.join(root, 'docs')).filter(p => p.endsWith('.md'))
const chapters = files.filter(p => p.includes('/chapters/'))
const errors = []
if (chapters.length !== 12) errors.push(`Expected 12 chapters, found ${chapters.length}`)
for (const file of files) {
  const text = readFileSync(file, 'utf8')
  if (file.includes('/chapters/')) {
    for (const required of ['## 小结', '## 练习', '## 一手文献', '这个方法会怎样误导我们']) {
      if (!text.includes(required)) errors.push(`${file}: missing ${required}`)
    }
    if (text.length < 1600) errors.push(`${file}: chapter unexpectedly short`)
  }
  if (/TODO|待补充|Coming soon/.test(text)) errors.push(`${file}: unfinished placeholder`)
  for (const match of text.matchAll(/!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)/g)) {
    const href = match[1].split('#')[0]
    if (!href || /^(https?:|mailto:)/.test(href)) continue
    const target = href.startsWith('/') ? path.join(root, 'docs/public', href) : path.resolve(path.dirname(file), href)
    if (!existsSync(target)) errors.push(`${file}: missing link ${href}`)
  }
}
for (const file of walk(path.join(root, 'notebooks')).filter(p => p.endsWith('.ipynb'))) {
  const nb = JSON.parse(readFileSync(file, 'utf8'))
  if (nb.nbformat !== 4 || !nb.cells.length) errors.push(`${file}: invalid notebook`)
}
if (errors.length) { console.error(errors.join('\n')); process.exit(1) }
console.log(`Checked ${files.length} pages, ${chapters.length} chapters and local Markdown links.`)
