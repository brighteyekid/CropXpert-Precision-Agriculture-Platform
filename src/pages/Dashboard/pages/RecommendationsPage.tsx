import { useState, useEffect } from 'react'
import client from '../../../api/client'
import type { LangCode } from '../../../components/LanguageSwitcher/index'

interface CropResult {
    rank: number; crop: string; ml_confidence: number
    msp_inr_per_quintal: number | null; mandi_price: number | null
    mandi_trend: string | null; final_score: number
    sowing_tip: string; sowing_months: string[]
    fertilizer_dose: { urea: string; dap: string }
    gemini_rationale?: string
}

interface PredictResponse {
    top3: CropResult[]
    feature_importances: Record<string, number>
    reading_id: number | null
    timestamp: string
}

const LABELS: Record<string, Record<string, string>> = {
    header: { EN: 'Crop Recommendations — Based on Current Soil', HI: 'फसल सिफारिशें — वर्तमान मिट्टी के आधार पर', MR: 'पीक शिफारसी — सध्याच्या मातीवर आधारित', TA: 'பயிர் பரிந்துரைகள் — தற்போதைய மண் அடிப்படையில்', TE: 'పంట సిఫార్సులు — ప్రస్తుత నేల ఆధారంగా' },
    refresh: { EN: 'Refresh Analysis', HI: 'विश्लेषण रिफ्रेश करें', MR: 'विश्लेषण रिफ्रेश करा', TA: 'பகுப்பாய்வைப் புதுப்பிக்கவும்', TE: 'విశ్లేషణ రిఫ్రెష్ చేయండి' },
    why: { EN: 'Why this crop?', HI: 'यह फसल क्यों?', MR: 'ही पीक का?', TA: 'ஏன் இந்த பயிர்?', TE: 'ఈ పంట ఎందుకు?' },
}

interface InitialRec {
    crop: string
    confidence: number
    msp: number
    timestamp: string
}

