<script setup lang="ts">
import { ref } from "vue";
import { clearHistory, getHistory } from "../stores/history";
const items = ref(getHistory());
function clear() { if (confirm("确认清空全部历史记录吗？")) { clearHistory(); items.value = []; } }
</script>
<template><div class="page-toolbar"><div><h2>分析历史</h2><p>浏览保存在当前浏览器中的分析记录。</p></div><button class="secondary" :disabled="!items.length" @click="clear">清空记录</button></div><section v-if="items.length" class="history-list"><article v-for="item in items" :key="item.id" class="card history-item"><div><span class="category">{{ item.intent }}</span><time>{{ item.createdAt }}</time></div><h3>{{ item.question }}</h3><p>{{ item.conclusion }}</p><small>任务编号：{{ item.id }}</small></article></section><section v-else class="empty-state"><div>◷</div><h3>暂无分析记录</h3><p>在智能问析页面完成分析后，记录会自动保存在这里。</p></section></template>

