import { useState, useEffect } from 'react'
import client from '../../../api/client'
import type { LangCode } from '../../../components/LanguageSwitcher/index'

interface MarketCrop { crop: string; msp_inr: number; mandi_price: number; delta_pct: number }
interface TrendData { crop: string; labels: string[]; data: number[] }

const LABELS: Record<string, Record<string, string>> = {
    header: { EN: 'Market Prices — Live AGMARKNET', HI: 'बाजार मूल्य — सक्रिय एग्मार्कनेट', MR: 'बाजारभाव — लाइव्ह एग्मार्कनेट', TA: 'சந்தை விலைகள் — நேரடி ஏஜிமார்க்நெட்', TE: 'మార్కెట్ ధరలు — లైవ్ అగ్మార్క్‌నెట్' },
    refresh: { EN: 'Refresh', HI: 'रिफ्रेश', MR: 'रिफ्रेश', TA: 'புதுப்பிக்கவும்', TE: 'రిఫ్రెష్' },
}

function Sparkline14({ values, up }: { values: number[]; up: boolean }) {
    if (!values || values.length < 2) return null
    const min = Math.min(...values); const max = Math.max(...values); const rng = max - min || 1
    const W = 60; const H = 24
    const pts = values.map((v, i) => {
        const x = ((i / (values.length - 1)) * W).toFixed(1)
        const y = (H - ((v - min) / rng) * H * 0.8 - H * 0.1).toFixed(1)
        return `${x},${y}`
    }).join(' ')
    return (
        <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} aria-hidden="true">
            <polyline points={pts} fill="none" stroke={up ? 'var(--color-green-accent)' : '#c8922a'} strokeWidth="1" opacity={up ? 0.65 : 0.5} />
        </svg>
    )
}

export default function MarketPricesPage({ lang = 'EN' }: { lang?: LangCode }) {
    const [crops, setCrops] = useState<MarketCrop[]>([])
    const [trendData, setTrendData] = useState<TrendData | null>(null)
    const [compareDistrict, setCompareDistrict] = useState('')
    const [loading, setLoading] = useState(true)

    const fetchData = async () => {
        setLoading(true)
        try {
            const resp = await client.get('/api/market/all-crops')
            setCrops(resp.data || [])
            // Fetch trend for first crop
            if (resp.data?.length > 0) {
                const trendResp = await client.get('/api/market/trend', { params: { crop: resp.data[0].crop, days: 30 } })
                setTrendData(trendResp.data)
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    useEffect(() => { fetchData() }, [])

    if (loading) return <div className="dp-header"><span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}… Loading</span></div>

    return (
        <div>
            <div className="dp-header">
                <span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}</span>
                <div className="dp-header__actions">
                    <span className="dp-meta-note">Last fetch — {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
                    <button className="dp-ghost-btn" id="market-refresh" onClick={fetchData}>{LABELS.refresh[lang] || LABELS.refresh.EN}</button>
                </div>
            </div>

            <div className="market-ticker-strip" role="region" aria-label="Price ticker">
                {crops.slice(0, 7).map(({ crop, mandi_price, delta_pct }) => {
                    const up = delta_pct >= 0
                    return (
                        <div key={crop} className="ticker-item">
                            <span className="ticker-item__crop">{crop}</span>
                            <span className="ticker-item__price">₹{mandi_price.toLocaleString()}</span>
                            <span className={`ticker-item__delta ticker-item__delta--${up ? 'up' : 'down'}`}>{up ? '+' : ''}{delta_pct}%</span>
                        </div>
                    )
                })}
            </div>

            <div className="market-full-header">
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', letterSpacing: '0.14em', textTransform: 'uppercase' as const, color: 'var(--color-text-light)' }}>Crop</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', letterSpacing: '0.14em', textTransform: 'uppercase' as const, color: 'var(--color-text-light)' }}>MSP</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', letterSpacing: '0.14em', textTransform: 'uppercase' as const, color: 'var(--color-text-light)' }}>Mandi</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', letterSpacing: '0.14em', textTransform: 'uppercase' as const, color: 'var(--color-text-light)' }}>Delta</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.48rem', letterSpacing: '0.14em', textTransform: 'uppercase' as const, color: 'var(--color-text-light)' }}>Trend</span>
            </div>
            <div className="market-full-table">
                {crops.map(({ crop, msp_inr, mandi_price, delta_pct }) => {
                    const up = delta_pct >= 0
                    // Generate synthetic sparkline from msp/mandi
                    const sVals = Array.from({ length: 14 }, (_, i) => msp_inr + (mandi_price - msp_inr) * (i / 13) + (Math.random() - 0.5) * msp_inr * 0.02)
                    return (
                        <div key={crop} className="market-full-row">
                            <span className="mft__crop">{crop}</span>
                            <span className="mft__num">₹{msp_inr.toLocaleString()}</span>
                            <span className="mft__num">₹{mandi_price.toLocaleString()}</span>
                            <span className={up ? 'mft__delta--up' : 'mft__delta--down'}>{up ? '+' : ''}{delta_pct}%</span>
                            <Sparkline14 values={sVals} up={up} />
                        </div>
                    )
                })}
            </div>

            <div className="district-compare">
                <span className="db-block__label">District Price Comparison</span>
                <div className="district-compare__input-row">
                    <div className="ob-field" style={{ maxWidth: '360px' }}>
                        <span className="ob-field__float-label">Compare District</span>
                        <input className="ob-field__input" type="text" placeholder="Type a district name…"
                            value={compareDistrict} onChange={e => setCompareDistrict(e.target.value)}
                            id="market-compare-district" aria-label="Compare district" />
                    </div>
                </div>
                {compareDistrict.length >= 3 && crops.length > 0 && (
                    <DistrictCompare crop={crops[0].crop} district={compareDistrict} />
                )}
            </div>
        </div>
    )
}

function DistrictCompare({ crop, district }: { crop: string; district: string }) {
    const [data, setData] = useState<{ msp_inr: number; mandi_price: number; delta_pct: number } | null>(null)
    useEffect(() => {
        client.get('/api/market/mandi-prices', { params: { crop, district } })
            .then(r => setData(r.data))
            .catch(() => { })
    }, [crop, district])
    if (!data) return null
    const ourPrice = data.mandi_price
    const theirPrice = Math.round(ourPrice * 0.98) // Simulated other district
    const diff = ourPrice - theirPrice
    return (
        <div className="district-compare__result">
            <div className="district-compare__col">
                <span className="district-compare__district-label">Your District</span>
                <span className="district-compare__price">₹{ourPrice.toLocaleString()}/qt</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--color-text-light)' }}>{crop} — Current Mandi</span>
            </div>
            <div>
                <div className={`district-compare__delta-center district-compare__delta-center--${diff >= 0 ? 'up' : 'down'}`}>{diff >= 0 ? '+' : ''}₹{diff}</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '8px', textAlign: 'center' as const, color: 'var(--color-text-light)' }}>Your premium</div>
            </div>
            <div className="district-compare__col" style={{ alignItems: 'flex-end' }}>
                <span className="district-compare__district-label">{district}</span>
                <span className="district-compare__price">₹{theirPrice.toLocaleString()}/qt</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--color-text-light)' }}>{crop} — Estimated</span>
            </div>
        </div>
    )
}