export default function RecommendationsPage({ lang = 'EN', initialRec }: { lang?: LangCode; initialRec?: InitialRec | null }) {
    const [prediction, setPrediction] = useState<PredictResponse | null>(null)
    const [allCrops, setAllCrops] = useState<CropResult[]>([])
    const [compared, setCompared] = useState<CropResult[]>([])
    const [loading, setLoading] = useState(true)
    const [noData, setNoData] = useState(false)

    const fetchPrediction = async () => {
        setLoading(true)
        setNoData(false)
        try {
            const latestResp = await client.get('/api/sensors/latest').catch((e) => {
                if (e?.response?.status === 404) { setNoData(true); return null }
                return null
            })
            if (latestResp?.data) {
                const predResp = await client.post('/api/predict', { reading_id: latestResp.data.id })
                setPrediction(predResp.data)
                setAllCrops(predResp.data.top3 || [])
            } else if (!latestResp) {
                setNoData(true)
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    // On mount: if we have an initialRec from the dashboard, show it instantly
    // without running a new prediction (so overview and recs show the SAME crop)
    useEffect(() => {
        if (initialRec) {
            // Synthesise a minimal PredictResponse from the cached rec so the UI renders
            const synth: PredictResponse = {
                top3: [{
                    rank: 1, crop: initialRec.crop,
                    ml_confidence: initialRec.confidence,
                    msp_inr_per_quintal: initialRec.msp,
                    mandi_price: Math.round(initialRec.msp * 1.01),
                    mandi_trend: `+1.0% above MSP`,
                    final_score: initialRec.confidence,
                    sowing_tip: 'Click "Refresh Analysis" to load full sowing and fertilizer details.',
                    sowing_months: [],
                    fertilizer_dose: { urea: '—', dap: '—' },
                }],
                feature_importances: {},
                reading_id: null,
                timestamp: initialRec.timestamp,
            }
            setPrediction(synth)
            setAllCrops(synth.top3)
            setLoading(false)
        } else {
            // No cached rec — run fresh prediction
            fetchPrediction()
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])


    const addCompare = (crop: CropResult) => {
        setCompared(prev => {
            if (prev.find(c => c.crop === crop.crop)) return prev
            if (prev.length >= 3) return prev
            return [...prev, crop]
        })
    }

    const top = prediction?.top3?.[0]
    const maxConf = allCrops.length > 0 ? allCrops[0].ml_confidence : 1

    const featureCols = top ? [
        { label: 'MSP', value: top.msp_inr_per_quintal ? `₹${top.msp_inr_per_quintal.toLocaleString()}/qt` : '—' },
        { label: 'Mandi Price', value: top.mandi_price ? `₹${top.mandi_price.toLocaleString()}/qt` : '—' },
        { label: 'Trend', value: top.mandi_trend || '—' },
        { label: 'Sowing Window', value: top.sowing_months.join(' – ') || '—' },
        { label: 'Final Score', value: `${(top.final_score * 100).toFixed(1)}%` },
        { label: 'Fertilizer', value: `${top.fertilizer_dose.urea}, ${top.fertilizer_dose.dap}` },
    ] : []

    // Feature importance reasons
    const importances = prediction?.feature_importances || {}
    const sortedFeatures = Object.entries(importances).sort((a, b) => b[1] - a[1]).slice(0, 3)
    const reasons = sortedFeatures.map(([feat, imp]) => `${feat} (importance: ${(imp * 100).toFixed(1)}%) is a key driver for this recommendation.`)

    if (loading) return <div className="dp-header"><span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}… Loading</span></div>

    if (noData || (!prediction && allCrops.length === 0)) {
        return (
            <div>
                <div className="dp-header">
                    <span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}</span>
                </div>
                <div style={{ padding: '40px 0', display: 'flex', flexDirection: 'column', gap: 12 }}>
                    <span className="db-block__label" style={{ marginBottom: 0 }}>No Soil Data Yet</span>
                    <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.875rem', fontWeight: 300, color: 'var(--color-text-body)', lineHeight: 1.7, maxWidth: '52ch' }}>
                        Complete onboarding and enter your soil readings to get your first AI-powered crop recommendation.
                    </p>
                    <a href="/onboarding" style={{
                        display: 'inline-block', marginTop: 16,
                        fontFamily: 'var(--font-mono)', fontSize: '0.52rem', fontWeight: 400,
                        letterSpacing: '0.14em', textTransform: 'uppercase' as const,
                        color: '#f0ede4', background: 'var(--color-green-dark)',
                        padding: '14px 28px', textDecoration: 'none', alignSelf: 'flex-start',
                    }}>Go to Onboarding</a>
                </div>
            </div>
        )
    }

    return (
        <div style={{ paddingBottom: compared.length > 0 ? '48px' : '0' }}>
            <div className="dp-header">
                <span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}</span>
                <div className="dp-header__actions">
                    <button className="dp-ghost-btn" id="rec-refresh" onClick={fetchPrediction}>{LABELS.refresh[lang] || LABELS.refresh.EN}</button>
                    <span className="dp-meta-note">{prediction?.timestamp ? `Last analysed — ${new Date(prediction.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}` : ''}</span>
                </div>
            </div>

            {top && (
                <>
                    <div style={{ marginBottom: 4 }}>
                        <div className="db-rec__headline-row">
                            <h2 className="db-rec__crop">{top.crop}</h2>
                            <span className="db-rec__confidence">{(top.ml_confidence * 100).toFixed(1)}%</span>
                        </div>
                    </div>

                    <div className="rec-feature-band">
                        {featureCols.map(({ label, value }) => (
                            <div key={label} className="rec-feature-col">
                                <span className="rec-feature-col__label">{label}</span>
                                <span className="rec-feature-col__value">{value}</span>
                            </div>
                        ))}
                    </div>

                    <div className="why-block">
                        <span className="db-block__label" style={{ marginBottom: 8 }}>{LABELS.why[lang] || LABELS.why.EN}</span>
                        {top.gemini_rationale && (
                            <div className="why-block__row">
                                <span className="why-block__diamond" style={{ background: 'var(--color-green-accent)' }} aria-hidden="true" />
                                <p className="why-block__text" style={{ fontStyle: 'italic' }}>
                                    <strong style={{ color: 'var(--color-green-accent)', marginRight: 4 }}>AI Agronomist:</strong>
                                    {top.gemini_rationale}
                                </p>
                            </div>
                        )}
                    </div>
                </>
            )}

            <span className="db-block__label">Top {allCrops.length} Crop Candidates — Ranked by ML Score</span>
            <div className="rec-list">
                {allCrops.map((crop, i) => (
                    <div key={crop.crop} className="rec-list__item">
                        <span className="rec-list__rank">{String(i + 1) .padStart(2, '0')}</span>
                        <div className="rec-list__name-block">
                            <span className="rec-list__name">{crop.crop}</span>
                            <span className="rec-list__conf">{(crop.ml_confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div className="rec-list__bar-track">
                            <div className="rec-list__bar-fill" style={{ width: `${(crop.ml_confidence / maxConf) * 100}%` }} />
                        </div>
                        <span className={`rec-list__delta rec-list__delta--${crop.mandi_trend?.startsWith('+') ? 'up' : 'down'}`}>{crop.mandi_trend || '—'}</span>
                        <button className="rec-list__detail-btn" onClick={() => addCompare(crop)} id={`rec-detail-${crop.crop.toLowerCase()}`}>Details</button>
                    </div>
                ))}
            </div>

            {compared.length > 0 && (
                <div className="rec-compare-strip" role="region" aria-label="Crop comparison">
                    {compared.map((crop, i) => (
                        <div key={crop.crop} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            {i > 0 && <span className="rec-compare-strip__sep" aria-hidden="true" />}
                            <div className="rec-compare-strip__item">
                                <span className="rec-compare-strip__name">{crop.crop}</span>
                                <span className="rec-compare-strip__conf">{(crop.ml_confidence * 100).toFixed(1)}%</span>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '8px', color: 'rgba(240,237,228,0.5)' }}>Score: {(crop.final_score * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    ))}
                    <button style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'rgba(240,237,228,0.4)', fontSize: '0.65rem', cursor: 'pointer' }} onClick={() => setCompared([])} aria-label="Clear comparison">Clear</button>
                </div>
            )}
        </div>
    )
}
