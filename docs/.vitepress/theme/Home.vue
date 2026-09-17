<script setup>
import { withBase } from 'vitepress'
import CausalPlayground from './CausalPlayground.vue'
const parts = [
  { n: '01—03', title: '从问题出发', desc: '什么算解释？先做一个实验，再补够用的数学与代码。', href: '/chapters/01-question' },
  { n: '04—06', title: '读懂模型的计算', desc: '走进 Transformer，读取中间状态，认识探针的能力与边界。', href: '/chapters/04-transformer' },
  { n: '07—09', title: '用实验检验机制', desc: '学习激活修补，沿着归纳头和 IOI 理解经典回路。', href: '/chapters/07-patching' },
  { n: '10—12', title: '从神经元到特征', desc: '理解叠加与稀疏自编码器，完成自己的第一份研究报告。', href: '/chapters/10-superposition' }
]
</script>

<template>
  <main class="book-home">
    <section class="opening">
      <div class="opening-copy">
        <p class="edition">中文机制可解释性教程 · 基础篇 v0.1</p>
        <h1>模型答对了。<br>它是怎么算的？</h1>
        <p class="subtitle">Happy MI：动手学机制可解释性</p>
        <p class="intro">从一个能亲手拆开的小网络出发，学习观察、提出假设，再用实验检验。一步步走进神经网络的内部计算。</p>
        <div class="home-actions">
          <a class="primary" :href="withBase('/guide/start.html')">开始学习</a>
          <a class="secondary" href="#curriculum">浏览全书目录</a>
        </div>
        <p class="entry-note">无需可解释性基础 · 核心实验可用 CPU · 免费在线阅读</p>
      </div>
      <div class="opening-lab">
        <CausalPlayground />
        <p class="lab-caption">先试试看：一个能读出信息的节点，一定会影响答案吗？</p>
      </div>
    </section>
    <section id="curriculum" class="curriculum">
      <div class="section-intro"><h2>一条循序渐进的学习路线</h2><p>12 章，围绕经典问题展开。每章都有练习、方法边界与一手文献。</p></div>
      <div class="part-list">
        <a v-for="part in parts" :key="part.n" :href="withBase(part.href + '.html')" class="part-link">
          <span class="part-number">{{ part.n }} 章</span><h3>{{ part.title }}</h3><p>{{ part.desc }}</p><span class="part-action">进入本部分</span>
        </a>
      </div>
    </section>
    <section class="reading-note">
      <h2>把解释写成可以被检验的预测。</h2>
      <p>我们会看激活、画注意力图，也会追问：换一组输入还成立吗？改变这个组件，结果真的会变吗？一幅漂亮的图只是起点。</p>
      <a :href="withBase('/chapters/02-first-experiment.html')">从第一个因果实验开始</a>
    </section>
  </main>
</template>
