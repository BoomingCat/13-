<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref } from "vue";
import * as echarts from "echarts";
import { analyze, type AnalysisResult } from "../api/analysis";
import { saveHistory } from "../stores/history";

const examples = ["统计每条产线最近7天的产量趋势", "分析各工序本月良率", "统计各设备停机时间", "找出低于安全库存的产品"];
const question = ref(examples[0]);
const loading = ref(false);
const result = ref<AnalysisResult>();
const chartElement = ref<HTMLDivElement>();
let chart: echarts.ECharts | undefined;

async function submit() {
  if (!question.value.trim() || loading.value) return;
  loading.value = true;
  try {
    result.value = await analyze(question.value.trim());
    saveHistory(result.value);
    await nextTick();
    if (chartElement.value && result.value.chart) {
      chart?.dispose(); chart = echarts.init(chartElement.value); chart.setOption(result.value.chart.option);
    }
  } finally { loading.value = false; }
}

onBeforeUnmount(() => chart?.dispose());
</script>

<template>
  <section class="hero">
    <div class="mode-tag">LOCAL ANALYSIS ENGINE</div>
    <h2>用自然语言，直接分析企业数据</h2>
    <p>当前使用规则引擎和本地演示数据，已保留 DeepSeek 与后端 API 接入口。</p>
    <div class="prompt"><textarea v-model="question" @keydown.ctrl.enter="submit"/><button :disabled="loading" @click="submit">{{ loading ? "分析中…" : "开始分析" }}</button></div>
    <div class="examples"><button v-for="item in examples" :key="item" @click="question = item">{{ item }}</button></div>
  </section>

  <template v-if="result">
    <section class="grid two-col">
      <article class="card"><div class="card-title"><h3>执行轨迹</h3><span>{{ result.steps.length }} 步</span></div><ol class="steps"><li v-for="step in result.steps" :key="step.name"><i>✓</i><div><strong>{{ step.name }}</strong><p>{{ step.detail }}</p></div></li></ol></article>
      <article class="card conclusion"><div class="card-title"><h3>智能结论</h3><span>{{ result.intent }}</span></div><p>{{ result.conclusion }}</p><div class="notice">演示结果来自本地数据，不调用任何外部模型。</div></article>
    </section>
    <section class="card spaced"><div class="card-title"><h3>{{ result.chart?.title }}</h3><span>可视化结果</span></div><div ref="chartElement" class="chart"></div></section>
    <section class="card spaced"><div class="card-title"><h3>结果数据</h3><span>{{ result.rows.length }} 行</span></div><div class="table-wrap"><table><thead><tr><th v-for="col in result.columns" :key="col">{{ col }}</th></tr></thead><tbody><tr v-for="(row, index) in result.rows" :key="index"><td v-for="(cell, i) in row" :key="i">{{ cell }}</td></tr></tbody></table></div></section>
    <section class="card spaced"><div class="card-title"><h3>生成的 SQL</h3><span class="success">只读校验通过</span></div><pre>{{ result.sql }}</pre></section>
  </template>
  <section v-else class="empty-state"><div>⌁</div><h3>输入问题开始分析</h3><p>你可以从上方四个示例问题开始。</p></section>
</template>

