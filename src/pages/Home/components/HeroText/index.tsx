import DataStrip from '../DataStrip/index'
import './styles.css'

export default function HeroText() {
    return (
        <div className="hero-text">
            {/* Eyebrow label */}
            <div className="hero-text__eyebrow">
                <span className="hero-text__label">Precision Agriculture Platform — India</span>
                <span className="hero-text__label-rule" aria-hidden="true" />
            </div>

            {/* Main headline */}
            <h1 className="hero-text__headline">
                Know your soil.<br />
                <em style={{ whiteSpace: 'nowrap' }}>Grow with</em> certainty.
            </h1>

            {/* Sub-headline */}
            <p className="hero-text__subheadline">
                Real soil intelligence, proven crop guidance, and live market prices — built for Indian agriculture.
            </p>

            {/* Accent rule paragraph break */}
            <span className="hero-text__accent-rule" aria-hidden="true" />

            {/* Body copy */}
            <p className="hero-text__body">
                CropXpert reads nitrogen, potassium, pH, and moisture directly from the field. It matches your readings against 22 verified Indian crop profiles and returns a ranked recommendation in under two seconds. Paired with live mandi prices, you plan harvests with the same data your markets use.
            </p>

            {/* CTA row */}
            <div className="hero-text__cta-row">
                <a href="#platform" className="hero-text__btn-primary" id="hero-explore">
                    Explore Platform
                </a>
                <a href="#how-it-works" className="hero-text__btn-text" id="hero-how">
                    — See How It Works
                </a>
            </div>

            {/* Data strip */}
            <DataStrip />
        </div>
    )
}
