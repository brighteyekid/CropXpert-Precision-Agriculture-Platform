import { useState } from 'react'
import './styles.css'

const LANGUAGES = [
    {
        code: 'HI' as const,
        name: 'HINDI',
        phrase: 'आपकी मिट्टी के लिए चावल की सिफारिश की जाती है।',
    },
    {
        code: 'MR' as const,
        name: 'MARATHI',
        phrase: 'तुमच्या मातीसाठी भाताची शिफारस केली जाते.',
    },
    {
        code: 'TA' as const,
        name: 'TAMIL',
        phrase: 'உங்கள் மண்ணுக்கு அரிசி பரிந்துரைக்கப்படுகிறது.',
    },
    {
        code: 'TE' as const,
        name: 'TELUGU',
        phrase: 'మీ నేల కోసం వరి సిఫారసు చేయబడింది.',
    },
]

const LANG_TABS = ['EN', 'HI', 'MR', 'TA', 'TE'] as const
type Tab = typeof LANG_TABS[number]

const COVERAGE_CARDS = [
    { lang: 'Hindi', states: 'UP · MP · Bihar · Rajasthan', speakers: '528M+ speakers' },
    { lang: 'Marathi', states: 'Maharashtra · Goa', speakers: '83M+ speakers' },
    { lang: 'Tamil', states: 'Tamil Nadu · Puducherry', speakers: '75M+ speakers' },
    { lang: 'Telugu', states: 'Andhra Pradesh · Telangana', speakers: '96M+ speakers' },
]

export default function MultilingualSection() {
    // Single source of truth — activeCode drives BOTH the tab and the panel
    const [activeCode, setActiveCode] = useState<Tab>('TA')

    const handleSelect = (code: Tab) => setActiveCode(code)

    return (
        <section className="multilingual" id="multilingual" aria-label="Multilingual platform feature">
            <div className="multilingual__inner">

                {/* LEFT — Dark language demo panel */}
                <div className="multilingual__dark-panel">
                    <span className="ml-panel__eyebrow">Live Interface — Vernacular Mode</span>

                    <div className="ml-panel__blocks">
                        {LANGUAGES.map(({ code, name, phrase }) => (
                            <div
                                key={code}
                                className={`ml-block ${activeCode === code ? 'ml-block--active' : ''}`}
                                onClick={() => handleSelect(code)}
                            >
                                <span className="ml-block__lang">{name}</span>
                                <p className="ml-block__phrase">{phrase}</p>
                                <div className="ml-block__rule" />
                            </div>
                        ))}
                    </div>

                    {/* Language tab selector */}
                    <div className="ml-panel__tabs">
                        {LANG_TABS.map((tab) => (
                            <button
                                key={tab}
                                className={`ml-tab ${activeCode === tab ? 'ml-tab--active' : ''}`}
                                onClick={() => handleSelect(tab)}
                                aria-pressed={activeCode === tab}
                            >
                                {tab}
                            </button>
                        ))}
                    </div>
                </div>

                {/* RIGHT — Light explanation panel */}
                <div className="multilingual__light-panel">
                    <span className="ml-right__label">Vernacular First — Novel Contribution II</span>

                    <h2 className="ml-right__headline">
                        Speaks the language of 400 million farmers.
                    </h2>

                    <p className="ml-right__body">
                        CropXpert delivers every ML output, advisory text, and government scheme detail in the farmer's native script — Hindi, Marathi, Tamil, and Telugu. Browser locale auto-detection selects the right language on first load, with no additional input required. Recommendations are localised end-to-end: the model output, the scheme name, and the mandi price advisory all render in the selected script. Coverage expands with each software release.
                    </p>

                    {/* 2×2 language coverage grid */}
                    <div className="ml-right__cards">
                        {COVERAGE_CARDS.map(({ lang, states, speakers }) => (
                            <div key={lang} className="ml-coverage-card">
                                <h3 className="ml-coverage-card__lang">{lang}</h3>
                                <p className="ml-coverage-card__states">{states}</p>
                                <span className="ml-coverage-card__speakers">{speakers}</span>
                            </div>
                        ))}
                    </div>

                    {/* SMS / zero-smartphone band */}
                    <div className="ml-sms-band">
                        <div className="ml-sms-band__left">
                            <span className="ml-sms-band__label">Zero Smartphone Access</span>
                            <code className="ml-sms-band__code">CROP N90 P42 K43 PH6.5 DIST PUNE</code>
                        </div>
                        <p className="ml-sms-band__note">Works on any basic keypad phone.</p>
                    </div>
                </div>

            </div>
        </section>
    )
}
