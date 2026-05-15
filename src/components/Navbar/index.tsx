import { useEffect, useRef, useState } from 'react'
import LanguageSwitcher, { type LangCode } from '../LanguageSwitcher/index'
import './styles.css'

const NAV_LINKS = ['Platform', 'Solutions', 'Research', 'Pricing'] as const

interface Props {
    activeLang: LangCode
    onLangChange: (code: LangCode) => void
}

export default function Navbar({ activeLang, onLangChange }: Props) {
    const [scrolled, setScrolled] = useState(false)
    const navRef = useRef<HTMLElement>(null)

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 60)
        window.addEventListener('scroll', onScroll, { passive: true })
        return () => window.removeEventListener('scroll', onScroll)
    }, [])

    return (
        <nav ref={navRef} className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`} aria-label="Main navigation">
            {/* Logo */}
            <a href="/" className="navbar__logo" aria-label="CropXpert home">
                Crop<span className="navbar__logo-x">X</span>pert
            </a>

            {/* Nav links */}
            <ul className="navbar__links" role="list">
                {NAV_LINKS.map((link) => (
                    <li key={link}>
                        <a href={`#${link.toLowerCase()}`} className="navbar__link">
                            {link}
                        </a>
                    </li>
                ))}
            </ul>

            {/* Language switcher — right of links, left of CTA */}
            <LanguageSwitcher variant="navbar" active={activeLang} onChange={onLangChange} />

            {/* CTA ghost button */}
            <a href="/onboarding" className="navbar__cta" id="nav-get-started">
                Get Started
            </a>
        </nav>
    )
}
