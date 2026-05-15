import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import LanguageSwitcher, { type LangCode } from '../../components/LanguageSwitcher/index'
import client from '../../api/client'
import './styles.css'

// ──────────────────────────── Step indicator ────────────────────────────────
const STEPS = [
    { num: '01', name: 'Your Location' },
    { num: '02', name: 'Your Farm' },
    { num: '03', name: 'Your Soil' },
] as const

function StepIndicator({ current }: { current: number }) {
    return (
        <div className="step-indicator">
            {STEPS.map(({ num, name }, i) => {
                const state = i < current ? 'done' : i === current ? 'active' : 'idle'
                return (
                    <div key={num} className={`si-item si-item--${state}`}>
                        <div className="si-item__marker" aria-hidden="true">
                            {state === 'done' && <span className="si-item__check" />}
                            {state === 'active' && <span className="si-item__diamond" />}
                        </div>
                        <span className="si-item__num">{num}</span>
                        <span className="si-item__name">{name}</span>
                    </div>
                )
            })}
        </div>
    )
}

// ──────────────────────────── Step 1 — Location ──────────────────────────────
const DISTRICTS = [
    'Pune, Maharashtra', 'Nashik, Maharashtra', 'Nagpur, Maharashtra',
    'Lucknow, Uttar Pradesh', 'Patna, Bihar', 'Jaipur, Rajasthan',
    'Coimbatore, Tamil Nadu', 'Madurai, Tamil Nadu', 'Hyderabad, Telangana',
    'Mysuru, Karnataka', 'Indore, Madhya Pradesh', 'Bhopal, Madhya Pradesh',
    'Kolhapur, Maharashtra', 'Solapur, Maharashtra', 'Aurangabad, Maharashtra',
    'Varanasi, Uttar Pradesh', 'Agra, Uttar Pradesh', 'Kanpur, Uttar Pradesh',
    'Ahmedabad, Gujarat', 'Surat, Gujarat', 'Rajkot, Gujarat',
    'Kochi, Kerala', 'Thiruvananthapuram, Kerala', 'Visakhapatnam, Andhra Pradesh',
    'Vijayawada, Andhra Pradesh', 'Bhubaneswar, Odisha', 'Ranchi, Jharkhand',
    'Raipur, Chhattisgarh', 'Chandigarh, Punjab', 'Ludhiana, Punjab',
]

