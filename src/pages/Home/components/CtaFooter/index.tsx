import './styles.css'

const LANG_CODES = ['EN', 'HI', 'MR', 'TA', 'TE'] as const

const FOOTER_LINKS = ['Platform', 'Research', 'Government Schemes', 'Contact'] as const

export default function CtaFooter() {
    return (
        <>
            {/* ── CTA Block ── */}
            <section className="cta-block" id="get-started" aria-label="Call to action">
                <div className="cta-block__rule" aria-hidden="true" />
                <div className="cta-block__inner">
                    <span className="cta-block__label">Precision Agriculture Platform — India</span>

                    <h2 className="cta-block__headline">
                        Your soil has the answer.<br />
                        <em>CropXpert reads it for you.</em>
                    </h2>

                    <div className="cta-block__buttons">
                        <a href="/onboarding" className="cta-btn cta-btn--filled" id="cta-get-started">
                            Get Started
                        </a>
                        <a href="#research" className="cta-btn cta-btn--ghost" id="cta-research">
                            View Research Paper
                        </a>
                    </div>

                    {/* Language echoes */}
                    <div className="cta-block__langs">
                        {LANG_CODES.map((code, i) => (
                            <span key={code} className="cta-lang">
                                {i > 0 && <span className="cta-lang__pipe" aria-hidden="true">|</span>}
                                {code}
                            </span>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── Footer ── */}
            <footer className="site-footer">
                <div className="site-footer__rule" aria-hidden="true" />
                <div className="site-footer__inner">

                    {/* Left — branding */}
                    <div className="footer-col footer-col--left">
                        <span className="footer-wordmark">
                            Crop<span className="footer-wordmark__x">X</span>pert
                        </span>
                        <span className="footer-institution">
                            Dept. of CINTEL — SRMIST Kattankulathur — 2024–25
                        </span>
                        <span className="footer-guide">Guide: Dr. R. Siva</span>
                    </div>

                    {/* Center — nav links */}
                    <nav className="footer-col footer-col--center" aria-label="Footer navigation">
                        {FOOTER_LINKS.map((link) => (
                            <a key={link} href={`#${link.toLowerCase().replace(/\s+/g, '-')}`} className="footer-nav-link">
                                {link}
                            </a>
                        ))}
                    </nav>

                    {/* Right — team */}
                    <div className="footer-col footer-col--right">
                        <span className="footer-team-name">Adnan Nagdiwala</span>
                        <span className="footer-team-roll">RA2211003010440</span>
                        <span className="footer-team-name" style={{ marginTop: '12px' }}>Chandra Bhayal</span>
                        <span className="footer-team-roll">RA2211003010453</span>
                    </div>

                </div>

                {/* Bottom strip */}
                <div className="site-footer__bottom">
                    <div className="site-footer__bottom-rule" aria-hidden="true" />
                    <p className="site-footer__bottom-text">
                        CropXpert — Minor Project 2024–25 — Department of Computer Science and Intelligent Systems — SRM Institute of Science and Technology
                    </p>
                </div>
            </footer>
        </>
    )
}
