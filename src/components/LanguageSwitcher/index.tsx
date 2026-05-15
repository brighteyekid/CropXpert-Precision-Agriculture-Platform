import { useState, useEffect } from 'react'
import './styles.css'

export const LANGUAGES = [
    { code: 'EN', label: 'English' },
    { code: 'HI', label: 'Hindi' },
    { code: 'MR', label: 'Marathi' },
    { code: 'TA', label: 'Tamil' },
    { code: 'TE', label: 'Telugu' },
] as const

export type LangCode = typeof LANGUAGES[number]['code']

interface Props {
    /** 'navbar' = horizontal hairline-separated row; 'sidebar' = vertical sticky strip */
    variant: 'navbar' | 'sidebar'
    active?: LangCode
    onChange?: (code: LangCode) => void
}

export default function LanguageSwitcher({ variant, active = 'EN', onChange }: Props) {
    const [current, setCurrent] = useState<LangCode>(active)
    const [visible, setVisible] = useState(variant === 'navbar')

    // Sidebar appears after scroll past hero (100vh)
    useEffect(() => {
        if (variant !== 'sidebar') return
        const onScroll = () => setVisible(window.scrollY > window.innerHeight * 0.6)
        window.addEventListener('scroll', onScroll, { passive: true })
        return () => window.removeEventListener('scroll', onScroll)
    }, [variant])

    const select = (code: LangCode) => {
        setCurrent(code)
        onChange?.(code)
    }

    if (variant === 'sidebar') {
        return (
            <div className={`lang-sidebar ${visible ? 'lang-sidebar--visible' : ''}`} aria-label="Language switcher">
                {LANGUAGES.map(({ code, label }) => (
                    <button
                        key={code}
                        className={`lang-sidebar__item ${current === code ? 'lang-sidebar__item--active' : ''}`}
                        onClick={() => select(code)}
                        aria-label={label}
                    >
                        {current === code && <span className="lang-sidebar__dot" aria-hidden="true" />}
                        <span className="lang-sidebar__code">{code}</span>
                        <span className="lang-sidebar__label">{label}</span>
                    </button>
                ))}
            </div>
        )
    }

    // Navbar variant
    return (
        <div className="lang-nav" aria-label="Language switcher">
            {LANGUAGES.map(({ code, label }, i) => (
                <span key={code} className="lang-nav__item">
                    {i > 0 && <span className="lang-nav__sep" aria-hidden="true" />}
                    <button
                        className={`lang-nav__code ${current === code ? 'lang-nav__code--active' : ''}`}
                        onClick={() => select(code)}
                        aria-label={label}
                        aria-pressed={current === code}
                    >
                        {code}
                    </button>
                </span>
            ))}
        </div>
    )
}
