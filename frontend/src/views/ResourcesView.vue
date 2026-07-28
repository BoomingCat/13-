<script setup lang="ts">
import { computed, ref } from "vue";
import { tables, type TableItem } from "../data/catalog";
const keyword = ref("");
const selected = ref<TableItem>(tables[0]);
const filtered = computed(() => tables.filter(item => `${item.name}${item.displayName}${item.category}`.includes(keyword.value)));
</script>

<template>
  <div class="page-toolbar"><div><h2>数据资源中心</h2><p>查看企业数据底座中的表、字段、类型和业务含义。</p></div><button class="primary">同步元数据</button></div>
  <section class="resource-layout"><article class="card resource-list"><input v-model="keyword" placeholder="搜索数据表"/><button v-for="item in filtered" :key="item.name" :class="{ selected: selected.name === item.name }" @click="selected=item"><span class="table-icon">▦</span><div><strong>{{ item.displayName }}</strong><small>{{ item.name }} · {{ item.rows.toLocaleString() }} 行</small></div><em>{{ item.category }}</em></button></article><article class="card resource-detail"><div class="card-title"><div><h3>{{ selected.displayName }}</h3><p>{{ selected.description }}</p></div><span>{{ selected.category }}</span></div><div class="metadata"><div><b>{{ selected.rows.toLocaleString() }}</b><span>数据行数</span></div><div><b>{{ selected.columns.length }}</b><span>字段数量</span></div><div><b>PostgreSQL</b><span>数据来源</span></div></div><h3 class="section-title">字段定义</h3><div class="table-wrap"><table><thead><tr><th>字段名</th><th>类型</th><th>业务说明</th></tr></thead><tbody><tr v-for="col in selected.columns" :key="col.name"><td><code>{{ col.name }}</code></td><td><span class="type">{{ col.type }}</span></td><td>{{ col.description }}</td></tr></tbody></table></div></article></section>
</template>

