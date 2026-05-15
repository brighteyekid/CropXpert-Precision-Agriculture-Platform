import { useState } from 'react'
import Navbar from '../../components/Navbar/index'
import LanguageBanner from '../../components/LanguageBanner/index'
import LanguageSwitcher, { type LangCode } from '../../components/LanguageSwitcher/index'
import Hero from './components/Hero/index'
import HowItWorks from './components/HowItWorks/index'
import MultilingualSection from './components/MultilingualSection/index'
import MarketSection from './components/MarketSection/index'
import WelfareSection from './components/WelfareSection/index'
import DashboardPreview from './components/DashboardPreview/index'
import SocialProof from './components/SocialProof/index'
import CtaFooter from './components/CtaFooter/index'
import './styles.css'

export default function Home() {
    // Single global language state — drives Navbar switcher, sidebar switcher, and banner
    const [activeLang, setActiveLang] = useState<LangCode>('EN')

    return (
        <main className="home">
            {/* Fixed elements */}
            <Navbar activeLang={activeLang} onLangChange={setActiveLang} />
            <LanguageBanner activeLang={activeLang} />

            {/* Page sections */}
            <Hero />
            <HowItWorks />
            <MultilingualSection />
            <MarketSection />
            <WelfareSection />
            <DashboardPreview />
            <SocialProof />
            <CtaFooter />

            {/* Sticky sidebar language switcher — fades in after hero */}
            <LanguageSwitcher variant="sidebar" active={activeLang} onChange={setActiveLang} />
        </main>
    )
}
