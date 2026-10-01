const CLOUD_BACKEND_URL = 'https://fraud-detection-tu4w.onrender.com';

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  (typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'
    : CLOUD_BACKEND_URL)
).replace(/\/+$/, '');

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getAllCategories() {
  const res = await fetch(`${API_BASE_URL}/all-categories`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getAllBenchmarks() {
  const res = await fetch(`${API_BASE_URL}/all-benchmarks`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getCategoryBenchmarks(catCode) {
  const res = await fetch(`${API_BASE_URL}/category-benchmarks/${catCode}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanCategory(catCode, signals) {
  const res = await fetch(`${API_BASE_URL}/scan-category/${catCode}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(signals),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanCategoryPreset(catCode, variantId) {
  const res = await fetch(`${API_BASE_URL}/scan-category-preset/${catCode}/${variantId}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

// ─── Individual Category Endpoints ──────────────────────────────────────────

export async function getVariants() {
  const res = await fetch(`${API_BASE_URL}/variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getMuleVariants() {
  const res = await fetch(`${API_BASE_URL}/mule-variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getGenAIVariants() {
  const res = await fetch(`${API_BASE_URL}/genai-variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getSocVariants() {
  const res = await fetch(`${API_BASE_URL}/soc-variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getPmVariants() {
  const res = await fetch(`${API_BASE_URL}/pm-variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getTbVariants() {
  const res = await fetch(`${API_BASE_URL}/tb-variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getMrfVariants() {
  const res = await fetch(`${API_BASE_URL}/mrf-variants`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getBenchmarks() {
  const res = await fetch(`${API_BASE_URL}/benchmarks`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getMuleBenchmarks() {
  return getCategoryBenchmarks('MM');
}

export async function getGenAIBenchmarks() {
  return getCategoryBenchmarks('GENAI');
}

export async function scanTransaction(signals) {
  const res = await fetch(`${API_BASE_URL}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(signals),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanPreset(variantId) {
  const res = await fetch(`${API_BASE_URL}/scan-preset/${variantId}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanTransfer(transferData) {
  const res = await fetch(`${API_BASE_URL}/scan-transfer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transferData),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanMulePreset(variantId) {
  const res = await fetch(`${API_BASE_URL}/scan-mule-preset/${variantId}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanGenAI(biometricSignals) {
  const res = await fetch(`${API_BASE_URL}/scan-genai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(biometricSignals),
  });
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function scanGenAIPreset(variantId) {
  const res = await fetch(`${API_BASE_URL}/scan-genai-preset/${variantId}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getMuleGraph(txId) {
  const res = await fetch(`${API_BASE_URL}/mule-graph/${txId}`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getMMGraph(account) {
  const res = await fetch(`${API_BASE_URL}/mm/graph/${encodeURIComponent(account)}`);
  if (!res.ok) throw new Error(`MM graph: ${res.status}`);
  return res.json();
}

export async function getMMResults() {
  const res = await fetch(`${API_BASE_URL}/mm/results`);
  if (!res.ok) throw new Error(`MM results: ${res.status}`);
  return res.json();
}

export async function getMMStream() {
  const res = await fetch(`${API_BASE_URL}/mm/stream`);
  if (!res.ok) throw new Error(`MM stream: ${res.status}`);
  return res.json();
}

export async function probeMMDataset(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE_URL}/mm/dataset/probe`, { method: 'POST', body: form });
  if (!res.ok) throw new Error((await res.json()).detail || `Probe failed: ${res.status}`);
  return res.json();
}

export async function runMMDataset(file, config) {
  const form = new FormData();
  form.append('file', file);
  form.append('config', JSON.stringify(config));
  const res = await fetch(`${API_BASE_URL}/mm/dataset/run`, { method: 'POST', body: form });
  if (!res.ok) throw new Error((await res.json()).detail || `Run failed: ${res.status}`);
  return res.json();
}

export async function getMMJob(id) {
  const res = await fetch(`${API_BASE_URL}/mm/dataset/job/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Job: ${res.status}`);
  return res.json();
}

export async function startMMRedTeam(payload) {
  const res = await fetch(`${API_BASE_URL}/mm/red-team`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error((await res.json()).detail || `Red team failed: ${res.status}`);
  return res.json();
}

export async function getMMRedTeamJob(id) {
  const res = await fetch(`${API_BASE_URL}/mm/red-team/job/${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error(`Red-team job: ${res.status}`);
  return res.json();
}

export async function getMMRedTeamResults() {
  const res = await fetch(`${API_BASE_URL}/mm/red-team/results`);
  if (!res.ok) throw new Error(`No red-team run: ${res.status}`);
  return res.json();
}

export async function generateMMCampaign(payload) {
  const res = await fetch(`${API_BASE_URL}/mm/generate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  if (!res.ok) throw new Error((await res.json()).detail || `MM generation failed: ${res.status}`);
  return res.json();
}

export async function getContract() {
  const res = await fetch(`${API_BASE_URL}/contract`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}


export async function getAttacks() {
  const res = await fetch(`${API_BASE_URL}/attacks`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE_URL}/stats`);
  if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
  return res.json();
}
