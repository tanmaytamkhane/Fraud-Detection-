import React, { useEffect, useState } from 'react';
import { getMMRedTeamJob, getMMRedTeamResults, startMMRedTeam } from '../api/client';

const variants = ['MM-V1', 'MM-V2', 'MM-V3', 'MM-V4'];

export default function MMRedTeamPage() {
  const [selected, setSelected] = useState(variants);
  const [attempts, setAttempts] = useState(10);
  const [job, setJob] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { getMMRedTeamResults().then(setResult).catch(() => {}); }, []);
  useEffect(() => {
    if (!job || ['complete','failed'].includes(job.status)) return;
    const timer = setInterval(async () => {
      try {
        const next = await getMMRedTeamJob(job.job_id);
        setJob({ ...next, job_id: job.job_id });
        if (next.status === 'complete') setResult(next.result);
      } catch (e) { setError(e.message); }
    }, 3000);
    return () => clearInterval(timer);
  }, [job]);
  async function start() {
    setError('');
    try { setJob(await startMMRedTeam({ variants: selected, n_attempts_per_variant: attempts })); }
    catch (e) { setError(e.message); }
  }
  return <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
    <h1 className="text-2xl font-semibold">Money Movement Red Team</h1>
    <p className="text-sm text-zinc-400">Synthetic raw-transfer stress test of the synthetic MM model. Results measure this simulator, not real-world evasion. Dense background graph cycles may trigger broad chain actions; inspect legitimate false positives before interpreting low evasion rates.</p>
    <div className="border border-[#1e2536] bg-[#0b0e14] rounded p-5 space-y-4">
      <div className="flex flex-wrap gap-4">{variants.map(v => <label key={v} className="text-sm text-zinc-300"><input type="checkbox" checked={selected.includes(v)} onChange={() => setSelected(selected.includes(v) ? selected.filter(x => x !== v) : [...selected, v])} /> {v}</label>)}</div>
      <label className="text-sm text-zinc-300">Attempts per variant: {attempts}<input className="block w-64 mt-2" type="range" min="1" max="50" value={attempts} onChange={e => setAttempts(Number(e.target.value))} /></label>
      <button onClick={start} disabled={!selected.length || (job && ['queued','running'].includes(job.status))} className="rounded bg-red-500 text-white text-sm font-semibold px-4 py-2 disabled:opacity-50">Run 5-level sweep</button>
      {job && <p className="text-xs text-cyan-300">Job {job.job_id}: {job.status}{job.error && ` · ${job.error}`}</p>}
      {error && <p role="alert" className="text-xs text-red-300">{error}</p>}
    </div>
    <div className="border border-[#1e2536] bg-[#0b0e14] rounded p-5 overflow-x-auto">
      <h2 className="font-semibold mb-3">Latest sweep</h2>
      {!result && <p className="text-sm text-zinc-400">No run yet.</p>}
      {result && <><p className="text-xs text-amber-300 mb-3">{result.warning}</p><table className="w-full text-sm text-left"><thead className="text-zinc-400 border-b border-zinc-700"><tr><th className="py-2">Variant</th><th>Evasion level</th><th>Rings</th><th>Evasion rate</th><th>Mean peak score</th></tr></thead><tbody>{result.table.map((r,i) => <tr key={i} className="border-b border-zinc-800"><td className="py-2">{r.variant}</td><td>{(r.evasion_level*100).toFixed(0)}%</td><td>{r.rings}</td><td>{(r.evasion_rate*100).toFixed(1)}%</td><td>{(r.mean_peak_risk*100).toFixed(1)}%</td></tr>)}</tbody></table></>}
    </div>
  </div>;
}
