import './styles.css'

const STEPS = [
    {
        id: 'field',
        label: 'FIELD',
        align: 'left' as const,
        numeral: '01',
        headline: 'Sensors read your soil in seconds.',
        body: 'Four probes measure nitrogen, potassium, pH, and soil moisture directly in your field bed. No lab, no delay — readings transmit in under three seconds.',
    },
    {
        id: 'analysis',
        label: 'ANALYSIS',
        align: 'right' as const,
        numeral: '02',
        headline: 'Your readings meet 22 verified crop profiles.',
        body: 'A Random Forest classifier trained on 2,200 field samples matches your soil signature to ranked crop options. Validated accuracy sits at 99.2% across all supported varieties.',
    },
    {
        id: 'decision',
        label: 'DECISION',
        align: 'left' as const,
        numeral: '03',
        headline: 'A ranked recommendation — with the market built in.',
        body: 'AGMARKNET live pricing and MSP figures flow directly into the final score. Every recommendation accounts for what your crop is actually selling for in your district today.',
    },
] as const

function SoilDiagram() {
    const bands = [
        { label: 'N', color: 'rgba(42,61,46,0.14)' },
        { label: 'P', color: 'rgba(42,61,46,0.09)' },
        { label: 'K', color: 'rgba(42,61,46,0.11)' },
        { label: 'pH', color: 'rgba(42,61,46,0.07)' },
    ]
    return (
        <div className="hw-diagram hw-diagram--soil" aria-hidden="true">
            {bands.map(({ label, color }) => (
                <div key={label} className="hw-diagram__band" style={{ background: color }}>
                    <span className="hw-diagram__band-label">{label}</span>
                </div>
            ))}
        </div>
    )
}

// bars sorted so index 2 (value 99) is the tallest / accent bar
const BAR_VALUES = [65, 82, 99, 71, 78]

function BarChart() {
    const max = Math.max(...BAR_VALUES)
    return (
        <div className="hw-diagram hw-diagram--bars" aria-hidden="true">
            {BAR_VALUES.map((h, i) => {
                const pct = Math.round((h / max) * 100)
                const isAccent = h === max
                return (
                    <div key={i} className="hw-diagram__bar-wrap">
                        {isAccent && <span className="hw-diagram__bar-label hw-diagram__bar-label--accent">{h}</span>}
                        {!isAccent && <span className="hw-diagram__bar-label">{h}</span>}
                        <div
                            className={`hw-diagram__bar ${isAccent ? 'hw-diagram__bar--accent' : ''}`}
                            style={{ height: `${pct}%` }}
                        />
                    </div>
                )
            })}
        </div>
    )
}

function RankCard() {
    const crops = [
        { rank: '01', name: 'Rice', price: '₹2,183/qt', top: true },
        { rank: '02', name: 'Maize', price: '₹1,962/qt', top: false },
        { rank: '03', name: 'Soybean', price: '₹4,600/qt', top: false },
    ]
    return (
        <div className="hw-diagram hw-diagram--rank" aria-hidden="true">
            {crops.map(({ rank, name, price, top }) => (
                <div key={rank} className={`hw-diagram__rank-row ${top ? 'hw-diagram__rank-row--top' : ''}`}>
                    <span className="hw-diagram__rank-num">{rank}</span>
                    <span className="hw-diagram__rank-name">{name}</span>
                    <span className="hw-diagram__rank-price">{price}</span>
                </div>
            ))}
        </div>
    )
}

const DIAGRAMS = [SoilDiagram, BarChart, RankCard]

export default function HowItWorks() {
    return (
        <section className="how-it-works" id="how-it-works" aria-labelledby="hiw-title">
            <div className="how-it-works__inner">
                <div className="hiw-header">
                    <span className="hiw-header__label">How It Works</span>
                    <h2 id="hiw-title" className="sr-only">Platform process — three steps from field to decision</h2>
                </div>

                {STEPS.map((step, i) => {
                    const Diagram = DIAGRAMS[i]
                    return (
                        <div key={step.id} className={`hiw-step hiw-step--${step.align}`}>
                            {/* Connector line (not on first) */}
                            {i > 0 && (
                                <div className="hiw-connector" aria-hidden="true">
                                    <div className="hiw-connector__line" />
                                    <div className="hiw-connector__chevron" />
                                </div>
                            )}

                            <div className="hiw-step__content">
                                <span className="hiw-step__ghost-num" aria-hidden="true">{step.numeral}</span>
                                <span className="hiw-step__label">{step.label}</span>
                                <h3 className="hiw-step__headline">{step.headline}</h3>
                                <p className="hiw-step__body">{step.body}</p>
                            </div>

                            <div className="hiw-step__diagram">
                                <Diagram />
                            </div>
                        </div>
                    )
                })}

                {/* Pull quote — centered after step 03 */}
                <div className="hiw-pullquote">
                    <hr className="hiw-pullquote__rule" />
                    <blockquote className="hiw-pullquote__text">
                        "Agricultural intelligence that was only available to institutions — now in a pocket-sized field sensor."
                    </blockquote>
                </div>
            </div>
        </section>
    )
}
