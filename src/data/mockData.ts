/**
 * CropXpert — Centralized mock data.
 * All dashboard pages pull from here so the data is consistent.
 * When the backend is available, useApi hooks fetch real data;
 * when it's not, these mocks are used as-is.
 */

// ── Types ───────────────────────────────────────────────────

export interface SoilReading {
    key: string
    label: string
    value: number
    unit: string
    status: 'OPTIMAL' | 'LOW' | 'CRITICAL'
    statusClass: 'optimal' | 'low' | 'critical'
    low: number
    high: number
}

export interface MarketRow {
    crop: string
    category: 'CEREALS' | 'PULSES' | 'OILSEEDS' | 'VEGETABLES' | 'FRUITS'
    msp: string
    mspNum: number
    mandi: string
    mandiNum: number
    delta: string
    up: boolean
    high7: string
    low7: string
    spark7: number[]
    spark14: number[]
}

export interface CropCandidate {
    name: string
    conf: number
    delta: string
    up: boolean
}

export interface SchemeData {
    id: string
    tag: string
    eligible: 'yes' | 'check'
    nameKey: string
    name: string
    benefit: string
    eligibility: string[]
    docs: string[]
    url: string
}

export interface HistoricalReading {
    date: string
    n: number
    p: number
    k: number
    ph: number
    moist: number
    temp: number
    rec: string
}

// ── Farmer Profile ──────────────────────────────────────────

export const FARMER = {
    name: 'Anil Nagdiwala',
    initials: 'AN',
    farmName: 'Nagdiwala Farm',
    district: 'Pune',
    state: 'Maharashtra',
    acreage: 3.5,
}

// ── Soil Readings ───────────────────────────────────────────

export const SOIL_READINGS: SoilReading[] = [
    { key: 'N', label: 'Nitrogen', value: 90, unit: 'mg/kg', status: 'OPTIMAL', statusClass: 'optimal', low: 80, high: 120 },
    { key: 'P', label: 'Phosphorus', value: 38, unit: 'mg/kg', status: 'LOW', statusClass: 'low', low: 50, high: 80 },
    { key: 'K', label: 'Potassium', value: 51, unit: 'mg/kg', status: 'OPTIMAL', statusClass: 'optimal', low: 60, high: 100 },
    { key: 'pH', label: 'Acidity', value: 6.5, unit: 'pH', status: 'OPTIMAL', statusClass: 'optimal', low: 5.5, high: 7.5 },
    { key: 'H₂O', label: 'Moisture', value: 28, unit: '%', status: 'LOW', statusClass: 'low', low: 40, high: 70 },
]

export const FULL_PARAMS = [
    { key: 'N', label: 'N — Nitrogen', value: 90, unit: 'mg/kg', status: 'optimal' as const, icarMin: 80, icarMax: 120, action: 'Maintain current fertiliser schedule — readings are within the optimal ICAR range for rice.' },
    { key: 'P', label: 'P — Phosphorus', value: 38, unit: 'mg/kg', status: 'low' as const, icarMin: 40, icarMax: 80, action: 'Apply DAP at 50 kg per acre before the next irrigation cycle to restore phosphorus levels.' },
    { key: 'K', label: 'K — Potassium', value: 51, unit: 'mg/kg', status: 'optimal' as const, icarMin: 40, icarMax: 90, action: 'No action required this cycle. Re-test at mid-season for continued monitoring.' },
    { key: 'pH', label: 'pH — Acidity', value: 6.5, unit: 'pH', status: 'optimal' as const, icarMin: 6.0, icarMax: 7.0, action: 'Soil pH is ideal. Avoid lime application — current value does not require adjustment.' },
    { key: 'H₂O', label: 'Moisture', value: 28, unit: '%', status: 'low' as const, icarMin: 30, icarMax: 60, action: 'Irrigate within 48 hours. Moisture is below the lower ICAR threshold for Kharif crops.' },
    { key: 'Temp', label: 'Temperature', value: 28.4, unit: '°C', status: 'optimal' as const, icarMin: 22, icarMax: 32, action: 'Temperature is within the optimal germination range. No seasonal adjustments needed.' },
]

// ── Trend Data ──────────────────────────────────────────────

export const MONTHS_12 = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb']

