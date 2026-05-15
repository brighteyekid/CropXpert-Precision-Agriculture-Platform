import './styles.css'

const PRICE_FEED = [
    { crop: 'Rice (MSP)', msp: '₹2,183', mandi: '₹2,210', delta: '+1.2%', up: true },
    { crop: 'Wheat (MSP)', msp: '₹2,275', mandi: '₹2,261', delta: '−0.6%', up: false },
    { crop: 'Soybean', msp: '₹4,600', mandi: '₹4,728', delta: '+2.8%', up: true },
]

export default function MarketSection() {
    return (
        <section className="market-section" id="market" aria-label="Market intelligence">
            <div className="market-section__inner">

                {/* Vertical decorative stripe */}
                <div className="market-section__stripe" aria-hidden="true" />

                {/* Left negative space — rotated "MARKET" label */}
                <div className="market-section__left" aria-hidden="true">
                    <span className="market-section__vert-text">MARKET</span>
                </div>

                {/* Right content */}
                <div className="market-section__right">
                    <span className="market-right__label">Market Intelligence — Novel Contribution III</span>

                    <h2 className="market-right__headline">
                        Every recommendation carries a price.
                    </h2>

                    <p className="market-right__body">
                        Real-time AGMARKNET mandi prices update the recommendation score every six hours. If your top crop is at a month-low in your district, the algorithm flags a second-ranked alternative — before you plant.
                    </p>
                    <p className="market-right__body">
                        The weighted scoring formula governs every output: each crop candidate balances agronomic compatibility against live market conditions and prevailing MSP floors, giving you a recommendation that is simultaneously scientifically grounded and commercially rational.
                    </p>

                    {/* Formula — typeset as display text */}
                    <p className="market-right__formula">
                        Score(c) = 0.60 × ML + 0.25 × MSP + 0.15 × Demand
                    </p>

                    {/* Spacer + hairline rule connecting formula to price table */}
                    <div className="market-right__bridge" aria-hidden="true" />

                    {/* Live price feed terminal */}
                    <div className="market-price-feed" aria-label="Live mandi price feed">
                        <div className="market-price-feed__header">
                            <span>CROP</span>
                            <span>MSP</span>
                            <span>MANDI</span>
                            <span>±</span>
                        </div>
                        {PRICE_FEED.map(({ crop, msp, mandi, delta, up }) => (
                            <div key={crop} className="market-price-feed__row">
                                <span className="mpf__crop">{crop}</span>
                                <span className="mpf__msp">{msp}</span>
                                <span className="mpf__mandi">{mandi}</span>
                                <span className={`mpf__delta ${up ? 'mpf__delta--up' : 'mpf__delta--down'}`}>
                                    {delta}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </section>
    )
}
