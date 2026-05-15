import { useEffect, useRef, useState } from 'react'
import './styles.css'

const TRANSLATIONS: Record<string, string> = {
    HI: 'वास्तविक मृदा बुद्धिमत्ता, सिद्ध फसल मार्गदर्शन, और लाइव बाजार मूल्य — भारतीय कृषि के लिए।',
    MR: 'वास्तविक माती बुद्धिमत्ता, सिद्ध पीक मार्गदर्शन, आणि थेट बाजारभाव — भारतीय शेतीसाठी.',
    TA: 'உண்மையான மண் நுண்ணறிவு, நிரூபிக்கப்பட்ட பயிர் வழிகாட்டுதல், மற்றும் நேரடி சந்தை விலைகள்.',
    TE: 'నిజమైన నేల తెలివి, నిరూపించబడిన పంట మార్గదర్శకత్వం, మరియు లైవ్ మార్కెట్ ధరలు.',
}

interface Props {
    activeLang: string
}

export default function LanguageBanner({ activeLang }: Props) {
    const [visible, setVisible] = useState(false)
    const [text, setText] = useState('')
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    useEffect(() => {
        if (activeLang === 'EN') {
            setVisible(false)
            return
        }

        const translation = TRANSLATIONS[activeLang]
        if (!translation) return

        setText(translation)
        setVisible(true)

        // Auto-dismiss after 4 seconds
        if (timerRef.current) clearTimeout(timerRef.current)
        timerRef.current = setTimeout(() => setVisible(false), 4000)

        return () => {
            if (timerRef.current) clearTimeout(timerRef.current)
        }
    }, [activeLang])

    // Dismiss on scroll
    useEffect(() => {
        const onScroll = () => setVisible(false)
        window.addEventListener('scroll', onScroll, { passive: true, once: true })
        return () => window.removeEventListener('scroll', onScroll)
    }, [visible])

    return (
        <div className={`lang-banner ${visible ? 'lang-banner--visible' : ''}`} role="status" aria-live="polite">
            <p className="lang-banner__text">{text}</p>
        </div>
    )
}
