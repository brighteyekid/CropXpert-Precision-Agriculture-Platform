import './styles.css'

const SCHEME_CARDS = [
    {
        tag: 'Gov. Scheme',
        name: 'PM-KISAN',
        detail: 'Landholding below 2 ha · registered Aadhaar',
        value: '₹6,000 / year',
    },
    {
        tag: 'Zero-Interest Loan',
        name: 'Kisan Credit Card',
        detail: 'Crop loan up to ₹3L at 0% with prompt repayment',
        value: '0% interest',
    },
    {
        tag: 'Insurance',
        name: 'PM Fasal Bima',
        detail: 'Premium ≤2% rabi · ≤1.5% kharif',
        value: '100% coverage',
    },
    {
        tag: 'Subsidy',
        name: 'Soil Health Card',
        detail: 'Periodic soil testing · fertiliser advisory included',
        value: 'Free of cost',
    },
]

const SCHEME_FOOTER = 'PM-KISAN — PM Fasal Bima Yojana — KCC — NABARD — Soil Health Card'

export default function WelfareSection() {
    return (
        <section className="welfare" id="welfare" aria-label="Government welfare schemes">
            <div className="welfare__inner">

                {/* Header */}
                <span className="welfare__eyebrow">Government Integration — Novel Contribution IV</span>
                <h2 className="welfare__headline">
                    Every scheme you qualify for.{' '}
                    <em>Found for you.</em>
                </h2>
                <p className="welfare__sub">
                    CropXpert queries the MyScheme.gov.in API monthly using the farmer's registered state, landholding, crop type, and Aadhaar linkage to surface only the schemes they are actually eligible for — removing the discovery burden entirely.
                </p>

                {/* Scheme cards row */}
                <div className="welfare__cards">
                    {SCHEME_CARDS.map(({ tag, name, detail, value }) => (
                        <div key={name} className="scheme-card">
                            <span className="scheme-card__tag">{tag}</span>
                            <h3 className="scheme-card__name">{name}</h3>
                            <p className="scheme-card__detail">{detail}</p>
                            <span className="scheme-card__value">{value}</span>
                        </div>
                    ))}
                </div>

                {/* Body + CTA */}
                <p className="welfare__body">
                    Scheme eligibility checks are recalculated every 30 days as government portals publish updates. Any newly qualifying scheme triggers a push notification through the CropXpert app and SMS.
                </p>

                <div className="welfare__cta-row">
                    <a href="#schemes" className="welfare__ghost-btn" id="welfare-cta">
                        Explore All Schemes
                    </a>
                </div>

                <p className="welfare__footer-schemes">{SCHEME_FOOTER}</p>

            </div>
        </section>
    )
}
