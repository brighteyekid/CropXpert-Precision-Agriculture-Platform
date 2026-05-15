import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import LanguageSwitcher, { type LangCode } from '../../components/LanguageSwitcher/index'
import client from '../../api/client'
import SoilReadingsPage from './pages/SoilReadingsPage'
import RecommendationsPage from './pages/RecommendationsPage'
import MarketPricesPage from './pages/MarketPricesPage'
import SchemesPage from './pages/SchemesPage'
import './styles.css'

// ──────────────────────────── Types ─────────────────────────────────────────
interface SoilStatus { value: number; status: string; optimal_range: [number, number] }
interface DashboardData {
    latest_reading: { n: number; p: number; k: number; ph: number; moisture: number; temp: number; rainfall: number | null } | null
    soil_health: Record<string, SoilStatus>
    last_recommendation: { crop: string; confidence: number; msp: number; timestamp: string } | null
    trend_data: { labels: string[]; n: number[]; p: number[]; k: number[] }
    schemes_available: number
    profit_estimate: { crop: string; net_profit_per_acre: number; input_cost: number } | null
}

interface MarketRow { crop: string; msp_inr: number; mandi_price: number; delta_pct: number }
interface FarmerData { name: string | null; district: string | null; state: string | null; acreage: number | null }

const NAV_ITEMS = [
    { id: 'overview', label: 'Overview' },
    { id: 'soil', label: 'Soil Readings' },
    { id: 'recommendations', label: 'Crop Recommendations' },
    { id: 'market', label: 'Market Prices' },
    { id: 'schemes', label: 'Schemes and Loans' },
] as const
type NavId = typeof NAV_ITEMS[number]['id']

// ──────────────────────────── Sparkline ─────────────────────────────────────
function Sparkline({ values, up }: { values: number[]; up: boolean }) {
    if (!values || values.length < 2) return null
    const min = Math.min(...values); const max = Math.max(...values); const rng = max - min || 1
    const W = 40; const H = 20
    const pts = values.map((v, i) => {
        const x = ((i / (values.length - 1)) * W).toFixed(1)
        const y = (H - ((v - min) / rng) * H).toFixed(1)
        return `${x},${y}`
    }).join(' ')
    return (
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} aria-hidden="true">
            <polyline points={pts} fill="none" stroke={up ? 'var(--color-green-accent)' : '#c8922a'} strokeWidth="1"
                opacity={up ? 0.65 : 0.5} />
        </svg>
    )
}

