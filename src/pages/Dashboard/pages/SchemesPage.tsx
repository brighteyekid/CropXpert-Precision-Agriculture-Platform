import { useState, useEffect } from 'react'
import client from '../../../api/client'
import type { LangCode } from '../../../components/LanguageSwitcher/index'

interface Scheme {
    id: number; name: string; description: string | null
    benefit_amount: string | null; eligibility: string | null
    documents_required: string | null; apply_url: string | null
    scheme_type: string | null; last_updated: string | null
    is_eligible: boolean; max_acreage_ha: number | null
}

interface Loan {
    id: number; name: string; provider: string
    interest_rate: number; max_amount: number
    tenure_months_max: number; eligibility: string
    apply_url: string
}

const LABELS: Record<string, Record<string, string>> = {
    header: { EN: 'Schemes and Loans — Your Eligibility', HI: 'योजनाएँ और ऋण — आपकी पात्रता', MR: 'योजना आणि कर्ज — तुमची पात्रता', TA: 'திட்டங்கள் மற்றும் கடன்கள் — உங்கள் தகுதி', TE: 'పథకాలు మరియు రుణాలు — మీ అర్హత' },
    apply: { EN: 'Apply via Government Portal', HI: 'सरकारी पोर्टल पर आवेदन करें', MR: 'सरकारी पोर्टलवर अर्ज करा', TA: 'அரசு போர்டலில் விண்ணப்பிக்கவும்', TE: 'ప్రభుత్వ పోర్టల్ ద్వారా దరఖాస్తు చేయండి' },
    loanCalc: { EN: 'Loan Estimate', HI: 'ऋण अनुमान', MR: 'कर्ज अंदाज', TA: 'கடன் மதிப்பீடு', TE: 'రుణ అంచనా' },
    loanAmt: { EN: 'Loan Amount', HI: 'ऋण राशि', MR: 'कर्ज रक्कम', TA: 'கடன் தொகை', TE: 'రుణ మొత్తం' },
    monthlyEMI: { EN: 'Monthly Installment', HI: 'मासिक किस्त', MR: 'मासिक हप्ता', TA: 'மாதாந்திர தவணை', TE: 'నెలవారీ వాయిదా' },
    totalRepay: { EN: 'Total Repayment', HI: 'कुल चुकौती', MR: 'एकूण परतफेड', TA: 'மொத்த திருப்பி செலுத்தல்', TE: 'మొత్తం తిరిగి చెల్లింపు' },
    eligibility: { EN: 'Eligibility', HI: 'पात्रता', MR: 'पात्रता', TA: 'தகுதி', TE: 'అర్హత' },
    documents: { EN: 'Required Documents', HI: 'आवश्यक दस्तावेज', MR: 'आवश्यक कागदपत्रे', TA: 'தேவையான ஆவணங்கள்', TE: 'అవసరమైన పత్రాలు' },
}

