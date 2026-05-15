import { useEffect, useRef } from 'react'
import './styles.css'

const STATS = [
    { numeral: '99.2', label: 'accuracy on 22 crops', unit: '%', isDecimal: true, hasComma: false, raw: 99.2 },
    { numeral: '3,600', label: 'hardware cost INR', unit: '₹', isDecimal: false, hasComma: true, raw: 3600 },
    { numeral: '22', label: 'Indian crop varieties', unit: '', isDecimal: false, hasComma: false, raw: 22 },
] as const

interface StatBlockProps {
    numeral: string
    label: string
    unit: string
    isDecimal: boolean
    hasComma: boolean
    raw: number
    index: number
}

function StatBlock({ numeral, label, unit, isDecimal, hasComma, raw, index }: StatBlockProps) {
    const numRef = useRef<HTMLSpanElement>(null)
    const triggered = useRef(false)

    useEffect(() => {
        const el = numRef.current
        if (!el) return

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting && !triggered.current) {
                    triggered.current = true
                    const duration = 1800 + index * 200
                    const start = performance.now()

                    const tick = (now: number) => {
                        const progress = Math.min((now - start) / duration, 1)
                        const ease = 1 - Math.pow(1 - progress, 3)
                        const current = raw * ease

                        if (isDecimal) {
                            el.textContent = current.toFixed(1)
                        } else if (hasComma) {
                            el.textContent = Math.floor(current).toLocaleString('en-IN')
                        } else {
                            el.textContent = Math.floor(current).toString()
                        }

                        if (progress < 1) requestAnimationFrame(tick)
                    }
                    requestAnimationFrame(tick)
                }
            },
            { threshold: 0.3 }
        )
        observer.observe(el)
        return () => observer.disconnect()
    }, [raw, index, isDecimal, hasComma])

    return (
        <div className="stat-block">
            <div className="stat-block__numeral">
                <span ref={numRef} className="stat-block__number">
                    {numeral}
                </span>
                {unit && <span className="stat-block__unit">{unit}</span>}
            </div>
            <p className="stat-block__label">{label}</p>
        </div>
    )
}

export default function DataStrip() {
    return (
        <div className="data-strip" aria-label="Platform statistics">
            {STATS.map((stat, i) => (
                <StatBlock key={stat.label} {...stat} index={i} />
            ))}
        </div>
    )
}
