<script setup>
import { computed, ref } from 'vue'
const x = ref(1)
const cutUsed = ref(false)
const cutCopy = ref(false)
const used = computed(() => cutUsed.value ? 0 : Number(x.value))
const copy = computed(() => cutCopy.value ? 0 : Number(x.value))
const score = computed(() => 2 * used.value - 1)
function reset() { x.value = 1; cutUsed.value = false; cutCopy.value = false }
</script>

<template>
  <div class="causal-playground" aria-label="手工构造网络的消融实验">
    <div class="lab-header"><span>动手实验 / 观测与干预</span><button type="button" @click="reset">重置</button></div>
    <p class="lab-description">两个节点都记录输入，但只有一条路径参与输出。</p>
    <svg viewBox="0 0 430 210" role="img" aria-label="输入 x 同时送入 h1 和 h2；输出分数等于 2 乘 h1 减 1，h2 的输出权重为零。">
      <g class="wires" fill="none" stroke-width="2.5">
        <path d="M66 100L190 53" :class="{ cut: cutUsed }"/><path d="M66 100L190 154" :class="{ cut: cutCopy }"/>
        <path d="M220 53L351 100" :class="{ cut: cutUsed }"/><path d="M220 154L351 100" stroke-dasharray="5 6" class="unused"/>
      </g>
      <g class="network-labels"><text x="272" y="49">权重 2</text><text x="274" y="166">权重 0</text></g>
      <g class="nodes"><circle cx="55" cy="100" r="26"/><circle cx="205" cy="48" r="26" :class="{ ablated: cutUsed }"/><circle cx="205" cy="156" r="26" :class="{ ablated: cutCopy }"/><circle cx="371" cy="100" r="26"/></g>
      <g class="node-values" text-anchor="middle" dominant-baseline="central"><text x="55" y="100">{{ x }}</text><text x="205" y="48">{{ used }}</text><text x="205" y="156">{{ copy }}</text><text x="371" y="100">{{ score }}</text></g>
      <g class="network-labels" text-anchor="middle"><text x="55" y="146">输入 x</text><text x="205" y="91">h₁</text><text x="205" y="201">h₂</text><text x="371" y="146">分数 s</text></g>
    </svg>
    <div class="lab-controls">
      <label>输入 x <select v-model.number="x" aria-label="输入 x"><option :value="1">1</option><option :value="0">0</option></select></label>
      <label><input type="checkbox" v-model="cutUsed"> 将 h₁ 置零</label>
      <label><input type="checkbox" v-model="cutCopy"> 将 h₂ 置零</label>
    </div>
    <p class="lab-result" aria-live="polite">输出分数：<strong>{{ score }}</strong>。{{ cutCopy && !cutUsed ? 'h₂ 被置零，输出仍由 h₁ 决定。' : cutUsed ? 'h₁ 被置零，输出分数变为 −1。' : '试着分别将两个节点置零。' }}</p>
    <small>教学构造，非语言模型测量。s = 2h₁ − 1。</small>
  </div>
</template>
