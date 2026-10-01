import React, { useEffect, useState } from 'react';
import { getMMJob, getMMResults, probeMMDataset, runMMDataset } from '../api/client';

const required = ['transfer_id', 'sender', 'receiver', 'amount', 'timestamp', 'label', 'device_id', 'channel'];

export default function DatasetLabPage() {
  const [file, setFile] = useState(null);
  const [probe, setProbe] = useState(null);
  const [mapping, setMapping] = useState({});
  const [settings, setSettings] = useState({ mode: 'train', time_unit: 'steps', seconds_per_step: '', short_window_steps: 1, long_window_steps: 24, dormancy_steps: 30, currency_threshold: '' });
  const [job, setJob] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => { getMMResults().then(setResults).catch(() => {}); }, []);
  useEffect(() => {
    if (!job || ['complete', 'failed'].includes(job.status)) return;
    const timer = setInterval(async () => {
      try {
        const next = await getMMJob(job.job_id);
        setJob({ ...next, job_id: job.job_id });
        if (next.status === 'complete') {
          if (next.result?.mode === 'zero-shot') setResults(next.result);
          else getMMResults().then(setResults).catch(() => {});
        }
      } catch (e) { setError(e.message); }
    }, 2000);
    return () => clearInterval(timer);
  }, [job]);

  async function inspect() {
    if (!file) return;
    setBusy(true); setError('');
    try {
      const p = await probeMMDataset(file);
      setProbe(p); setMapping(p.candidate_column_map || {});
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  async function run() {
    if (!file || !probe) return;
    setBusy(true); setError('');
    try {
      const config = {
        column_map: mapping,
        mode: settings.mode,
        time_unit: settings.time_unit,
        seconds_per_step: settings.seconds_per_step === '' ? null : Number(settings.seconds_per_step),
        short_window_steps: Number(settings.short_window_steps),
        long_window_steps: Number(settings.long_window_steps),
        dormancy_steps: Number(settings.dormancy_steps),
        currency_threshold: settings.currency_threshold === '' ? null : Number(settings.currency_threshold),
        split: 'time',
      };
      const next = await runMMDataset(file, config);
      setJob(next);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }

  const metricRows = results?.metrics ? Object.entries(results.metrics) : [];
  return <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
    <div>
      <h1 className="text-2xl font-semibold text-white">Money Movement Dataset Lab</h1>
      <p className="text-sm text-zinc-400 mt-2">Train and compare HDC and XGBoost on chronological raw transfers. Confirm every column mapping before running.</p>
    </div>
    <section className="rounded-lg border border-[#1e2536] bg-[#0b0e14] p-5 space-y-4">
      <div className="flex flex-wrap gap-3 items-center">
        <input type="file" accept=".csv,text/csv" onChange={e => { setFile(e.target.files?.[0] || null); setProbe(null); }} className="text-sm text-zinc-300" />
        <button disabled={!file || busy} onClick={inspect} className="px-4 py-2 rounded bg-cyan-500 text-black text-sm font-semibold disabled:opacity-50">Probe CSV</button>
        {file && <span className="text-xs text-zinc-500">{file.name} · {(file.size/1e6).toFixed(1)} MB</span>}
      </div>
      {probe && <>
        <p className="text-sm text-zinc-300">Sample: {probe.sample_rows.toLocaleString()} rows · {probe.columns.length} columns. Guesses below require confirmation.</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {required.map(key => <label key={key} className="text-xs text-zinc-400">{key}
            <select value={mapping[key] || ''} onChange={e => setMapping({ ...mapping, [key]: e.target.value || null })} className="block mt-1 w-full bg-[#141a25] border border-[#2b3446] rounded p-2 text-zinc-100">
              <option value="">Unavailable</option>{probe.columns.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>)}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          <label className="text-xs text-zinc-400">Mode<select value={settings.mode} onChange={e => setSettings({ ...settings, mode: e.target.value })} className="block mt-1 w-full bg-[#141a25] border border-[#2b3446] rounded p-2 text-zinc-100"><option value="train">Train</option><option value="finetune">Finetune synthetic model</option><option value="zero-shot">Zero-shot</option></select></label>
          <label className="text-xs text-zinc-400">Time unit<select value={settings.time_unit} onChange={e => setSettings({ ...settings, time_unit: e.target.value })} className="block mt-1 w-full bg-[#141a25] border border-[#2b3446] rounded p-2 text-zinc-100"><option value="steps">Steps</option><option value="ISO string">ISO string</option></select></label>
          {['seconds_per_step', 'short_window_steps', 'long_window_steps', 'dormancy_steps', 'currency_threshold'].map(k => <label key={k} className="text-xs text-zinc-400">{k.replaceAll('_', ' ')}<input type="number" value={settings[k]} onChange={e => setSettings({ ...settings, [k]: e.target.value })} className="block mt-1 w-full bg-[#141a25] border border-[#2b3446] rounded p-2 text-zinc-100" /></label>)}
        </div>
        {!mapping.device_id && <p className="text-amber-400 text-xs">No device ID: shared-device signal will be zero.</p>}
        {!mapping.label && <p className="text-amber-400 text-xs">No label: choose zero-shot. Accuracy and recall cannot be measured.</p>}
        {settings.time_unit === 'steps' && settings.seconds_per_step === '' && <p className="text-amber-400 text-xs">Step duration unknown. Velocity and dormancy use relative steps.</p>}
        <button disabled={busy || !mapping.sender || !mapping.receiver || !mapping.amount || !mapping.timestamp || (settings.mode !== 'zero-shot' && !mapping.label)} onClick={run} className="px-4 py-2 rounded bg-red-500 text-white text-sm font-semibold disabled:opacity-50">Run dataset</button>
      </>}
    </section>
    {error && <div role="alert" className="border border-red-500/40 bg-red-500/10 text-red-300 rounded p-4 text-sm">{error}</div>}
    {job && <div className="border border-cyan-500/30 bg-cyan-500/5 rounded p-4 text-sm">Job {job.job_id}: {job.status}{job.error && ` · ${job.error}`}</div>}
    <section className="rounded-lg border border-[#1e2536] bg-[#0b0e14] p-5">
      <h2 className="text-lg font-semibold">Latest held-out result</h2>
      {!results && <p className="text-sm text-zinc-400 mt-3">No MM run yet.</p>}
      {results && <>
        <p className="text-xs text-zinc-400 mt-2">{results.source || 'Unlabeled data'} · {results.split?.test?.toLocaleString() || results.n_scored?.toLocaleString() || 0} scored transfers</p>
        {results.notes?.map((n, i) => <p className="text-xs text-amber-300 mt-1" key={i}>{n}</p>)}
        {metricRows.length > 0 ? <div className="overflow-x-auto mt-4"><table className="w-full text-sm text-left"><thead className="text-zinc-400 border-b border-[#2b3446]"><tr><th className="py-2">Model</th><th>Precision</th><th>Recall</th><th>F1</th><th>PR-AUC</th><th>ROC-AUC</th></tr></thead><tbody>{metricRows.map(([name,m]) => <tr key={name} className="border-b border-[#1e2536]"><td className="py-2 uppercase">{name}</td>{['precision','recall','f1','pr_auc','roc_auc'].map(k => <td key={k}>{m[k] == null ? '—' : (m[k]*100).toFixed(2)}%</td>)}</tr>)}</tbody></table></div> : <p className="text-sm text-zinc-400 mt-3">Unlabeled run: no accuracy claim available.</p>}
        {results.observed_alert_types && <div className="text-sm text-zinc-300 mt-4">Observed subtypes: {Object.entries(results.observed_alert_types).map(([k,v]) => `${k} ${v.count} cases, ${(v.recall*100).toFixed(1)}% recall`).join(' · ')}</div>}
      </>}
    </section>
  </div>;
}
