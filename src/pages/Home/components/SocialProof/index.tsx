import './styles.css'

const PROOF_CARDS = [
    {
        label: 'ACCURACY',
        numeral: '99.2',
        superscript: '%',
        detail: 'held-out test set — 22 Indian crop categories — Random Forest classifier',
    },
    {
        label: 'INFERENCE',
        numeral: '2.3',
        superscript: 'ms',
        detail: 'mean inference time — Flask-hosted server — Joblib-serialized model — 4.7 MB',
    },
    {
        label: 'HARDWARE',
        numeral: '3,600',
        superscript: 'INR',
        detail: 'complete bill of materials — permanently reusable — comparable to one lab test',
    },
]

const REFS = [
    'IEEE IEMCON 2017 — Pudumalar et al. — Random Forest baseline',
    'IEEE Access Vol.9 — Sharma et al. — Sensor-satellite fusion methodology',
]

export default function SocialProof() {
    return (
        <section className="social-proof" id="research" aria-label="Research foundation and credibility">
            <div className="social-proof__inner">

                {/* Ghost numeral — training dataset size */}
                <span className="sp-ghost" aria-hidden="true">2,200</span>

                {/* Left column */}
                <div className="sp-left">
                    <span className="sp-left__label">Research Foundation — SRMIST CINTEL</span>

                    <h2 className="sp-left__headline">
                        Built on peer-reviewed research. Validated on Indian field data.
                    </h2>

                    <p className="sp-left__body">
                        The system was developed at SRM Institute of Science and Technology, Kattankulathur, under the guidance of Dr. R. Siva in the Department of Computer Science and Intelligent Systems. The ML methodology follows established benchmarks from eight published papers in IEEE, Sensors, and Computers and Electronics in Agriculture. Tested against 2,200 labelled samples across 22 Indian crop categories.
                    </p>

                    <div className="sp-refs">
                        {REFS.map((ref) => (
                            <div key={ref} className="sp-ref">
                                <span className="sp-ref__bullet" aria-hidden="true" />
                                <span className="sp-ref__text">{ref}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right column — proof cards */}
                <div className="sp-right">
                    {PROOF_CARDS.map(({ label, numeral, superscript, detail }) => (
                        <div key={label} className="sp-card">
                            <span className="sp-card__label">{label}</span>
                            <div className="sp-card__numeral-row">
                                <span className="sp-card__numeral">{numeral}</span>
                                <span className="sp-card__superscript">{superscript}</span>
                            </div>
                            <span className="sp-card__detail">{detail}</span>
                        </div>
                    ))}

                    {/* Conviction quote strip */}
                    <div className="sp-quote-strip">
                        <blockquote className="sp-quote">
                            A platform that speaks the farmer's language, knows their soil, and watches the market on their behalf.
                        </blockquote>
                    </div>
                </div>

            </div>
        </section>
    )
}
