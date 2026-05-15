import { useEffect, useState } from 'react'
import './styles.css'

interface Props {
    onDone: () => void
}

export default function BootSplash({ onDone }: Props) {
    const [wiping, setWiping] = useState(false)

    useEffect(() => {
        // 2.2s display, then 400ms vertical wipe
        const showTimer = setTimeout(() => {
            setWiping(true)
            setTimeout(onDone, 400)
        }, 2200)
        return () => clearTimeout(showTimer)
    }, [onDone])

    return (
        <div className={`boot-splash ${wiping ? 'boot-splash--wipe' : ''}`} aria-live="polite" aria-label="Loading CropXpert">
            <div className="boot-splash__center">
                {/* Wordmark */}
                <span className="boot-splash__wordmark">
                    Crop<span className="boot-splash__x">X</span>pert
                </span>
                <span className="boot-splash__tagline">Precision Agriculture Platform</span>

                {/* Scan-line loader */}
                <div className="boot-splash__loader" aria-hidden="true">
                    <div className="boot-splash__track">
                        <div className="boot-splash__scan" />
                    </div>
                </div>
            </div>

            {/* Institutional footer */}
            <p className="boot-splash__footer">
                Dept. of CINTEL — SRMIST Kattankulathur
            </p>
        </div>
    )
}