export const NPK_SERIES = {
    N: [72, 68, 74, 78, 76, 80, 82, 79, 77, 83, 88, 90],
    P: [45, 48, 46, 50, 52, 49, 55, 54, 38, 38, 37, 38],
    K: [35, 38, 34, 40, 42, 39, 44, 46, 43, 45, 48, 51],
}

export const PH_SERIES = [6.2, 6.3, 6.4, 6.3, 6.5, 6.4, 6.5, 6.6, 6.5, 6.4, 6.5, 6.5]
export const MOISTURE_SERIES = [42, 38, 45, 50, 48, 52, 46, 44, 30, 28, 27, 28]

export const LINE_COLORS: Record<string, string> = {
    N: 'var(--color-green-dark)',
    P: 'var(--color-green-mid)',
    K: 'var(--color-green-accent)',
}

// ── Market Data ─────────────────────────────────────────────

export const MARKET_DATA: MarketRow[] = [
    { crop: 'Rice', category: 'CEREALS', msp: '₹2,183', mspNum: 2183, mandi: '₹2,210', mandiNum: 2210, delta: '+1.2%', up: true, high7: '₹2,240', low7: '₹2,188', spark7: [60, 65, 58, 70, 72, 68, 74], spark14: [2180, 2190, 2195, 2200, 2205, 2208, 2210, 2215, 2218, 2220, 2225, 2218, 2214, 2210] },
    { crop: 'Wheat', category: 'CEREALS', msp: '₹2,275', mspNum: 2275, mandi: '₹2,261', mandiNum: 2261, delta: '−0.6%', up: false, high7: '₹2,295', low7: '₹2,255', spark7: [80, 78, 75, 77, 74, 73, 72], spark14: [2295, 2288, 2282, 2278, 2274, 2270, 2268, 2265, 2263, 2261, 2259, 2258, 2260, 2261] },
    { crop: 'Soybean', category: 'OILSEEDS', msp: '₹4,600', mspNum: 4600, mandi: '₹4,728', mandiNum: 4728, delta: '+2.8%', up: true, high7: '₹4,750', low7: '₹4,620', spark7: [50, 55, 60, 58, 65, 70, 75], spark14: [4600, 4618, 4635, 4648, 4660, 4672, 4685, 4695, 4700, 4710, 4718, 4725, 4727, 4728] },
    { crop: 'Maize', category: 'CEREALS', msp: '₹2,090', mspNum: 2090, mandi: '₹1,910', mandiNum: 1910, delta: '+2.1%', up: true, high7: '₹1,930', low7: '₹1,875', spark7: [55, 58, 56, 60, 62, 59, 63], spark14: [1870, 1878, 1882, 1888, 1892, 1895, 1900, 1903, 1905, 1907, 1908, 1909, 1910, 1910] },
    { crop: 'Chickpea', category: 'PULSES', msp: '₹5,440', mspNum: 5440, mandi: '₹5,380', mandiNum: 5380, delta: '−1.1%', up: false, high7: '₹5,510', low7: '₹5,370', spark7: [75, 73, 71, 72, 70, 69, 68], spark14: [5510, 5498, 5490, 5479, 5468, 5458, 5449, 5441, 5433, 5425, 5418, 5410, 5405, 5380] },
    { crop: 'Tomato', category: 'VEGETABLES', msp: '—', mspNum: 0, mandi: '₹3,200', mandiNum: 3200, delta: '+5.2%', up: true, high7: '₹3,400', low7: '₹2,980', spark7: [40, 45, 50, 55, 60, 62, 65], spark14: [2980, 3010, 3040, 3070, 3090, 3110, 3130, 3150, 3165, 3175, 3185, 3192, 3198, 3200] },
    { crop: 'Onion', category: 'VEGETABLES', msp: '—', mspNum: 0, mandi: '₹1,850', mandiNum: 1850, delta: '−2.4%', up: false, high7: '₹2,100', low7: '₹1,820', spark7: [85, 80, 78, 75, 72, 70, 68], spark14: [2100, 2075, 2052, 2030, 2010, 1992, 1974, 1958, 1942, 1928, 1914, 1902, 1878, 1850] },
    { crop: 'Groundnut', category: 'OILSEEDS', msp: '₹5,850', mspNum: 5850, mandi: '₹5,920', mandiNum: 5920, delta: '+1.2%', up: true, high7: '₹5,960', low7: '₹5,840', spark7: [58, 60, 62, 61, 63, 64, 65], spark14: [5840, 5852, 5860, 5868, 5876, 5882, 5888, 5893, 5898, 5902, 5906, 5910, 5916, 5920] },
    { crop: 'Mango', category: 'FRUITS', msp: '—', mspNum: 0, mandi: '₹8,500', mandiNum: 8500, delta: '+3.1%', up: true, high7: '₹8,700', low7: '₹8,200', spark7: [50, 55, 58, 60, 63, 65, 68], spark14: [8200, 8240, 8280, 8310, 8340, 8370, 8395, 8415, 8430, 8445, 8458, 8468, 8480, 8500] },
    { crop: 'Lentil', category: 'PULSES', msp: '₹6,000', mspNum: 6000, mandi: '₹5,920', mandiNum: 5920, delta: '−1.3%', up: false, high7: '₹6,080', low7: '₹5,890', spark7: [72, 70, 68, 67, 66, 65, 64], spark14: [6080, 6065, 6050, 6038, 6026, 6015, 6005, 5995, 5986, 5975, 5964, 5952, 5940, 5920] },
]

