import { defineConfig } from 'vitepress'

const base = process.env.SITE_BASE || '/happy-mi/'

export const chapters = [
  ['01-question', '1. 我们想解释什么'],
  ['02-first-experiment', '2. 第一个因果实验'],
  ['03-math-and-code', '3. 够用的数学与代码'],
  ['04-transformer', '4. 从预测词到 Transformer'],
  ['05-reading', '5. 观察模型的中间计算'],
  ['06-probes', '6. 探针：读得出，就用到了吗'],
  ['07-patching', '7. 用干预检验假设'],
  ['08-induction', '8. 归纳头：一个复制算法'],
  ['09-ioi', '9. IOI：从组件到回路'],
  ['10-superposition', '10. 叠加：特征多于维度'],
  ['11-sae', '11. 稀疏自编码器'],
  ['12-project', '12. 完成一份可检验的解释']
]

export default defineConfig({
  lang: 'zh-CN',
  title: 'Happy MI',
  description: '动手学机制可解释性：面向零基础读者的中文教程，结合原理、代码与实验。',
  base,
  cleanUrls: false,
  head: [
    ['meta', { name: 'theme-color', content: '#2359a8' }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}mark.svg` }]
  ],
  markdown: { math: true, lineNumbers: true },
  lastUpdated: true,
  themeConfig: {
    logo: '/mark.svg',
    siteTitle: 'Happy MI',
    nav: [
      { text: '开始学习', link: '/guide/start' },
      { text: '实验手册', link: '/labs/' },
      { text: '术语表', link: '/reference/glossary' },
      { text: '关于', link: '/guide/about' }
    ],
    sidebar: [
      { text: '开始之前', items: [
        { text: '阅读路线', link: '/guide/start' },
        { text: '环境准备', link: '/guide/setup' }
      ] },
      { text: '第一部分 · 从问题出发', items: chapters.slice(0, 3).map(([slug, text]) => ({ text, link: `/chapters/${slug}` })) },
      { text: '第二部分 · 读懂计算', items: chapters.slice(3, 6).map(([slug, text]) => ({ text, link: `/chapters/${slug}` })) },
      { text: '第三部分 · 检验机制', items: chapters.slice(6, 9).map(([slug, text]) => ({ text, link: `/chapters/${slug}` })) },
      { text: '第四部分 · 理解特征', items: chapters.slice(9).map(([slug, text]) => ({ text, link: `/chapters/${slug}` })) },
      { text: '动手与查阅', items: [
        { text: '实验手册', link: '/labs/' },
        { text: '首版实测记录', link: '/labs/results' },
        { text: 'GPT-2 实验', link: '/labs/gpt2' },
        { text: '习题提示与答案', link: '/reference/answers' },
        { text: '符号与术语', link: '/reference/glossary' },
        { text: '一手文献导读', link: '/reference/reading' },
        { text: '关于与贡献', link: '/guide/about' }
      ] }
    ],
    search: {
      provider: 'local',
      options: {
        miniSearch: {
          options: {
            tokenize: (text: string) => text.toLowerCase().match(/[\p{Script=Han}]|[a-z0-9_]+/gu) || []
          },
          searchOptions: { prefix: true, fuzzy: false }
        },
        locales: { root: { translations: {
          button: { buttonText: '搜索教程', buttonAriaLabel: '搜索教程' },
          modal: { noResultsText: '没有找到相关内容', resetButtonTitle: '清空',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' } }
        } } }
      }
    },
    outline: { level: [2, 3], label: '本页内容' },
    docFooter: { prev: '上一章', next: '下一章' },
    darkModeSwitchLabel: '切换深色模式',
    sidebarMenuLabel: '课程目录',
    returnToTopLabel: '回到顶部',
    lastUpdated: { text: '最近更新', formatOptions: { dateStyle: 'medium' } },
    editLink: { pattern: 'https://github.com/d2interp/happy-mi/edit/main/docs/:path', text: '改进这一页' },
    socialLinks: [{ icon: 'github', link: 'https://github.com/d2interp/happy-mi' }],
    footer: { message: '正文 CC BY-NC-SA 4.0 · 代码 MIT', copyright: 'Happy MI · d2interp 社区' }
  }
})
