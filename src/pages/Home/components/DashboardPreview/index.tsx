import './styles.css'

// Simulated 12-month trend data for N, P, K
const MONTHS = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb']

const SERIES = {
    N: [72, 68, 74, 78, 76, 80, 82, 79, 77, 83, 88, 90],
    P: [45, 48, 46, 50, 52, 49, 55, 54, 58, 57, 60, 62],
    K: [35, 38, 34, 40, 42, 39, 44, 46, 43, 45, 48, 51],
}

const CHART_W = 100
const CHART_H = 60
const MAX_VAL = 100

function toX(i: number) {
    return (i / (MONTHS.length - 1)) * CHART_W
}
function toY(v: number) {
    return CHART_H - (v / MAX_VAL) * CHART_H
}

function buildPath(values: number[]) {
    return values
        .map((v, i) => `${i === 0 ? 'M' : 'L'} ${toX(i).toFixed(2)} ${toY(v).toFixed(2)}`)
        .join(' ')
}

const LINES = [
    { key: 'N' as const, label: 'Nitrogen', color: 'var(--color-green-dark)', strokeOpacity: 0.7 },
    { key: 'P' as const, label: 'Phosphorus', color: 'var(--color-green-mid)', strokeOpacity: 0.55 },
    { key: 'K' as const, label: 'Potassium', color: 'var(--color-green-accent)', strokeOpacity: 0.5 },
]

const READINGS = [
    { label: 'N — Nitrogen', status: 'OPTIMAL', statusClass: 'optimal', value: 90, recommendation: 'Maintain current fertiliser schedule.' },
    { label: 'P — Phosphorus', status: 'LOW', statusClass: 'low', value: 62, recommendation: 'Apply DAP 50 kg/acre before next watering.' },
    { label: 'K — Potassium', status: 'OPTIMAL', statusClass: 'optimal', value: 51, recommendation: 'No action required this cycle.' },
]

const SIDEBAR_PARAMS = [
    { label: 'N — Nitrogen', status: 'optimal' },
    { label: 'P — Phosphorus', status: 'low' },
    { label: 'K — Potassium', status: 'optimal' },
    { label: 'pH — Acidity', status: 'optimal' },
    { label: 'H₂O — Moisture', status: 'warn' },
]

const CALLOUTS = [
    { label: 'TRAFFIC-LIGHT INDEX', text: 'Colour-coded field status across all five soil parameters in one glance.' },
    { label: '12-MONTH HISTORY', text: 'Full NPK and pH trend stored per farm — exportable as CSV for agronomist review.' },
    { label: 'ICAR BENCHMARKS', text: 'Every reading compared against ICAR agro-climatic zone benchmarks for your district.' },
]

export default function DashboardPreview() {
    const lastMonth = MONTHS.length - 1
    return (
        <section className="dashboard-preview" id="dashboard" aria-label="Soil health dashboard preview">
            <div className="dashboard-preview__inner">
                <span className="dash-meta__label">Soil Health Dashboard — Live Reading View</span>

                {/* Main frame */}
                <div className="dash-frame">
                    {/* Sidebar */}
                    <div className="dash-sidebar">
                        <div className="dash-sidebar__farm">
                            <span className="dash-sidebar__farm-name">Nagdiwala Farm</span>
                            <span className="dash-sidebar__location">Pune District, Maharashtra</span>
                            <span className="dash-sidebar__timestamp">Last read: 28 Feb 2025 · 06:42 AM</span>
                        </div>
                        <div className="dash-sidebar__params">
                            {SIDEBAR_PARAMS.map(({ label, status }) => (
                                <div key={label} className="dash-param">
                                    <span className={`dash-param__dot dash-param__dot--${status}`} aria-label={status} />
                                    <span className="dash-param__label">{label}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Main content */}
                    <div className="dash-main">
                        {/* Trend chart */}
                        <div className="dash-chart">
                            <svg
                                className="dash-chart__svg"
                                viewBox={`0 0 ${CHART_W} ${CHART_H}`}
                                preserveAspectRatio="none"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                {/* Horizontal grid lines */}
                                {[25, 50, 75].map(y => (
                                    <line key={y} x1="0" y1={toY(y)} x2={CHART_W} y2={toY(y)}
                                        stroke="rgba(42,61,46,0.1)" strokeWidth="0.3" />
                                ))}

                                {/* Line traces */}
                                {LINES.map(({ key, color, strokeOpacity }) => (
                                    <g key={key}>
                                        <path
                                            d={buildPath(SERIES[key])}
                                            fill="none"
                                            stroke={color}
                                            strokeOpacity={strokeOpacity}
                                            strokeWidth="0.8"
                                        />
                                        {/* Data nodes */}
                                        {SERIES[key].map((v, i) => (
                                            <rect
                                                key={i}
                                                x={toX(i) - (i === lastMonth ? 2 : 1.5)}
                                                y={toY(v) - (i === lastMonth ? 2 : 1.5)}
                                                width={i === lastMonth ? 4 : 3}
                                                height={i === lastMonth ? 4 : 3}
                                                fill={color}
                                                fillOpacity={strokeOpacity}
                                            />
                                        ))}
                                        {/* Current month annotation */}
                                        <g>
                                            <line
                                                x1={toX(lastMonth)}
                                                y1={toY(SERIES[key][lastMonth]) + 3}
                                                x2={toX(lastMonth)}
                                                y2={CHART_H}
                                                stroke={color}
                                                strokeOpacity={strokeOpacity * 0.4}
                                                strokeWidth="0.4"
                                                strokeDasharray="1 1"
                                            />
                                        </g>
                                    </g>
                                ))}
                            </svg>

                            {/* X-axis month labels */}
                            <div className="dash-chart__x-axis">
                                {MONTHS.map((m, i) => (
                                    <span key={i} className={`dash-chart__month ${i === lastMonth ? 'dash-chart__month--current' : ''}`}>
                                        {m}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Current reading annotations for the current month */}
                        <div className="dash-chart__annotations">
                            {LINES.map(({ key, color }) => (
                                <span key={key} className="dash-chart__annotation" style={{ color }}>
                                    {key}: {SERIES[key][lastMonth]}
                                </span>
                            ))}
                        </div>

                        {/* Summary strip */}
                        <div className="dash-summary">
                            {READINGS.map(({ label, status, statusClass, value, recommendation }) => (
                                <div key={label} className="dash-reading">
                                    <span className="dash-reading__value">{value}</span>
                                    <span className={`dash-reading__status dash-reading__status--${statusClass}`}>{status}</span>
                                    <span className="dash-reading__rec">{recommendation}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Caption */}
                <p className="dash-meta__caption">
                    Every farm profile stores a full NPK, pH, and moisture history — visualised as a traffic-light health index.
                </p>

                {/* Feature callouts */}
                <div className="dash-callouts">
                    {CALLOUTS.map(({ label, text }, i) => (
                        <div key={label} className="dash-callout">
                            {i > 0 && <span className="dash-callout__sep" aria-hidden="true">·</span>}
                            <div className="dash-callout__content">
                                <span className="dash-callout__label">{label}</span>
                                <p className="dash-callout__text">{text}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    )
}