// ── Crop Recommendations ────────────────────────────────────

export const ALL_CROPS: CropCandidate[] = [
    { name: 'Rice', conf: 97.3, delta: '+1.2%', up: true },
    { name: 'Maize', conf: 88.4, delta: '+0.8%', up: true },
    { name: 'Soybean', conf: 84.1, delta: '+2.1%', up: true },
    { name: 'Wheat', conf: 79.5, delta: '−0.6%', up: false },
    { name: 'Jowar', conf: 76.2, delta: '+0.3%', up: true },
    { name: 'Cotton', conf: 72.8, delta: '−1.2%', up: false },
    { name: 'Groundnut', conf: 68.4, delta: '+0.5%', up: true },
    { name: 'Sunflower', conf: 64.1, delta: '−0.4%', up: false },
    { name: 'Sugarcane', conf: 61.7, delta: '+1.8%', up: true },
    { name: 'Turmeric', conf: 58.3, delta: '+0.9%', up: true },
    { name: 'Chickpea', conf: 55.2, delta: '−0.2%', up: false },
    { name: 'Tomato', conf: 52.6, delta: '+2.4%', up: true },
    { name: 'Onion', conf: 49.1, delta: '−0.8%', up: false },
    { name: 'Potato', conf: 46.8, delta: '+0.6%', up: true },
    { name: 'Mung Bean', conf: 44.2, delta: '+1.1%', up: true },
    { name: 'Lentil', conf: 41.7, delta: '−0.3%', up: false },
    { name: 'Bajra', conf: 38.5, delta: '+0.7%', up: true },
    { name: 'Ragi', conf: 35.2, delta: '−0.5%', up: false },
    { name: 'Tur Dal', conf: 32.1, delta: '+1.3%', up: true },
    { name: 'Garlic', conf: 29.8, delta: '+0.4%', up: true },
    { name: 'Ginger', conf: 27.4, delta: '−0.9%', up: false },
    { name: 'Coriander', conf: 22.1, delta: '+0.2%', up: true },
]

export const WHY_REASONS = [
    'N-90 is within the optimal range of 80–100 mg/kg for rice cultivation.',
    'Current mandi price of ₹2,210/qt exceeds MSP by 1.2% — positive margin signal.',
    'Sowing window aligns with the regional Kharif season calendar for Maharashtra.',
]

export const FEATURE_COLS = [
    { label: 'MSP', value: '₹2,183/qt' },
    { label: 'Mandi Price', value: '₹2,210/qt' },
    { label: 'Delta', value: '+1.2%' },
    { label: 'Sowing Window', value: 'Jun 15 – Jul 10' },
    { label: 'Harvest Window', value: 'Oct 20 – Nov 10' },
    { label: 'Est. Yield', value: '5–6 t/ha' },
]

// ── Historical Readings ─────────────────────────────────────

