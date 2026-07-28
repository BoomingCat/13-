<script setup lang="ts">
import { computed, ref } from "vue";
import { defaultMetrics, type MetricItem } from "../data/catalog";

const KEY = "datamind-metrics";
const metrics = ref<MetricItem[]>(JSON.parse(localStorage.getItem(KEY) ?? "null") ?? defaultMetrics);
const keyword = ref("");
const editing = ref<MetricItem | null>(null);
const filtered = computed(() => metrics.value.filter(item => `${item.name}${item.code}${item.category}${item.synonyms.join()}`.includes(keyword.value)));
function persist() { localStorage.setItem(KEY, JSON.stringify(metrics.value)); }
function add() { editing.value = { code: "", name: "", description: "", formula: "", category: "生产", synonyms: [] }; }
function edit(item: MetricItem) { editing.value = { ...item, synonyms: [...item.synonyms] }; }
function save() { if (!editing.value?.code || !editing.value.name) return; const index = metrics.value.findIndex(i => i.code === editing.value!.code); if (index >= 0) metrics.value[index] = editing.value; else metrics.value.push(editing.value); persist(); editing.value = null; }
function remove(code: string) { if (confirm("确认删除这个指标吗？")) { metrics.value = metrics.value.filter(i => i.code !== code); persist(); } }
</script>

<template>
  <div class="page-toolbar"><div><h2>业务知识管理</h2><p>维护制造业指标口径、计算公式和同义词。</p></div><button class="primary" @click="add">新增指标</button></div>
  <section class="stats-row"><div class="stat"><b>{{ metrics.length }}</b><span>业务指标</span></div><div class="stat"><b>4</b><span>业务主题</span></div><div class="stat"><b>{{ metrics.reduce((n, i) => n + i.synonyms.length, 0) }}</b><span>指标同义词</span></div></section>
  <section class="card"><div class="filter"><input v-model="keyword" placeholder="搜索指标名称、编码或主题"/></div><div class="table-wrap"><table><thead><tr><th>指标名称</th><th>主题</th><th>指标编码</th><th>计算公式</th><th>同义词</th><th>操作</th></tr></thead><tbody><tr v-for="item in filtered" :key="item.code"><td><strong>{{ item.name }}</strong><small>{{ item.description }}</small></td><td><span class="category">{{ item.category }}</span></td><td><code>{{ item.code }}</code></td><td>{{ item.formula }}</td><td>{{ item.synonyms.join("、") || "-" }}</td><td><button class="text-btn" @click="edit(item)">编辑</button><button class="text-btn danger" @click="remove(item.code)">删除</button></td></tr></tbody></table></div></section>
  <div v-if="editing" class="modal-mask"><form class="modal" @submit.prevent="save"><div class="card-title"><h3>{{ metrics.some(i => i.code === editing?.code) ? "编辑指标" : "新增指标" }}</h3><button type="button" class="close" @click="editing=null">×</button></div><label>指标名称<input v-model="editing.name" required/></label><label>指标编码<input v-model="editing.code" required/></label><label>业务主题<select v-model="editing.category"><option>生产</option><option>质量</option><option>设备</option><option>库存</option></select></label><label>指标说明<textarea v-model="editing.description"/></label><label>计算公式<input v-model="editing.formula"/></label><label>同义词（顿号分隔）<input :value="editing.synonyms.join('、')" @input="editing.synonyms = ($event.target as HTMLInputElement).value.split('、').filter(Boolean)"/></label><div class="modal-actions"><button type="button" @click="editing=null">取消</button><button class="primary" type="submit">保存</button></div></form></div>
</template>

