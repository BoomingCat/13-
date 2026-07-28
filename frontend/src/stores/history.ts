import type { AnalysisResult } from "../api/analysis";

export interface HistoryItem {
  id: string;
  createdAt: string;
  question: string;
  intent: string;
  conclusion: string;
}

const KEY = "datamind-analysis-history";

export function getHistory(): HistoryItem[] {
  try { return JSON.parse(localStorage.getItem(KEY) ?? "[]") as HistoryItem[]; } catch { return []; }
}

export function saveHistory(result: AnalysisResult): void {
  const items = getHistory();
  items.unshift({ id: result.task_id, createdAt: new Date().toLocaleString("zh-CN"), question: result.question, intent: result.intent, conclusion: result.conclusion });
  localStorage.setItem(KEY, JSON.stringify(items.slice(0, 50)));
}

export function clearHistory(): void { localStorage.removeItem(KEY); }

