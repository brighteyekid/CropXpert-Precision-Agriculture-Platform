import { useState, useEffect } from 'react'
import client from '../../../api/client'
import type { LangCode } from '../../../components/LanguageSwitcher/index'
import { useArduinoSerial } from '../../../hooks/useArduinoSerial'

interface SensorReading {
    id: number; nitrogen: number; phosphorus: number; potassium: number
    ph: number; moisture: number; temperature: number; humidity: number | null
    rainfall: number | null; source: string; timestamp: string
}

interface SoilParam {
    key: string; label: string; value: number; unit: string
    status: 'optimal' | 'low' | 'critical'
    icarMin: number; icarMax: number; action: string
}

const LABELS: Record<string, Record<string, string>> = {
    header: { EN: 'Soil Readings — Field Analysis', HI: 'मिट्टी रीडिंग — क्षेत्र विश्लेषण', MR: 'माती वाचन — शेत विश्लेषण', TA: 'மண் வாசிப்பு — வயல் பகுப்பாய்வு', TE: 'నేల రీడింగ్‌లు — ఫీల్డ్ విశ్లేషణ' },
    newReading: { EN: 'New Reading', HI: 'नई रीडिंग', MR: 'नवीन वाचन', TA: 'புதிய வாசிப்பு', TE: 'కొత్త రీడింగ్' },
    download: { EN: 'Download Report', HI: 'रिपोर्ट डाउनलोड करें', MR: 'अहवाल डाउनलोड करा', TA: 'அறிக்கை பதிவிறக்கம்', TE: 'నివేదిక డౌన్‌లోడ్' },
}

function getIcarAction(key: string, value: number, min: number, max: number): string {
    if (value >= min && value <= max) {
        return `${key} is within the optimal ICAR range (${min}–${max}). No action required.`
    } else if (value < min) {
        return `${key} is below the ICAR minimum of ${min}. Consider supplementary application before next cycle.`
    }
    return `${key} exceeds the ICAR maximum of ${max}. Reduce application rate or investigate runoff sources.`
}

function getStatus(value: number, min: number, max: number): 'optimal' | 'low' | 'critical' {
    if (value >= min && value <= max) return 'optimal'
    if (value < min && value >= min * 0.6) return 'low'
    return 'critical'
}

type ChartRange = '3M' | '6M' | '12M' | 'LIVE'

function buildPath(values: number[], W: number, H: number) {
    const min = Math.min(...values); const max = Math.max(...values); const rng = max - min || 1
    return values.map((v, i) => {
        const x = ((i / (values.length - 1)) * W).toFixed(1)
        const y = (H - ((v - min) / rng) * H * 0.85 - H * 0.075).toFixed(1)
        return `${i === 0 ? 'M' : 'L'}${x},${y}`
    }).join(' ')
}

function MiniLineChart({ values, color, label }: { values: number[]; color: string; label: string }) {
    if (!values || values.length < 2) return null
    const W = 300; const H = 60
    return (
        <div className="mini-chart">
            <span className="mini-chart__label">{label}</span>
            <svg viewBox={`0 0 ${W} ${H}`} xmlns="http://www.w3.org/2000/svg">
                <path d={buildPath(values, W, H)} fill="none" stroke={color} strokeWidth="1" opacity="0.65" />
            </svg>
        </div>
    )
}

