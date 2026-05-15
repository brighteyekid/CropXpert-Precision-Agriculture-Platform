import './styles.css'

const LAYERS = [
    { id: 'nitrogen', label: 'N — Nitrogen', y: 0 },
    { id: 'potassium', label: 'K — Potassium', y: 1 },
    { id: 'acidity', label: 'pH — Acidity', y: 2 },
    { id: 'moisture', label: 'H₂O — Moisture', y: 3 },
] as const

const GRID_COLS = 18
const GRID_ROWS = 24
const CELL_W = 100 / GRID_COLS
const CELL_H = 100 / GRID_ROWS

export default function SoilGrid() {
    // Generate dots for grid
    const dots: { cx: number; cy: number; opacity: number }[] = []
    for (let r = 0; r < GRID_ROWS; r++) {
        for (let c = 0; c < GRID_COLS; c++) {
            // Vary opacity per layer band
            const band = Math.floor((r / GRID_ROWS) * 4)
            const baseOpacity = [0.18, 0.12, 0.15, 0.10][band] ?? 0.12
            const jitter = (Math.sin(r * 7.3 + c * 13.1) + 1) * 0.5 * 0.08
            dots.push({
                cx: CELL_W * c + CELL_W / 2,
                cy: CELL_H * r + CELL_H / 2,
                opacity: baseOpacity + jitter,
            })
        }
    }

    return (
        <div className="soil-grid" aria-hidden="true">
            {/* Ghost numeral backdrop */}
            <div className="soil-grid__ghost">22</div>

            {/* SVG field */}
            <svg
                className="soil-grid__svg"
                viewBox="0 0 100 100"
                preserveAspectRatio="none"
                xmlns="http://www.w3.org/2000/svg"
            >
                {/* Horizontal band dividers */}
                {[25, 50, 75].map((y) => (
                    <line
                        key={y}
                        x1="0" y1={y} x2="100" y2={y}
                        stroke="var(--color-green-mid)"
                        strokeWidth="0.15"
                        strokeOpacity="0.25"
                    />
                ))}

                {/* Dot grid */}
                {dots.map(({ cx, cy, opacity }, i) => (
                    <circle
                        key={i}
                        cx={cx}
                        cy={cy}
                        r="0.5"
                        fill="var(--color-green-dark)"
                        fillOpacity={opacity}
                    />
                ))}

                {/* Reticle — centered at 50, 50 */}
                <circle className="reticle-core" cx="50" cy="50" r="1.5"
                    fill="var(--color-green-accent)" fillOpacity="0.9" />
                <circle className="reticle-ring-1" cx="50" cy="50" r="4"
                    fill="none" stroke="var(--color-green-accent)" strokeWidth="0.3" />
                <circle className="reticle-ring-2" cx="50" cy="50" r="4"
                    fill="none" stroke="var(--color-green-accent)" strokeWidth="0.15" />
                {/* Crosshair lines */}
                <line x1="47" y1="50" x2="46" y2="50" stroke="var(--color-green-accent)" strokeWidth="0.25" strokeOpacity="0.6" />
                <line x1="53" y1="50" x2="54" y2="50" stroke="var(--color-green-accent)" strokeWidth="0.25" strokeOpacity="0.6" />
                <line x1="50" y1="47" x2="50" y2="46" stroke="var(--color-green-accent)" strokeWidth="0.25" strokeOpacity="0.6" />
                <line x1="50" y1="53" x2="50" y2="54" stroke="var(--color-green-accent)" strokeWidth="0.25" strokeOpacity="0.6" />
            </svg>

            {/* Layer annotations — right side */}
            <div className="soil-grid__annotations">
                {LAYERS.map(({ id, label }) => (
                    <div key={id} className="soil-grid__annotation">
                        <span className="soil-grid__annotation-dot" />
                        {label}
                    </div>
                ))}
            </div>
        </div>
    )
}
