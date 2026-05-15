import HeroText from '../HeroText/index'
import HeroVisual from '../HeroVisual/index'
import './styles.css'

export default function Hero() {
    return (
        <section className="hero" id="hero" aria-label="Hero section">
            <div className="hero__inner">
                {/* Left: 60% text column */}
                <div className="hero__left">
                    <HeroText />
                </div>

                {/* Right: 40% visual column */}
                <div className="hero__right">
                    <HeroVisual />
                </div>
            </div>
        </section>
    )
}