export default function SoilReadingsPage({ lang = 'EN' }: { lang?: LangCode }) {
    const [latest, setLatest] = useState<SensorReading | null>(null)
    const [history, setHistory] = useState<SensorReading[]>([])
    const [tab, setTab] = useState<ChartRange>('12M')
    const [loading, setLoading] = useState(true)
    const [liveData, setLiveData] = useState<SensorReading[]>([])
    const arduino = useArduinoSerial()

    useEffect(() => {
        async function fetch() {
            setLoading(true)
            try {
                // 404 = no readings yet — not a real error
                const latestResp = await client.get('/api/sensors/latest').catch((e) => {
                    if (e?.response?.status === 404) return null  // no data yet
                    return null
                })
                const histResp = await client.get('/api/sensors/history', { params: { days: 365 } }).catch(() => null)
                if (latestResp?.data) setLatest(latestResp.data)
                if (histResp?.data) setHistory(histResp.data)
            } catch (e) { console.error(e) }
            finally { setLoading(false) }
        }
        fetch()
        return () => { arduino.disconnect() }
    }, [])

    const handleConnectLive = async () => {
        if (!arduino.connected) {
            const ok = await arduino.connect()
            if (!ok) return
        }
        setTab('LIVE')
        arduino.startLiveRead((data) => {
            const timestamp = new Date().toISOString()
            const newReading: SensorReading = {
                id: Date.now(),
                nitrogen: parseFloat(data.n) || 0,
                phosphorus: parseFloat(data.p) || 0,
                potassium: parseFloat(data.k) || 0,
                ph: parseFloat(data.ph) || 0,
                moisture: parseFloat(data.moisture) || 0,
                temperature: parseFloat(data.temp) || 0,
                humidity: null,
                rainfall: null,
                source: 'live',
                timestamp
            }
            setLiveData(prev => [...prev, newReading].slice(-40))
            setLatest(newReading)
        })
    }

    const ICAR: Record<string, [number, number]> = {
        N: [80, 120], P: [50, 80], K: [60, 100], pH: [5.5, 7.5], 'H₂O': [40, 70], Temp: [22, 32]
    }

    const params: SoilParam[] = latest ? [
        { key: 'N', label: 'N — Nitrogen', value: latest.nitrogen, unit: 'mg/kg', status: getStatus(latest.nitrogen, 80, 120), icarMin: 80, icarMax: 120, action: getIcarAction('Nitrogen', latest.nitrogen, 80, 120) },
        { key: 'P', label: 'P — Phosphorus', value: latest.phosphorus, unit: 'mg/kg', status: getStatus(latest.phosphorus, 50, 80), icarMin: 50, icarMax: 80, action: getIcarAction('Phosphorus', latest.phosphorus, 50, 80) },
        { key: 'K', label: 'K — Potassium', value: latest.potassium, unit: 'mg/kg', status: getStatus(latest.potassium, 60, 100), icarMin: 60, icarMax: 100, action: getIcarAction('Potassium', latest.potassium, 60, 100) },
        { key: 'pH', label: 'pH — Acidity', value: latest.ph, unit: 'pH', status: getStatus(latest.ph, 5.5, 7.5), icarMin: 5.5, icarMax: 7.5, action: getIcarAction('pH', latest.ph, 5.5, 7.5) },
        { key: 'H₂O', label: 'Moisture', value: latest.moisture, unit: '%', status: getStatus(latest.moisture, 40, 70), icarMin: 40, icarMax: 70, action: getIcarAction('Moisture', latest.moisture, 40, 70) },
        { key: 'Temp', label: 'Temperature', value: latest.temperature, unit: '°C', status: getStatus(latest.temperature, 22, 32), icarMin: 22, icarMax: 32, action: getIcarAction('Temperature', latest.temperature, 22, 32) },
    ] : []

    const sorted = [...history].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    const COUNT_MAP: Record<string, number> = { '3M': 3, '6M': 6, '12M': 12, 'LIVE': 0 }
    const count = COUNT_MAP[tab]
    const trendData = tab === 'LIVE' ? liveData : sorted.slice(-count)
    const nValues = trendData.map(r => r.nitrogen)
    const pValues = trendData.map(r => r.phosphorus)
    const kValues = trendData.map(r => r.potassium)
    const phValues = trendData.map(r => r.ph)
    const moistValues = trendData.map(r => r.moisture)
    const trendLabels = tab === 'LIVE' 
        ? trendData.map(r => new Date(r.timestamp).toLocaleTimeString('en-IN', { hour12: false, second: '2-digit', minute: '2-digit', hour: '2-digit' }))
        : trendData.map(r => new Date(r.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }))

    const W = 600; const H = 120
    const allVals = [...nValues, ...pValues, ...kValues]
    const gMin = allVals.length > 0 ? Math.min(...allVals) - 5 : 0
    const gMax = allVals.length > 0 ? Math.max(...allVals) + 5 : 100
    const toX = (i: number) => trendLabels.length > 1 ? (i / (trendLabels.length - 1)) * W : W / 2
    const toY = (v: number) => gMax > gMin ? H - ((v - gMin) / (gMax - gMin)) * H * 0.85 - H * 0.075 : H / 2
    const LINE_COLORS: Record<string, string> = { N: 'var(--color-green-dark)', P: 'var(--color-green-mid)', K: 'var(--color-green-accent)' }

    const handleExport = () => { window.open(`${client.defaults.baseURL}/api/sensors/export`, '_blank') }

    if (loading) return <div className="dp-header"><span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}… Loading</span></div>

    if (!latest && history.length === 0) {
        return (
            <div>
                <div className="dp-header">
                    <span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}</span>
                </div>
                <div style={{
                    padding: '40px 0',
                    display: 'flex', flexDirection: 'column', gap: 12,
                }}>
                    <span className="db-block__label" style={{ marginBottom: 0 }}>No Readings Yet</span>
                    <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.875rem', fontWeight: 300, color: 'var(--color-text-body)', lineHeight: 1.7, maxWidth: '52ch' }}>
                        No soil data has been recorded yet. You can add a reading in two ways:
                    </p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                            <span className="db-scheme-alert__diamond" style={{ marginTop: 4, flexShrink: 0 }} aria-hidden="true" />
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--color-text-light)', letterSpacing: '0.06em' }}>
                                <strong style={{ color: 'var(--color-green-dark)' }}>Connect Arduino UNO via USB</strong> — go to Onboarding Step 3 and click "Connect Arduino / UNO Sensor". Your sensor values will auto-populate.
                            </span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                            <span className="db-scheme-alert__diamond" style={{ marginTop: 4, flexShrink: 0 }} aria-hidden="true" />
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--color-text-light)', letterSpacing: '0.06em' }}>
                                <strong style={{ color: 'var(--color-green-dark)' }}>Enter values manually</strong> — complete Onboarding Step 3 with values from your soil test report.
                            </span>
                        </div>
                    </div>
                    <a href="/onboarding" style={{
                        display: 'inline-block', marginTop: 16,
                        fontFamily: 'var(--font-mono)', fontSize: '0.52rem', fontWeight: 400,
                        letterSpacing: '0.14em', textTransform: 'uppercase',
                        color: '#f0ede4', background: 'var(--color-green-dark)',
                        border: 'none', padding: '14px 28px', cursor: 'pointer',
                        textDecoration: 'none', alignSelf: 'flex-start',
                    }}>
                        Go to Onboarding
                    </a>
                </div>
            </div>
        )
    }

    return (
        <div>
            <div className="dp-header">
                <span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}</span>
                <div className="dp-header__actions">
                    <button className="dp-ghost-btn" id="sr-new-reading">{LABELS.newReading[lang] || LABELS.newReading.EN}</button>
                    <button className="dp-ghost-btn" id="sr-download" onClick={handleExport}>{LABELS.download[lang] || LABELS.download.EN}</button>
                </div>
            </div>

            {latest && (
                <div className="soil-reading-card">
                    <div className="soil-reading-card__ts">
                        <span>Last reading — {new Date(latest.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })} — {new Date(latest.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
                        <span>Source — {latest.source === 'mqtt' ? 'CropXpert Sensor' : 'Manual Entry'}</span>
                    </div>
                    <div className="src-cols">
                        {params.map(({ key, value, unit, status, icarMin, icarMax }) => {
                            const rng = icarMax - icarMin || 1
                            const pct = Math.min(100, Math.max(0, ((value - icarMin) / rng) * 100))
                            return (
                                <div key={key} className="src-col">
                                    <span className="src-col__label">{key}</span>
                                    <span className="src-col__value">{typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(1)) : value}</span>
                                    <span className="src-col__unit">{unit}</span>
                                    <span className={`src-col__pill src-col__pill--${status}`}>{status === 'optimal' ? 'Optimal' : status === 'low' ? 'Low' : 'Critical'}</span>
                                    <div className="src-col__range"><div className="src-col__range-track"><div className={`src-col__range-fill src-col__range-fill--${status}`} style={{ width: `${pct}%` }} /></div></div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            <table className="icar-table">
                <thead><tr><th>Parameter</th><th>Your Reading</th><th>ICAR Optimal Range</th><th>Status</th><th>Recommended Action</th></tr></thead>
                <tbody>
                    {params.map(({ key, label, value, unit, status, icarMin, icarMax, action }) => (
                        <tr key={key}>
                            <td className="icar-td--param">{label}</td>
                            <td className="icar-td--value">{typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(1)) : value} <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', fontWeight: 300 }}>{unit}</span></td>
                            <td className="icar-td--range">{icarMin} – {icarMax} {unit}</td>
                            <td><span className={`src-col__pill src-col__pill--${status}`} style={{ fontSize: '8px' }}>{status === 'optimal' ? 'Optimal' : status === 'low' ? 'Low' : 'Critical'}</span></td>
                            <td className="icar-td--action">{action}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <div className="db-rule" />

            <div className="dp-header" style={{ marginBottom: 12 }}>
                <span className="db-block__label">NPK Trend</span>
                <div className="chart-tabs">
                    {(['3M', '6M', '12M', 'LIVE'] as ChartRange[]).map(t => (
                        <button key={t} className={`chart-tab ${tab === t ? 'chart-tab--active' : ''} ${t === 'LIVE' ? 'chart-tab--live' : ''}`} 
                                onClick={() => { setTab(t); if (t !== 'LIVE') { arduino.stopRead() } else { handleConnectLive() } }}>
                            {t === '3M' ? '3 Months' : t === '6M' ? '6 Months' : t === '12M' ? '12 Months' : '● Live Stream'}
                        </button>
                    ))}
                </div>
            </div>

            {tab === 'LIVE' && liveData.length === 0 && (
                <div style={{ padding: '60px 0', textAlign: 'center' }}>
                    <span className="ob-scan-line" style={{ display: 'inline-block', width: 200, marginBottom: 16 }}>
                        <span className="ob-scan-line__track"><span className="ob-scan-line__bright" /></span>
                    </span>
                    <p style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-text-light)', letterSpacing: '0.06em' }}>WAITING FOR SENSOR DATA…</p>
                </div>
            )}

            {trendLabels.length > 1 && (
                <>
                    <div className="db-trend__chart-wrap">
                        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', height: '320px', display: 'block', minHeight: '320px' }} xmlns="http://www.w3.org/2000/svg">
                            {[0.25, 0.5, 0.75].map(p => (<line key={p} x1="0" y1={H * p} x2={W} y2={H * p} stroke="rgba(42,61,46,0.08)" strokeWidth="0.4" />))}
                            {([['N', nValues], ['P', pValues], ['K', kValues]] as [string, number[]][]).map(([key, vals]) => {
                                if (vals.length < 2) return null
                                const pts = vals.map((v, i) => `${i === 0 ? 'M' : 'L'}${toX(i).toFixed(1)},${toY(v).toFixed(1)}`).join(' ')
                                return (
                                    <g key={key}>
                                        <path d={pts} fill="none" stroke={LINE_COLORS[key]} strokeWidth="1" opacity="0.7" />
                                        {vals.map((v, i) => <rect key={i} x={toX(i) - 2} y={toY(v) - 2} width={4} height={4} fill={LINE_COLORS[key]} opacity="0.7" />)}
                                    </g>
                                )
                            })}
                        </svg>
                        <div className="db-trend__x-axis">
                            {trendLabels.map((m, i) => <span key={i} className={`db-trend__month ${i === trendLabels.length - 1 ? 'db-trend__month--current' : ''}`}>{m}</span>)}
                        </div>
                    </div>
                    <div className="mini-charts-row">
                        <MiniLineChart values={phValues} color="var(--color-green-accent)" label="pH — Acidity Trend" />
                        <MiniLineChart values={moistValues} color="#c8922a" label="H₂O — Moisture Trend" />
                    </div>
                </>
            )}

            <div className="db-rule" />

            <span className="db-block__label">Historical Reading Log</span>
            <table className="hist-table">
                <thead><tr><th>Date</th><th>N</th><th>P</th><th>K</th><th>pH</th><th>Moisture</th><th>Temp</th><th>Source</th></tr></thead>
                <tbody>
                    {history.slice(0, 20).map((row) => (
                        <tr key={row.id}>
                            <td>{new Date(row.timestamp).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: '2-digit' })}</td>
                            <td>{row.nitrogen}</td><td>{row.phosphorus}</td><td>{row.potassium}</td>
                            <td>{row.ph}</td><td>{row.moisture}%</td><td>{row.temperature}°C</td>
                            <td><span className="hist-table__crop-rec">{row.source}</span></td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