export const HISTORY: HistoricalReading[] = [
    { date: '28 Feb 25', n: 90, p: 38, k: 51, ph: 6.5, moist: 28, temp: 28.4, rec: 'Rice' },
    { date: '14 Feb 25', n: 83, p: 42, k: 49, ph: 6.4, moist: 32, temp: 27.1, rec: 'Rice' },
    { date: '31 Jan 25', n: 77, p: 44, k: 46, ph: 6.5, moist: 35, temp: 26.8, rec: 'Maize' },
    { date: '17 Jan 25', n: 79, p: 52, k: 48, ph: 6.4, moist: 38, temp: 25.5, rec: 'Rice' },
    { date: '01 Jan 25', n: 82, p: 55, k: 44, ph: 6.5, moist: 41, temp: 24.2, rec: 'Rice' },
]

// ── Government Schemes ──────────────────────────────────────

export const SCHEMES: SchemeData[] = [
    {
        id: 'pmkisan', tag: 'Gov. Scheme', eligible: 'yes', nameKey: 'PM-KISAN',
        name: 'PM-KISAN Samman Nidhi', benefit: '₹6,000 / year',
        eligibility: ['Landholding below 2 hectares.', 'Registered in Aadhaar-linked farm records.', 'Not a government employee or income-tax payer.'],
        docs: ['Aadhaar Card', 'Land ownership records (7/12 Extract)', 'Bank account passbook'],
        url: 'pmkisan.gov.in',
    },
    {
        id: 'kcc', tag: 'Zero-Interest Loan', eligible: 'yes', nameKey: 'KCC',
        name: 'Kisan Credit Card (KCC)', benefit: '0% effective interest',
        eligibility: ['Any farmer with cultivable land.', 'Valid during the crop season — up to ₹3 lakh.', 'Prompt repayment attracts 2% additional subvention.'],
        docs: ['Identity proof', 'Land records', 'Two passport photographs', 'Bank KYC form'],
        url: 'nabard.org/kcc',
    },
    {
        id: 'pmfby', tag: 'Crop Insurance', eligible: 'yes', nameKey: 'PMFBY',
        name: 'PM Fasal Bima Yojana 2.0', benefit: 'Premium: 2% (Kharif)',
        eligibility: ['Farmer with notified crop in a notified area.', 'Loanee farmers auto-enrolled — opt-out available.', 'Non-loanee farmers must apply before cutoff date.'],
        docs: ['Sowing declaration', 'Bank account details', 'Land records', 'Aadhaar'],
        url: 'pmfby.gov.in',
    },
    {
        id: 'shc', tag: 'Subsidy', eligible: 'check', nameKey: 'SHC',
        name: 'Soil Health Card Scheme', benefit: 'Free soil testing',
        eligibility: ['All farmers with cultivable land are eligible.', 'Testing cycles every 2 years per plot.', 'Digital card issued within 30 days of sampling.'],
        docs: ['Aadhaar Card', 'Land survey number', 'Mobile number for digital card'],
        url: 'soilhealth.dac.gov.in',
    },
    {
        id: 'nabard', tag: 'Infrastructure Fund', eligible: 'check', nameKey: 'NABARD',
        name: 'NABARD Rural Infrastructure Dev Fund', benefit: 'Low-interest credit',
        eligibility: ['Farmer Producer Organizations (FPOs) and cooperatives.', 'State government-sponsored infrastructure projects.', 'Minimum project cost: ₹25 lakh.'],
        docs: ['Organization registration certificate', 'Project DPR', 'State sponsorship letter'],
        url: 'nabard.org/ridf',
    },
]

export const SCHEME_TRANSLATIONS: Record<string, Record<string, string>> = {
    'PM-KISAN': { HI: 'पीएम-किसान सम्मान निधि', MR: 'पीएम-किसान सन्मान निधी', TA: 'பிஎம்-கிசான் சம்மான் நிதி', TE: 'పీఎం-కిసాన్ సమ్మాన్ నిధి' },
    'KCC': { HI: 'किसान क्रेडिट कार्ड', MR: 'किसान क्रेडिट कार्ड', TA: 'கிசான் கிரெடிட் கார்டு', TE: 'కిసాన్ క్రెడిట్ కార్డ్' },
}

export const APPLY_LABELS: Record<string, string> = {
    EN: 'Apply via Government Portal',
    HI: 'सरकारी पोर्टल पर आवेदन करें',
    MR: 'सरकारी पोर्टलवर अर्ज करा',
    TA: 'அரசு போர்டலில் விண்ணப்பிக்கவும்',
    TE: 'ప్రభుత్వ పోర్టల్ ద్వారా దరఖాస్తు చేయండి',
}