export default function SchemesPage({ lang = 'EN' }: { lang?: LangCode }) {
    const [schemes, setSchemes] = useState<Scheme[]>([])
    const [loans, setLoans] = useState<Loan[]>([])
    const [loading, setLoading] = useState(true)
    const [loanAmt, setLoanAmt] = useState(150000)
    const [emiResult, setEmiResult] = useState<{ monthly_emi: number; total_payment: number; total_interest: number } | null>(null)

    useEffect(() => {
        async function fetch() {
            setLoading(true)
            try {
                const [sResp, lResp] = await Promise.all([
                    client.get('/api/schemes').catch(() => null),
                    client.get('/api/schemes/loans').catch(() => null),
                ])
                if (sResp?.data) setSchemes(sResp.data)
                if (lResp?.data) setLoans(lResp.data)
            } catch (e) { console.error(e) }
            finally { setLoading(false) }
        }
        fetch()
    }, [])

    useEffect(() => {
        const debounce = setTimeout(async () => {
            try {
                const resp = await client.post('/api/schemes/emi-calculate', {
                    principal: loanAmt,
                    rate: 0,
                    tenure_months: 12,
                })
                setEmiResult(resp.data)
            } catch { /* ignore */ }
        }, 300)
        return () => clearTimeout(debounce)
    }, [loanAmt])

    const fmt = (n: number) => n >= 100000 ? `₹${(n / 100000).toFixed(1)} L` : `₹${(n / 1000).toFixed(0)}K`
    const welfareSchemes = schemes.filter(s => s.scheme_type === 'welfare' || !s.scheme_type)
    const loanSchemes = schemes.filter(s => s.scheme_type === 'loan')
    const allSchemes = [...welfareSchemes, ...loanSchemes]

    if (loading) return <div className="dp-header"><span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}… Loading</span></div>

    return (
        <div>
            <div className="dp-header">
                <span className="dp-header__label">{LABELS.header[lang] || LABELS.header.EN}</span>
                <span className="dp-meta-note">{LABELS.eligibility[lang] || LABELS.eligibility.EN} — {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
            </div>

            <div className="schemes-eligibility-band">
                <p>You qualify for <strong>{schemes.filter(s => s.is_eligible && s.scheme_type !== 'loan').length}</strong> welfare schemes and <strong>{loans.length}</strong> loan programs. {schemes.filter(s => !s.is_eligible).length > 0 && <span style={{ color: 'var(--color-warn)' }}>{schemes.filter(s => !s.is_eligible).length} scheme{schemes.filter(s => !s.is_eligible).length > 1 ? 's' : ''} ineligible based on your registered landholding.</span>}</p>
            </div>

            {allSchemes.map((scheme) => {
                const eligList = scheme.eligibility?.split(';').map(s => s.trim()).filter(Boolean) || []
                const docList = scheme.documents_required?.split(';').map(s => s.trim()).filter(Boolean) || []


                return (
                    <div key={scheme.id} className="scheme-detail-card" id={`scheme-${scheme.id}`}>
                        <div className="sdc-row-1">
                            <span className="sdc-tag">{scheme.scheme_type === 'loan' ? 'Loan' : 'Gov. Scheme'}{scheme.max_acreage_ha ? ` · Max ${scheme.max_acreage_ha} ha` : ''}</span>
                            <span className={`sdc-eligible sdc-eligible--${scheme.scheme_type === 'loan' ? 'check' : scheme.is_eligible ? 'yes' : 'no'}`}>
                                {scheme.scheme_type === 'loan' ? 'CHECK REQUIRED' : scheme.is_eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
                            </span>
                        </div>
                        <div className="sdc-row-2">
                            <span className="sdc-name">{scheme.name}</span>
                            <span className="sdc-benefit">{scheme.benefit_amount || '—'}</span>
                        </div>
                        {scheme.description && (
                            <p style={{ fontFamily: 'var(--font-body)', fontSize: '0.8rem', fontWeight: 300, color: 'var(--color-text-body)', lineHeight: 1.6, margin: '8px 0 12px' }}>
                                {scheme.description}
                            </p>
                        )}
                        <div className="sdc-row-3">
                            <div>
                                <span className="sdc-col-label">{LABELS.eligibility[lang] || LABELS.eligibility.EN}</span>
                                <div className="sdc-bullet-list">
                                    {eligList.map((item, i) => (
                                        <div key={i} className="sdc-bullet"><span className="sdc-diamond" aria-hidden="true" /><span>{item}</span></div>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <span className="sdc-col-label">{LABELS.documents[lang] || LABELS.documents.EN}</span>
                                <div className="sdc-bullet-list">
                                    {docList.map((doc, i) => (
                                        <div key={i} className="sdc-bullet"><span className="sdc-diamond" aria-hidden="true" /><span>{doc}</span></div>
                                    ))}
                                </div>
                            </div>
                        </div>
                        {scheme.apply_url && (
                            <>
                                <a href={scheme.apply_url.startsWith('http') ? scheme.apply_url : `https://${scheme.apply_url}`}
                                    target="_blank" rel="noopener noreferrer" className="sdc-apply-btn" id={`scheme-apply-${scheme.id}`}>
                                    {LABELS.apply[lang] || LABELS.apply.EN}
                                </a>
                                <span className="sdc-portal-url">{scheme.apply_url}</span>
                            </>
                        )}
                    </div>
                )
            })}

            <div className="loan-calc">
                <span className="loan-calc__label">{LABELS.loanCalc[lang] || LABELS.loanCalc.EN} — Kisan Credit Card</span>
                <div className="loan-calc__slider-row">
                    <label className="loan-calc__slider-label" htmlFor="loan-slider">{LABELS.loanAmt[lang] || LABELS.loanAmt.EN} — {fmt(loanAmt)} of ₹3L maximum</label>
                    <input id="loan-slider" className="loan-slider" type="range" min={10000} max={300000} step={5000}
                        value={loanAmt} onChange={e => setLoanAmt(Number(e.target.value))} aria-label="Loan amount" />
                </div>
                <div className="loan-calc__figures">
                    <div className="loan-calc__figure">
                        <span className="loan-calc__figure-label">{LABELS.loanAmt[lang] || LABELS.loanAmt.EN}</span>
                        <span className="loan-calc__figure-value">{fmt(emiResult?.total_payment ?? loanAmt)}</span>
                    </div>
                    <div className="loan-calc__figure">
                        <span className="loan-calc__figure-label">{LABELS.monthlyEMI[lang] || LABELS.monthlyEMI.EN}</span>
                        <span className="loan-calc__figure-value">{fmt(emiResult?.monthly_emi ?? Math.round(loanAmt / 12))}</span>
                    </div>
                    <div className="loan-calc__figure">
                        <span className="loan-calc__figure-label">{LABELS.totalRepay[lang] || LABELS.totalRepay.EN}</span>
                        <span className="loan-calc__figure-value">{fmt(emiResult?.total_payment ?? loanAmt)}</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
