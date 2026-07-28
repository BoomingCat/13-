<script setup lang="ts">
import { computed, ref } from "vue";
import AnalysisView from "./views/AnalysisView.vue";
import HistoryView from "./views/HistoryView.vue";
import KnowledgeView from "./views/KnowledgeView.vue";
import ResourcesView from "./views/ResourcesView.vue";

type Page = "analysis" | "knowledge" | "resources" | "history";
const page = ref<Page>("analysis");
const pages = [
  { id: "analysis" as Page, label: "智能问析", icon: "⌁" },
  { id: "knowledge" as Page, label: "业务知识", icon: "◇" },
  { id: "resources" as Page, label: "数据资源", icon: "▦" },
  { id: "history" as Page, label: "分析历史", icon: "◷" },
];
const current = computed(() => pages.find(item => item.id === page.value)!);
const component = computed(() => ({ analysis: AnalysisView, knowledge: KnowledgeView, resources: ResourcesView, history: HistoryView })[page.value]);
</script>

<template>
  <div class="shell">
    <aside>
      <div class="brand"><span>DM</span><div><strong>DataMind</strong><small>企业智能问析平台</small></div></div>
      <nav><button v-for="item in pages" :key="item.id" :class="{ active: page === item.id }" @click="page=item.id"><i>{{ item.icon }}</i>{{ item.label }}</button></nav>
      <div class="system-card"><span class="pulse"></span><div><strong>本地演示模式</strong><small>DeepSeek API 未启用</small></div></div>
    </aside>
    <main>
      <header><div><p class="eyebrow">MANUFACTURING INTELLIGENCE</p><h1>{{ current.label }}</h1></div><div class="header-actions"><span class="badge">API 接口已预留</span><div class="avatar">管</div></div></header>
      <component :is="component"/>
    </main>
  </div>
</template>

