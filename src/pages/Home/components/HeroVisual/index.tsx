import { useEffect, useRef } from 'react'
import SoilGrid from '../SoilGrid/index'
import './styles.css'

export default function HeroVisual() {
    const visualRef = useRef<HTMLDivElement>(null)

    // Parallax: ghost numeral drifts upward on scroll
    useEffect(() => {
        const el = visualRef.current
        if (!el) return
        const ghost = el.querySelector<HTMLElement>('.soil-grid__ghost')
        if (!ghost) return

        const onScroll = () => {
            const offset = window.scrollY * 0.18
            ghost.style.transform = `translateY(-${offset}px)`
        }
        window.addEventListener('scroll', onScroll, { passive: true })
        return () => window.removeEventListener('scroll', onScroll)
    }, [])

    return (
        <div ref={visualRef} className="hero-visual">
            <SoilGrid />
        </div>
    )
}
