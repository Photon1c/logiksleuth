import React, { useEffect, useMemo, useState } from 'react'

const api = {
  start: async (body) => fetch('/scan/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then(r => r.json()),
  status: async () => fetch('/scan/status').then(r => r.json()),
  results: async () => fetch('/scan/results').then(r => r.json()),
  getConfig: async () => fetch('/config').then(r => r.json()),
  setConfig: async (body) => fetch('/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }).then(r => r.json()),
  testProcedure: async () => fetch('/test/procedure').then(r => r.json()),
}

function Heatmap({ matrix, labels }) {
  if (!matrix || matrix.length === 0) return <div style={{ padding: 8 }}>No data</div>
  const size = 400
  const n = matrix.length
  const cell = Math.max(2, Math.floor(size / n))
  return (
    <svg width={size} height={size} style={{ border: '1px solid #ddd', background: '#fff' }}>
      {matrix.map((row, i) => row.map((v, j) => {
        const c = Math.max(0, Math.min(255, Math.floor(255 - v * 255)))
        return <rect key={`${i}-${j}`} x={j * cell} y={i * cell} width={cell} height={cell} fill={`rgb(${c},${c},255)`} />
      }))}
    </svg>
  )
}

function Graph({ clusters }) {
  return (
    <div style={{ padding: 8 }}>
      <div>Clusters: {clusters?.length || 0}</div>
      <ol>
        {(clusters || []).slice(0, 10).map((c, i) => (
          <li key={i}>#{i + 1} size={c.size}</li>
        ))}
      </ol>
    </div>
  )
}

export default function App() {
  const [csvPath, setCsvPath] = useState('')
  const [thr, setThr] = useState(0.7)
  const [year, setYear] = useState(5)
  const [geo, setGeo] = useState('')
  const [view, setView] = useState('heatmap')
  const [status, setStatus] = useState({ stage: 'Idle' })
  const [res, setRes] = useState(null)
  const [testRes, setTestRes] = useState(null)

  useEffect(() => {
    const t = setInterval(async () => {
      setStatus(await api.status())
    }, 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    (async () => {
      const cfg = await api.getConfig()
      setCsvPath(cfg.csv_path || '')
      setThr(cfg.similarity_threshold ?? 0.7)
      setYear(cfg.year_window ?? 5)
      setGeo(cfg.geo_window ?? '')
    })()
  }, [])

  const start = async () => {
    await api.start({ csv_path: csvPath, duration_hours: 0.02, similarity_threshold: Number(thr), year_window: Number(year), geo_window: geo ? Number(geo) : null })
    setRes(null)
  }
  const getResults = async () => setRes(await api.results())
  const saveConfig = async () => {
    const cfg = await api.setConfig({ csv_path: csvPath, similarity_threshold: Number(thr), year_window: Number(year), geo_window: geo ? Number(geo) : null })
    setThr(cfg.similarity_threshold)
    setYear(cfg.year_window)
    setGeo(cfg.geo_window ?? '')
  }
  const runTest = async () => setTestRes(await api.testProcedure())

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', padding: 16 }}>
      <h2>CaseLinker (Advanced)</h2>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <label>CSV <input value={csvPath} onChange={e => setCsvPath(e.target.value)} style={{ width: 260 }} /></label>
        <label>Similarity <input type="number" step="0.01" min="0" max="1" value={thr} onChange={e => setThr(e.target.value)} style={{ width: 80 }} /></label>
        <label>Year window <input type="number" min="0" value={year} onChange={e => setYear(e.target.value)} style={{ width: 80 }} /></label>
        <label>Geo window (CNTYFIPS diff) <input type="number" min="0" value={geo} onChange={e => setGeo(e.target.value)} style={{ width: 120 }} /></label>
        <button onClick={saveConfig}>Save Config</button>
        <button onClick={start}>Start Scan</button>
        <button onClick={getResults}>Get Results</button>
        <button onClick={runTest}>Run Procedure Test</button>
        <span>Stage: <strong>{status.stage}</strong></span>
      </div>

      <div style={{ marginTop: 16 }}>
        <button onClick={() => setView('heatmap')}>Heatmap</button>
        <button onClick={() => setView('graph')} style={{ marginLeft: 8 }}>Graph</button>
      </div>

      <div style={{ marginTop: 12, border: '1px solid #eee', padding: 8 }}>
        {view === 'heatmap' && <Heatmap matrix={res?.matrix || []} labels={res?.labels || []} />}
        {view === 'graph' && <Graph clusters={res?.top_clusters || []} />}
      </div>

      <div style={{ marginTop: 8, fontSize: 12, color: '#555' }}>
        <div>threshold={res?.threshold ?? thr}, year_window={res?.year_window ?? year}, geo_window={res?.geo_window ?? (geo || 'none')}</div>
      </div>

      {testRes && (
        <div style={{ marginTop: 12, padding: 8, border: '1px solid #eee' }}>
          <div>Procedure test: <strong style={{ color: testRes.ok ? 'green' : 'crimson' }}>{String(testRes.ok)}</strong></div>
          {testRes.coverage && (
            <div style={{ marginTop: 6 }}>
              Coverage: {Object.entries(testRes.coverage).map(([k, v]) => `${k} ${v[0]}/${v[1]}`).join(' | ')}
            </div>
          )}
          {Array.isArray(testRes.notes) && testRes.notes.length > 0 && (
            <div style={{ marginTop: 6, color: '#944' }}>Notes: {testRes.notes.join('; ')}</div>
          )}
        </div>
      )}
    </div>
  )
}