function Step1({ onNext }: { onNext: (v: string) => void }) {
    const [query, setQuery] = useState('')
    const [focused, setFocused] = useState(false)
    const [selected, setSelected] = useState('')
    const [geoLoading, setGeoLoading] = useState(false)

    const matches = query.length >= 1
        ? DISTRICTS.filter(d => d.toLowerCase().includes(query.toLowerCase())).slice(0, 6)
        : []

    const pick = (d: string) => { setSelected(d); setQuery(d); setFocused(false) }

    const useGeo = () => {
        if (!navigator.geolocation) return
        setGeoLoading(true)
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                try {
                    const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`)
                    const data = await resp.json()
                    const district = data.address?.county || data.address?.city || data.address?.town || ''
                    const state = data.address?.state || ''
                    const loc = `${district}, ${state}`
                    setQuery(loc)
                    setSelected(loc)
                } catch {
                    // Nominatim failed — try forward search with coords
                    try {
                        const lat = pos.coords.latitude.toFixed(4)
                        const lng = pos.coords.longitude.toFixed(4)
                        const r2 = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=10&addressdetails=1`)
                        const d2 = await r2.json()
                        const district2 = d2.address?.county || d2.address?.city || d2.address?.town || d2.address?.state_district || ''
                        const state2 = d2.address?.state || ''
                        if (district2) {
                            const loc2 = `${district2}, ${state2}`
                            setQuery(loc2)
                            setSelected(loc2)
                        }
                        // If still no district, leave field empty — don't use raw coords
                    } catch { /* leave blank */ }
                }
                setGeoLoading(false)
            },
            () => setGeoLoading(false),
            { enableHighAccuracy: true, timeout: 10000 }
        )
    }

    const canProceed = !!(selected || query.trim())

    return (
        <div className="ob-step">
            <span className="ob-step__label">Step 01 — Your Location</span>
            <h2 className="ob-step__headline">Where is your farm?</h2>

            <div className="ob-field ob-field--search">
                {query && <span className="ob-field__float-label">District, State</span>}
                <input
                    className="ob-field__input"
                    type="text"
                    placeholder="District, State"
                    value={query}
                    onChange={e => { setQuery(e.target.value); setSelected('') }}
                    onFocus={() => setFocused(true)}
                    onBlur={() => setTimeout(() => setFocused(false), 200)}
                    autoComplete="off"
                    id="ob-district"
                    aria-label="Enter your district and state"
                />
                {focused && matches.length > 0 && (
                    <ul className="ob-dropdown" role="listbox">
                        {matches.map(d => (
                            <li key={d} className="ob-dropdown__item"
                                onMouseDown={() => pick(d)} role="option" aria-selected={d === selected}>
                                {d}
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            <button className="ob-geo-btn" type="button" id="ob-use-location" onClick={useGeo} disabled={geoLoading}>
                <span className="ob-geo-btn__diamond" aria-hidden="true" />
                {geoLoading ? 'Detecting location…' : 'Use my current location'}
            </button>

            <div className="ob-nav ob-nav--step1">
                <span className="ob-nav__counter">Step 1 of 3</span>
                <button className="ob-next-btn" onClick={() => canProceed && onNext(selected || query)} id="ob-next-1"
                    style={{ opacity: canProceed ? 1 : 0.4 }}>
                    Next — Farm Details
                </button>
            </div>
        </div>
    )
}

// ──────────────────────────── Step 2 — Farm ──────────────────────────────────
const SOIL_TYPES = ['CLAY', 'LOAM', 'SANDY', 'SILT', 'MIXED'] as const
type SoilType = typeof SOIL_TYPES[number]

function Step2({ onNext, onBack }: {
    onNext: (v: { size: string; history: string; soil: SoilType }) => void
    onBack: () => void
}) {
    const [size, setSize] = useState('')
    const [history, setHistory] = useState('')
    const [soil, setSoil] = useState<SoilType | null>(null)

    const canProceed = !!soil && !!size.trim()

    return (
        <div className="ob-step">
            <span className="ob-step__label">Step 02 — Your Farm</span>
            <h2 className="ob-step__headline">Tell us about your land.</h2>

            <div className="ob-fields-row">
                <div className="ob-field">
                    {size && <span className="ob-field__float-label">Farm size (hectares)</span>}
                    <input className="ob-field__input" type="number" min="0" step="0.1" placeholder="Hectares"
                        value={size} onChange={e => setSize(e.target.value)} id="ob-size" aria-label="Farm size in hectares" />
                </div>
                <div className="ob-field">
                    {history && <span className="ob-field__float-label">Primary crop history</span>}
                    <input className="ob-field__input" type="text" placeholder="What did you grow last season?"
                        value={history} onChange={e => setHistory(e.target.value)} id="ob-history" aria-label="Previous crop" />
                </div>
            </div>

            <div className="ob-soil-selector" role="radiogroup" aria-label="Soil type">
                {SOIL_TYPES.map(type => (
                    <button key={type} className={`ob-soil-btn ${soil === type ? 'ob-soil-btn--active' : ''}`}
                        onClick={() => setSoil(type)} role="radio" aria-checked={soil === type} id={`ob-soil-${type.toLowerCase()}`}>
                        {type}
                    </button>
                ))}
            </div>

            <div className="ob-nav">
                <button className="ob-back-btn" onClick={onBack} id="ob-back-2">Back</button>
                <span className="ob-nav__counter">Step 2 of 3</span>
                <button className="ob-next-btn" onClick={() => canProceed && onNext({ size, history, soil: soil! })} id="ob-next-2"
                    style={{ opacity: canProceed ? 1 : 0.4 }}>
                    Next — Soil Readings
                </button>
            </div>
        </div>
    )
}

// ──────────────────────────── Arduino UNO Serial ─────────────────────────────
function useArduinoSerial() {
    const portRef = useRef<SerialPort | null>(null)
    const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null)
    const [connected, setConnected] = useState(false)
    const [reading, setReading] = useState(false)
    const bufferRef = useRef('')

    const parseSerialLine = useCallback((line: string): Record<string, string> | null => {
        // Expected Arduino JSON: {"N":90,"P":42,"K":43,"ph":6.5,"moisture":58,"temp":25}
        try {
            const data = JSON.parse(line.trim())
            const result: Record<string, string> = {}
            if (data.N !== undefined || data.n !== undefined) result.n = String(data.N ?? data.n)
            if (data.P !== undefined || data.p !== undefined) result.p = String(data.P ?? data.p)
            if (data.K !== undefined || data.k !== undefined) result.k = String(data.K ?? data.k)
            if (data.ph !== undefined || data.pH !== undefined) result.ph = String(data.ph ?? data.pH)
            if (data.moisture !== undefined || data.moist !== undefined) result.moisture = String(data.moisture ?? data.moist)
            if (data.temp !== undefined || data.temperature !== undefined) result.temp = String(data.temp ?? data.temperature)
            if (data.humidity !== undefined) result.humidity = String(data.humidity)
            return Object.keys(result).length > 0 ? result : null
        } catch {
            // Try CSV: N,P,K,pH,moisture,temp
            const parts = line.split(',').map(s => s.trim())
            if (parts.length >= 5 && parts.every(p => !isNaN(parseFloat(p)))) {
                return {
                    n: parts[0], p: parts[1], k: parts[2],
                    ph: parts[3], moisture: parts[4],
                    temp: parts[5] || '25',
                }
            }
            return null
        }
    }, [])

    const connect = useCallback(async (): Promise<boolean> => {
        if (!('serial' in navigator)) return false
        try {
            const port = await (navigator as any).serial.requestPort({
                filters: [
                    { usbVendorId: 0x2341 }, // Arduino
                    { usbVendorId: 0x1A86 }, // CH340 clone
                    { usbVendorId: 0x10C4 }, // CP2102
                ],
            })
            await port.open({ baudRate: 9600 })
            portRef.current = port
            setConnected(true)
            return true
        } catch {
            return false
        }
    }, [])

    const readOnce = useCallback(async (onData: (values: Record<string, string>) => void) => {
        if (!portRef.current?.readable) return
        setReading(true)
        const decoder = new TextDecoderStream()
        const readableStreamClosed = portRef.current.readable.pipeTo(decoder.writable as any)
        const reader = decoder.readable.getReader()
        readerRef.current = reader as any
        bufferRef.current = ''

        const timeout = setTimeout(() => {
            reader.cancel()
        }, 15000) // 15s max read time

        try {
            while (true) {
                const { value, done } = await reader.read()
                if (done) break
                bufferRef.current += value
                const lines = bufferRef.current.split('\n')
                bufferRef.current = lines.pop() || ''
                for (const line of lines) {
                    if (line.trim()) {
                        const parsed = parseSerialLine(line)
                        if (parsed) {
                            clearTimeout(timeout)
                            onData(parsed)
                            reader.cancel()
                            setReading(false)
                            return
                        }
                    }
                }
            }
        } catch { /* stream cancelled */ }
        clearTimeout(timeout)
        setReading(false)
        try { await readableStreamClosed.catch(() => { }) } catch { /* ignore */ }
    }, [parseSerialLine])

    const disconnect = useCallback(async () => {
        try {
            readerRef.current?.cancel()
            await portRef.current?.close()
        } catch { /* ignore */ }
        portRef.current = null
        setConnected(false)
    }, [])

    return { connected, reading, connect, readOnce, disconnect, supported: 'serial' in navigator }
}

// ──────────────────────────── Step 3 — Soil ──────────────────────────────────
const SOIL_FIELDS = [
    { id: 'n', label: 'N — Nitrogen', unit: 'mg/kg', auto: false },
    { id: 'p', label: 'P — Phosphorus', unit: 'mg/kg', auto: false },
    { id: 'k', label: 'K — Potassium', unit: 'mg/kg', auto: false },
    { id: 'ph', label: 'pH — Acidity', unit: '', auto: false },
    { id: 'moisture', label: 'Moisture %', unit: '%', auto: false },
    { id: 'temp', label: 'Temperature °C', unit: '°C', auto: true },
    { id: 'humidity', label: 'Humidity %', unit: '%', auto: true },
    { id: 'rainfall', label: 'Avg. Rainfall', unit: 'mm', auto: true },
] as const

interface Step3Props {
    onAnalyse: (soilValues: Record<string, string>) => void
    onBack: () => void
    location: string
}

function Step3({ onAnalyse, onBack, location }: Step3Props) {
    const [values, setValues] = useState<Record<string, string>>({})
    const [loading, setLoading] = useState(false)
    const [sensorMode, setSensorMode] = useState<'none' | 'connecting' | 'connected' | 'reading' | 'done'>('none')
    const arduino = useArduinoSerial()

    // Auto-fetch temperature, humidity & rainfall via /api/weather/current (open-meteo, no API key)
    useEffect(() => {
        async function fetchWeather() {
            try {
                const [district] = location.split(',').map(s => s.trim())
                if (!district) return
                const resp = await fetch(`http://localhost:8000/api/weather/current?city=${encodeURIComponent(district)}`)
                if (resp.ok) {
                    const w = await resp.json()
                    setValues(v => ({
                        ...v,
                        ...(w.temperature != null ? { temp: String(w.temperature) } : {}),
                        ...(w.humidity != null ? { humidity: String(w.humidity) } : {}),
                        ...(w.rainfall != null ? { rainfall: String(Math.round(w.rainfall)) } : { rainfall: v.rainfall || '842' }),
                    }))
                    return
                }
            } catch { /* ignore */ }
            // Fallback
            setValues(v => ({ ...v, rainfall: v.rainfall || '842' }))
        }
        fetchWeather()
    }, [location])

    const handleConnectArduino = async () => {
        setSensorMode('connecting')
        const ok = await arduino.connect()
        if (ok) {
            setSensorMode('connected')
            // Immediately start reading
            setSensorMode('reading')
            arduino.readOnce((data) => {
                setValues(v => ({ ...v, ...data }))
                setSensorMode('done')
            })
        } else {
            setSensorMode('none')
        }
    }

    const handleAnalyse = () => {
        // Validate at least N, P, K are filled
        const n = parseFloat(values.n || '0')
        const p = parseFloat(values.p || '0')
        const k = parseFloat(values.k || '0')
        if (n <= 0 && p <= 0 && k <= 0) {
            alert('Please enter at least Nitrogen (N), Phosphorus (P), and Potassium (K) values.')
            return
        }
        setLoading(true)
        onAnalyse(values)
    }

    const hasAllValues = !!(values.n && values.p && values.k && values.ph && values.moisture && values.temp)

    return (
        <div className="ob-step">
            <span className="ob-step__label">Step 03 — Soil Readings</span>
            <h2 className="ob-step__headline">Enter your sensor values.</h2>

            {/* Sensor connection band */}
            <div className="ob-sensor-band">
                {sensorMode === 'none' && (
                    <>
                        {arduino.supported ? (
                            <button className="ob-sensor-connect-btn" onClick={handleConnectArduino} id="ob-connect-sensor">
                                <span className="ob-geo-btn__diamond" aria-hidden="true" />
                                Connect Arduino / UNO Sensor
                            </button>
                        ) : (
                            <span className="ob-sensor-note">Web Serial not supported in this browser — enter values manually.</span>
                        )}
                        <span className="ob-sensor-note">If you don't have a sensor, fill in values from your soil test report below.</span>
                    </>
                )}
                {sensorMode === 'connecting' && (
                    <span className="ob-sensor-status ob-sensor-status--connecting">
                        <span className="ob-geo-btn__diamond" aria-hidden="true" />
                        Connecting to sensor…
                    </span>
                )}
                {(sensorMode === 'connected' || sensorMode === 'reading') && (
                    <span className="ob-sensor-status ob-sensor-status--reading">
                        <span className="ob-geo-btn__diamond" aria-hidden="true" />
                        Reading sensor data… Stand by.
                        <span className="ob-scan-line" style={{ marginLeft: 12 }}>
                            <span className="ob-scan-line__track"><span className="ob-scan-line__bright" /></span>
                        </span>
                    </span>
                )}
                {sensorMode === 'done' && (
                    <span className="ob-sensor-status ob-sensor-status--done">
                        <span className="ob-geo-btn__diamond" aria-hidden="true" />
                        Sensor values received! You can edit them below if needed.
                    </span>
                )}
            </div>

            <div className="ob-soil-grid">
                {SOIL_FIELDS.map(({ id, label, unit, auto }) => (
                    <div key={id} className={`ob-field ${auto ? 'ob-field--auto' : ''} ${sensorMode === 'done' && values[id] ? 'ob-field--auto' : ''}`}>
                        <span className="ob-field__float-label">{label}{unit ? ` (${unit})` : ''}</span>
                        {auto && (
                            <span className="ob-field__auto-note">
                                {id === 'rainfall' ? 'Auto-fetched · 7-day avg from open-meteo.com' : 'Auto-fetched · current from open-meteo.com'}
                            </span>
                        )}
                        {!auto && sensorMode === 'done' && values[id] && (
                            <span className="ob-field__auto-note">From connected sensor.</span>
                        )}
                        <input
                            className="ob-field__input"
                            type="number"
                            min="0"
                            step={id === 'ph' ? '0.1' : '1'}
                            placeholder={auto ? '' : '—'}
                            value={values[id] ?? ''}
                            onChange={e => setValues(v => ({ ...v, [id]: e.target.value }))}
                            readOnly={auto}
                            id={`ob-soil-${id}`}
                            aria-label={label}
                        />
                    </div>
                ))}
            </div>

            <div className="ob-info-band">
                {hasAllValues
                    ? '✓ All soil parameters filled. Click "Analyse My Soil" to get your crop recommendation.'
                    : 'If your readings are blank, a field estimate will be used based on ICAR district averages for your location.'}
            </div>

            <div className="ob-nav">
                <button className="ob-back-btn" onClick={onBack} id="ob-back-3">Back</button>
                <span className="ob-nav__counter">Step 3 of 3</span>
                <button
                    className={`ob-next-btn ob-next-btn--analyse ${loading ? 'ob-next-btn--scanning' : ''}`}
                    onClick={handleAnalyse}
                    id="ob-analyse"
                    disabled={loading}
                >
                    {loading ? (
                        <span className="ob-scan-line" aria-label="Analysing…">
                            <span className="ob-scan-line__track">
                                <span className="ob-scan-line__bright" />
                            </span>
                        </span>
                    ) : 'Analyse My Soil'}
                </button>
            </div>
        </div>
    )
}

// ──────────────────────────── Main Onboarding page ──────────────────────────
export default function Onboarding() {
    const navigate = useNavigate()
    const [step, setStep] = useState(0)
    const [lang, setLang] = useState<LangCode>('EN')
    const [location, setLocation] = useState('')
    const [farmData, setFarmData] = useState({ size: '', history: '', soil: '' })
    const [error, setError] = useState('')

    const handleStep1 = (loc: string) => {
        setLocation(loc)
        setStep(1)
    }

    const handleStep2 = (data: { size: string; history: string; soil: string }) => {
        setFarmData(data)
        setStep(2)
    }

    const handleAnalyse = async (soilValues: Record<string, string>) => {
        setError('')
        try {
            const [district, state] = location.split(',').map(s => s.trim())
            const mobile = '9876543210'

            // 1. Auth — send + verify OTP (dev mode auto-accepts)
            await client.post('/api/auth/send-otp', { mobile })
            const authResp = await client.post('/api/auth/verify-otp', { mobile, otp: '000000' })
            const token = authResp.data.access_token
            localStorage.setItem('cropxpert_token', token)
            localStorage.setItem('cropxpert_farmer_id', String(authResp.data.farmer_id))

            // 2. Update farmer profile with onboarding data
            await client.put('/api/farmer/profile', {
                name: farmData.history ? `${farmData.history} farmer` : 'Crop Farmer',
                state: state || 'Maharashtra',
                district: district || 'Pune',
                acreage: parseFloat(farmData.size) || 1.0,
                language_preference: lang.toLowerCase(),
            })

            // 3. Post sensor reading
            const reading = await client.post('/api/sensors/reading', {
                nitrogen: parseFloat(soilValues.n) || 50,
                phosphorus: parseFloat(soilValues.p) || 40,
                potassium: parseFloat(soilValues.k) || 40,
                ph: parseFloat(soilValues.ph) || 6.5,
                moisture: parseFloat(soilValues.moisture) || 50,
                temperature: parseFloat(soilValues.temp) || 25,
                humidity: parseFloat(soilValues.humidity) || 70,
            })

            // 4. Run ML prediction
            await client.post('/api/predict', { reading_id: reading.data.id })

            // 5. Navigate to dashboard
            setTimeout(() => navigate('/dashboard'), 1000)
        } catch (err: unknown) {
            console.error('Onboarding error:', err)
            const msg = err instanceof Error ? err.message : 'Unknown error'
            setError(`Server error: ${msg}. Make sure the backend is running on port 8000.`)
        }
    }

    return (
        <div className="onboarding">
            <aside className="ob-left">
                <a href="/" className="ob-left__wordmark" aria-label="CropXpert home">
                    Crop<span className="ob-left__x">X</span>pert
                </a>
                <div className="ob-left__divider" aria-hidden="true" />
                <StepIndicator current={step} />
                {error && (
                    <div className="ob-error-band">
                        <span className="ob-error-band__icon">!</span>
                        <p className="ob-error-band__text">{error}</p>
                    </div>
                )}
                <p className="ob-left__privacy">
                    Your data is stored securely in the CropXpert database. It is never shared with third parties.
                </p>
            </aside>

            <main className="ob-right">
                <div className="ob-right__lang">
                    <LanguageSwitcher variant="navbar" active={lang} onChange={setLang} />
                </div>

                {step === 0 && <Step1 onNext={handleStep1} />}
                {step === 1 && <Step2 onNext={handleStep2} onBack={() => setStep(0)} />}
                {step === 2 && <Step3 onAnalyse={handleAnalyse} onBack={() => setStep(1)} location={location} />}
            </main>
        </div>
    )
}