// ──────────────────────────── Overview Content ───────────────────────────────
function OverviewContent({
    dashboard, marketCrops, onNav
}: {
    dashboard: DashboardData | null
    marketCrops: MarketRow[]
    onNav: (id: NavId) => void
}) {
    const [alertDismissed, setAlertDismissed] = useState(false)
    const LINE_COLORS: Record<string, string> = { N: 'var(--color-green-dark)', P: 'var(--color-green-mid)', K: 'var(--color-green-accent)' }

    const rec = dashboard?.last_recommendation
    const soil = dashboard?.soil_health || {}
    const trend = dashboard?.trend_data || { labels: [], n: [], p: [], k: [] }
    const schemesCount = dashboard?.schemes_available || 0

    const SOIL_KEYS = [
        { key: 'N', field: 'nitrogen' },
        { key: 'P', field: 'phosphorus' },
        { key: 'K', field: 'potassium' },
        { key: 'pH', field: 'ph' },
        { key: 'H₂O', field: 'moisture' },
    ]

    function statusClass(s: string) { return s === 'green' ? 'optimal' : s === 'amber' ? 'low' : 'critical' }
    function statusLabel(s: string) { return s === 'green' ? 'OPTIMAL' : s === 'amber' ? 'LOW' : 'CRITICAL' }

    // Trend chart
    const months = trend.labels.length > 0 ? trend.labels : []
    const CHART_W = 500; const CHART_H = 60
    const allVals = [...(trend.n || []), ...(trend.p || []), ...(trend.k || [])]
    const gMin = allVals.length > 0 ? Math.min(...allVals) - 5 : 0
    const gMax = allVals.length > 0 ? Math.max(...allVals) + 5 : 100
    const toX = (i: number) => months.length > 1 ? (i / (months.length - 1)) * CHART_W : CHART_W / 2
    const toY = (v: number) => gMax > gMin ? CHART_H - ((v - gMin) / (gMax - gMin)) * CHART_H * 0.85 - CHART_H * 0.075 : CHART_H / 2

    const topMarket = marketCrops.slice(0, 3)

    return (
        <>
            {/* Block 1 — Recommendation */}
            <div className="db-block--recommendation">
                <div className="db-rec__main">
                    <span className="db-block__label">Top Recommendation — {rec?.timestamp ? new Date(rec.timestamp).toLocaleDateString() : 'Updated Today'}</span>
                    <div className="db-rec__headline-row">
                        <h2 className="db-rec__crop">{rec?.crop || '—'}</h2>
                        <span className="db-rec__confidence">{rec ? `${(rec.confidence * 100).toFixed(1)}%` : '—'}</span>
                    </div>
                    <div className="db-rec__micro-row">
                        <span className="db-rec__micro">MSP: ₹{rec?.msp?.toLocaleString() || '—'}/qt</span>
                        <span className="db-rec__pipe">|</span>
                        <span className="db-rec__micro">Profit est.: ₹{dashboard?.profit_estimate?.net_profit_per_acre?.toLocaleString() || '—'}/acre</span>
                        <span className="db-rec__pipe">|</span>
                        <span className="db-rec__micro db-rec__micro--up">{schemesCount} schemes available</span>
                    </div>
                    <p className="db-rec__detail">
                        {rec ? `ML model confidence at ${(rec.confidence * 100).toFixed(1)}% for ${rec.crop}. MSP stands at ₹${rec.msp}/quintal.` : 'Complete onboarding to get your first recommendation.'}
                    </p>
                </div>
                <div className="db-rec__actions">
                    <button className="db-rec__ghost-btn" id="db-full-analysis" onClick={() => onNav('recommendations')}>View Full Analysis</button>
                    <button className="db-rec__text-btn" id="db-compare" onClick={() => onNav('market')}>Compare Alternatives</button>
                </div>
            </div>

            <div className="db-rule" />

            {/* Block 2 — Soil strip */}
            <span className="db-block__label">Soil Health — Current Reading</span>
            <div className="db-soil-grid">
                {SOIL_KEYS.map(({ key, field }) => {
                    const info = soil[field]
                    const value = info?.value ?? 0
                    const st = info?.status || 'green'
                    const sc = statusClass(st)
                    const lo = info?.optimal_range?.[0] || 0
                    const hi = info?.optimal_range?.[1] || 100
                    const rng = hi - lo || 1
                    const pct = Math.min(100, Math.max(0, ((value - lo) / rng) * 100))
                    return (
                        <div key={key} className="db-soil-col">
                            <div className="db-soil-col__value-row">
                                <span className="db-soil-col__value">{typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(1)) : value}</span>
                                <div className="db-soil-col__bar-wrap" aria-hidden="true">
                                    <div className="db-soil-col__bar-track">
                                        <div className={`db-soil-col__bar-fill db-soil-col__bar-fill--${sc}`} style={{ height: `${pct}%` }} />
                                    </div>
                                </div>
                            </div>
                            <span className="db-soil-col__key">{key}</span>
                            <span className={`db-soil-col__status db-soil-col__status--${sc}`}>{statusLabel(st)}</span>
                        </div>
                    )
                })}
            </div>

            <div className="db-rule" />

            {/* Block 3 — Market */}
            <span className="db-block__label">Market Prices — Live AGMARKNET</span>
            <div className="db-market-header">
                <span>Crop</span><span>MSP</span><span>Mandi</span><span>Delta</span><span></span>
            </div>
            <div className="db-market-table">
                {topMarket.map(({ crop, msp_inr, mandi_price, delta_pct }) => {
                    const up = delta_pct >= 0
                    return (
                        <div key={crop} className="db-market-row">
                            <span className="db-market-row__crop">{crop}</span>
                            <span className="db-market-row__msp">₹{msp_inr.toLocaleString()}</span>
                            <span className="db-market-row__mandi">₹{mandi_price.toLocaleString()}</span>
                            <span className={`db-market-row__delta db-market-row__delta--${up ? 'up' : 'down'}`}>{up ? '+' : ''}{delta_pct}%</span>
                            <Sparkline values={[msp_inr * 0.98, msp_inr * 0.99, msp_inr, mandi_price * 0.99, mandi_price * 1.01, mandi_price, mandi_price]} up={up} />
                        </div>
                    )
                })}
            </div>

            {/* Block 4 — Scheme alert */}
            {!alertDismissed && schemesCount > 0 && (
                <div className="db-scheme-alert">
                    <span className="db-scheme-alert__diamond" aria-hidden="true" />
                    <p className="db-scheme-alert__text">
                        <strong>PM-KISAN</strong> — You qualify based on your registered landholding (&lt;2 ha).
                    </p>
                    <button className="db-scheme-alert__link" id="db-scheme-eligibility" onClick={() => onNav('schemes')}>Check Eligibility</button>
                    <button className="db-scheme-alert__dismiss" onClick={() => setAlertDismissed(true)} aria-label="Dismiss alert">✕</button>
                </div>
            )}

            <div className="db-rule" />

            {/* Block 5 — Trend chart */}
            {months.length > 0 && (
                <div className="db-block--trend">
                    <div className="db-trend__header">
                        <span className="db-block__label" style={{ marginBottom: 0 }}>NPK Trend</span>
                        <div className="db-trend__legend">
                            {Object.entries(LINE_COLORS).map(([key, color]) => (
                                <span key={key} className="db-trend__legend-item">
                                    <span className="db-trend__legend-dot" style={{ background: color }} aria-hidden="true" />
                                    <span className="db-trend__legend-label">{key}</span>
                                </span>
                            ))}
                        </div>
                    </div>
                    <div className="db-trend__chart-wrap">
                        <svg viewBox={`0 0 ${CHART_W} ${CHART_H}`} className="db-trend__svg" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
                            {[0.25, 0.5, 0.75].map(p => (
                                <line key={p} x1="0" y1={CHART_H * p} x2={CHART_W} y2={CHART_H * p} stroke="rgba(42,61,46,0.08)" strokeWidth="0.5" />
                            ))}
                            {([['N', trend.n], ['P', trend.p], ['K', trend.k]] as [string, number[]][]).map(([key, vals]) => {
                                if (!vals || vals.length === 0) return null
                                const pts = vals.map((v, i) => `${i === 0 ? 'M' : 'L'}${toX(i).toFixed(1)},${toY(v).toFixed(1)}`).join(' ')
                                return (
                                    <g key={key}>
                                        <path d={pts} fill="none" stroke={LINE_COLORS[key]} strokeWidth="1" opacity="0.7" />
                                        {vals.map((v, i) => (
                                            <rect key={i} x={toX(i) - 2} y={toY(v) - 2} width={4} height={4} fill={LINE_COLORS[key]} opacity="0.7" />
                                        ))}
                                    </g>
                                )
                            })}
                        </svg>
                        <div className="db-trend__x-axis">
                            {months.map((m, i) => (
                                <span key={i} className={`db-trend__month ${i === months.length - 1 ? 'db-trend__month--current' : ''}`}>{m}</span>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}

// ──────────────────────────── Sidebar ───────────────────────────────────────
function Sidebar({ active, onNav, hasReadings, weather }: {
    active: NavId
    onNav: (id: NavId) => void
    hasReadings: boolean
    weather: { temp: number | null; desc: string }
}) {
    const now = new Date()
    const dateStr = now.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
    const tempStr = weather.temp != null ? `${weather.temp}°C` : '—°C'
    return (
        <aside className="dash-sidebar">
            <div className="dash-sidebar__meta">
                <span className="ds-meta__date">{dateStr}</span>
                <span className="ds-meta__weather">{tempStr} · {weather.desc}</span>
            </div>
            <nav className="ds-nav" aria-label="Dashboard navigation">
                {NAV_ITEMS.map(({ id, label }, i) => (
                    <div key={id}>
                        {i === 3 && <div className="ds-nav__sep" />}
                        <button
                            className={`ds-nav__item ${active === id ? 'ds-nav__item--active' : ''}`}
                            onClick={() => onNav(id)}
                            id={`ds-nav-${id}`}
                        >
                            {label}
                        </button>
                    </div>
                ))}
            </nav>
            <div className="ds-sensor">
                <span className="ds-sensor__label">Sensor</span>
                {hasReadings ? (
                    <>
                        <span className="ds-sensor__status ds-sensor__status--connected">Reading Available</span>
                        <span className="ds-sensor__ts">Last sync · {now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
                    </>
                ) : (
                    <>
                        <span className="ds-sensor__status ds-sensor__status--manual">No Sensor — Manual</span>
                        <span className="ds-sensor__ts">Connect UNO via USB in Onboarding</span>
                    </>
                )}
            </div>
        </aside>
    )
}

// ──────────────────────────────────────────────────────────────────────────────
// Helpers
// Clean farmer display name — strip "District — " prefix if backend auto-built it
function cleanFarmerName(raw: string | null): string {
    if (!raw) return 'My Farm'
    // Strip pattern like "Pune — Rice farmer" → just show "Rice farmer"
    // or "Hiriyuru taluk — wheat farmer" → "Wheat farmer"
    const dashIdx = raw.indexOf(' — ')
    if (dashIdx !== -1) {
        const afterDash = raw.slice(dashIdx + 3).trim()
        // Capitalise first letter
        return afterDash.charAt(0).toUpperCase() + afterDash.slice(1)
    }
    return raw
}

function getInitials(name: string | null, district: string | null): string {
    const clean = cleanFarmerName(name)
    const words = clean.split(/\s+/).filter(Boolean)
    if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase()
    if (words.length === 1) return words[0].slice(0, 2).toUpperCase()
    if (district) return district.slice(0, 2).toUpperCase()
    return 'CX'
}

// ──────────────────────────── Top Bar ───────────────────────────────────────
function TopBar({ lang, onLangChange, farmer, schemeAlert }: {
    lang: LangCode
    onLangChange: (c: LangCode) => void
    farmer: FarmerData | null
    schemeAlert: boolean
}) {
    const navigate = useNavigate()
    const displayName = cleanFarmerName(farmer?.name ?? null)
    const initials = getInitials(farmer?.name ?? null, farmer?.district ?? null)
    const district = farmer?.district || null
    const state = farmer?.state || null
    const locationStr = [district, state].filter(Boolean).join(', ') || '—'

    return (
        <header className="dash-topbar">
            <button className="dash-topbar__wordmark" onClick={() => navigate('/')} aria-label="CropXpert home">
                Crop<span className="dash-topbar__x">X</span>pert
            </button>
            <div className="dash-topbar__farm">
                <span className="dash-topbar__farm-name">{displayName}</span>
                <span className="dash-topbar__district">{locationStr}</span>
            </div>
            <div className="dash-topbar__right">
                <LanguageSwitcher variant="navbar" active={lang} onChange={onLangChange} />
                {schemeAlert && (
                    <div className="dash-notif" title="New scheme alert" aria-label="New scheme alert">
                        <span className="dash-notif__diamond" aria-hidden="true" />
                    </div>
                )}
                <div className="dash-avatar" aria-label={`${displayName} — ${locationStr}`}>{initials}</div>
            </div>
        </header>
    )
}

// ──────────────────────────── Dashboard root ────────────────────────────────
export default function Dashboard() {
    const [activeNav, setActiveNav] = useState<NavId>('overview')
    const [lang, setLang] = useState<LangCode>('EN')
    const [dashboard, setDashboard] = useState<DashboardData | null>(null)
    const [marketCrops, setMarketCrops] = useState<MarketRow[]>([])
    const [farmer, setFarmer] = useState<FarmerData | null>(null)
    const [weather, setWeather] = useState<{ temp: number | null; desc: string }>({ temp: null, desc: '—' })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchAll() {
            setLoading(true)
            try {
                const [dashResp, marketResp, farmerResp] = await Promise.all([
                    client.get('/api/dashboard/summary').catch(() => null),
                    client.get('/api/market/all-crops').catch(() => null),
                    client.get('/api/farmer/profile').catch(() => null),
                ])
                if (dashResp?.data) setDashboard(dashResp.data)
                if (marketResp?.data) setMarketCrops(marketResp.data)
                if (farmerResp?.data) {
                    setFarmer(farmerResp.data)
                    // Fetch live weather for the farmer's district (open-meteo, no auth)
                    const district = farmerResp.data.district
                    if (district) {
                        fetch(`http://localhost:8000/api/weather/current?city=${encodeURIComponent(district)}`)
                            .then(r => r.ok ? r.json() : null)
                            .then(w => {
                                if (w && w.temperature != null) {
                                    setWeather({
                                        temp: w.temperature,
                                        desc: w.humidity != null ? `${w.humidity}% RH` : '—',
                                    })
                                }
                            })
                            .catch(() => {/* weather is optional */ })
                    }
                }
            } catch (e) {
                console.error('Dashboard fetch error:', e)
            } finally {
                setLoading(false)
            }
        }
        fetchAll()
    }, [])

    const schemesAvail = dashboard?.schemes_available || 0
    // The last recommendation from the DB — ensures Overview and RecommendationsPage always show the SAME crop
    const lastRec = dashboard?.last_recommendation ?? null

    const renderPage = () => {
        switch (activeNav) {
            case 'soil': return <SoilReadingsPage lang={lang} />
            case 'recommendations': return <RecommendationsPage lang={lang} initialRec={lastRec} />
            case 'market': return <MarketPricesPage lang={lang} />
            case 'schemes': return <SchemesPage lang={lang} />
            default: return <OverviewContent dashboard={dashboard} marketCrops={marketCrops} onNav={setActiveNav} />
        }
    }

    return (
        <div className="dashboard">
            <TopBar lang={lang} onLangChange={setLang} farmer={farmer} schemeAlert={schemesAvail > 0} />
            <div className="dashboard__body">
                <Sidebar active={activeNav} onNav={setActiveNav} hasReadings={!!dashboard?.latest_reading} weather={weather} />
                <main className="dashboard__content">
                    {loading ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '40px 0' }}>
                            <span className="db-block__label">Loading data from server…</span>
                        </div>
                    ) : renderPage()}
                </main>
            </div>
        </div>
    )
}
