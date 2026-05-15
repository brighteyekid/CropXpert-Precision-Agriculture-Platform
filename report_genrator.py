from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PAGE_W, PAGE_H = letter
MARGIN_TB = 1.0 * inch
MARGIN_LR = 0.75 * inch

doc = SimpleDocTemplate(
    "./MREM_IEEE_Paper_Verified.pdf",
    pagesize=letter,
    leftMargin=MARGIN_LR,
    rightMargin=MARGIN_LR,
    topMargin=MARGIN_TB,
    bottomMargin=MARGIN_TB,
    title="MREM: Multi-Radio Exposure Mapper — IEEE Format",
    author="Chandra Pratap Singh Bhayal, Hirav K., Pratik Roy,Shubham Dube",
    subject="Cross-Protocol IoT Reconnaissance",
)

IEEE_BLUE = colors.HexColor("#003087")
LINK_COLOR = colors.HexColor("#0645AD")
GRAY_LINE = colors.HexColor("#AAAAAA")
BLACK = colors.black
WHITE = colors.white
LIGHT_BLUE = colors.HexColor("#EEF2FF")
GREEN_CELL = colors.HexColor("#D4EDDA")

base = getSampleStyleSheet()


def S(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=base[parent], **kw)


sty = {
    "PaperTitle": S(
        "PaperTitle",
        "Title",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=IEEE_BLUE,
        spaceAfter=4,
    ),
    "SubTitle": S(
        "SubTitle",
        fontName="Helvetica-Oblique",
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        textColor=IEEE_BLUE,
        spaceAfter=6,
    ),
    "AuthorBlock": S(
        "AuthorBlock",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        spaceAfter=6,
    ),
    "SectionHead": S(
        "SectionHead",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=WHITE,
        spaceBefore=8,
        spaceAfter=4,
        alignment=TA_CENTER,
        backColor=IEEE_BLUE,
        leftIndent=-6,
        rightIndent=-6,
        borderPad=4,
    ),
    "SubHead": S(
        "SubHead",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=IEEE_BLUE,
        spaceBefore=6,
        spaceAfter=2,
    ),
    "SubSubHead": S(
        "SubSubHead",
        fontName="Helvetica-BoldOblique",
        fontSize=9,
        leading=12,
        textColor=IEEE_BLUE,
        spaceBefore=4,
        spaceAfter=1,
    ),
    "Body": S(
        "Body",
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    ),
    "AbstractBody": S(
        "AbstractBody",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11.5,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
        leftIndent=12,
        rightIndent=12,
    ),
    "Keywords": S(
        "Keywords",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leftIndent=12,
        rightIndent=12,
    ),
    "Link": S(
        "Link",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=LINK_COLOR,
        alignment=TA_LEFT,
        leftIndent=14,
        spaceAfter=4,
    ),
    "Ref": S(
        "Ref",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
        leftIndent=18,
        firstLineIndent=-18,
    ),
    "TH": S(
        "TH",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=WHITE,
    ),
    "TD": S("TD", fontName="Helvetica", fontSize=8, leading=10, alignment=TA_CENTER),
    "Caption": S(
        "Caption",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        spaceAfter=4,
    ),
}


def heading(text, level=1):
    if level == 1:
        return Paragraph(text, sty["SectionHead"])
    if level == 2:
        return Paragraph(text, sty["SubHead"])
    return Paragraph(text, sty["SubSubHead"])


def body(text):
    return Paragraph(text, sty["Body"])


def lnk(display, url):
    return Paragraph(
        f'<font color="#0645AD"><u><a href="{url}">{display}</a></u></font>',
        sty["Link"],
    )


def SP(n=4):
    return Spacer(1, n)


def hr():
    return HRFlowable(
        width="100%", thickness=0.5, color=GRAY_LINE, spaceAfter=4, spaceBefore=4
    )


def ref_entry(num, text, url):
    return Paragraph(
        f"[{num}] {text} "
        f'<font color="#0645AD"><u><a href="{url}">[Online Link]</a></u></font>',
        sty["Ref"],
    )


# ─── Story ────────────────────────────────────────────────────────────────────
story = []

# Title
story += [
    Paragraph("MREM: Multi-Radio Exposure Mapper", sty["PaperTitle"]),
    Paragraph(
        "A Cross-Protocol IoT Reconnaissance &amp; Intelligence Platform",
        sty["SubTitle"],
    ),
    SP(4),
    Paragraph(
        "<b>Chandra Pratap Singh Bhayal</b> &nbsp;|&nbsp; <b>Hirav K.</b> &nbsp;|&nbsp; <b>Pratik Roy</b>",
        sty["AuthorBlock"],
    ),
    Paragraph("Team: 802.11 &nbsp;|&nbsp; February 2026", sty["AuthorBlock"]),
    hr(),
]

# Abstract
story += [
    heading("I.  ABSTRACT"),
    Paragraph(
        "<b>Abstract</b> — Traditional IoT security tools often operate in protocol isolation, "
        "failing to account for cross-layer vulnerabilities present in multi-radio gateways. "
        "This paper introduces the <b>Multi-Radio Exposure Mapper (MREM)</b>, a hardware-accelerated "
        "intelligence platform for Red Team reconnaissance. Utilising an ESP32-S3, BW16 (RTL8720DN), "
        "and NRF24L01+ tri-radio stack, MREM correlates signals across 2.4 GHz/5 GHz Wi-Fi, "
        "Bluetooth Low Energy (BLE), and proprietary RF to identify hidden attack surfaces, "
        "provisioning windows, and device-to-gateway relationships. A <i>Unified Exposure Index</i> "
        "provides real-time vulnerability scoring (1–10) for physical environments through "
        "cross-protocol correlation, reducing device discovery time by up to 70% in high-density "
        "environments. At under $100 total cost and 10+ hours battery life, MREM moves Red Team "
        "operations from active exploitation to strategic intelligence.",
        sty["AbstractBody"],
    ),
    Paragraph(
        "<b>Keywords</b> — IoT Security, RF Fingerprinting, Cross-Protocol Correlation, "
        "BLE Vulnerabilities, Wireless Reconnaissance, Red Team, Exposure Index, Multi-Radio Gateway",
        sty["Keywords"],
    ),
    hr(),
]

# Introduction
story += [
    heading("II.  INTRODUCTION"),
    body(
        "The proliferation of IoT devices has introduced a vast heterogeneous wireless attack surface. "
        "Modern smart-home hubs, industrial gateways, and enterprise access points simultaneously "
        "operate across 2.4 GHz/5 GHz Wi-Fi, Bluetooth Low Energy (BLE), Zigbee, and proprietary RF "
        "channels. Despite this multi-radio reality, Red Team practitioners continue to rely on "
        "single-protocol tools — Flipper Zero, HackRF One, Wi-Fi Pineapple — that analyse each "
        "protocol in isolation, leaving critical cross-layer vulnerabilities undetected."
    ),
    body(
        "MREM addresses this fundamental gap by providing a unified reconnaissance platform that "
        "simultaneously captures and correlates traffic across all major IoT radio protocols, "
        "surfacing attack surfaces that no single-protocol scanner can reveal."
    ),
]

# Problem Statement
story += [
    heading("III.  PROBLEM STATEMENT"),
    body(
        "Red team practitioners currently use fragmented tooling that provides no unified situational "
        "awareness. Three classes of vulnerability are systematically missed:"
    ),
    body(
        "<b>1) Protocol Isolation:</b> Tools such as Flipper Zero and HackRF analyse individual "
        "protocols sequentially, missing simultaneous cross-protocol events."
    ),
    body(
        "<b>2) Transition-State Vulnerabilities:</b> Critical weaknesses emerge when devices fail "
        "over between protocols — e.g., a smart camera falling from WPA3 Wi-Fi to an unencrypted "
        "BLE heartbeat channel under congestion."
    ),
    body(
        "<b>3) No Situational Awareness:</b> Fragmented tooling provides no unified view of the "
        "attack surface across multiple radio technologies, preventing correlation of "
        "device-to-gateway relationships."
    ),
    body(
        "MREM solves this by providing a <i>Unified Exposure Index</i> that maps the invisible "
        "relationships between disparate radio signals and assigns a real-time risk score (1–10)."
    ),
]

# Literature Survey
story += [heading("IV.  LITERATURE SURVEY")]

# A. RF Fingerprinting
story += [
    heading("A.  RF Fingerprinting and Physical-Layer Device Authentication", 2),
    body(
        "RF fingerprinting exploits hardware-level imperfections in radio transmitters to identify "
        "specific devices independent of MAC addresses — a property of particular value when "
        "addresses are randomised or spoofed."
    ),
    SP(2),
    heading("1)  Transient Energy Spectrum Method [1]", 3),
    body(
        "Köse, Taşcıoğlu, and Telatar propose a low-complexity RF fingerprinting method based on "
        "the energy spectrum of transmitter turn-on transient signals. Unique spectral fingerprints "
        "are extracted from the power-up transient to classify wireless IoT devices without relying "
        "on sustained communication. The approach is evaluated on IEEE 802.11b hardware and forms "
        "the foundational methodology for MREM's hardware identification pipeline."
    ),
    lnk(
        '→ [1] IEEE Access 2019 — Köse et al., "RF Fingerprinting of IoT Devices Based on Transient Energy Spectrum"',
        "https://ieeexplore.ieee.org/document/8631016",
    ),
    SP(2),
    heading("2)  Deep Learning for RF Fingerprinting — Large-Scale Study [2]", 3),
    body(
        "Jian et al. present a comprehensive experimental study using CNN architectures on 400 GB "
        "of IQ signal data from 10,000 radios. The deep convolutional models operate directly on raw "
        "and processed IQ samples to identify devices under changing channels, noise levels, and "
        "training-set sizes, demonstrating scalability to very large device populations. This work "
        "validates the feasibility of deep learning-based RFF for operational IoT environments."
    ),
    lnk(
        '→ [2] IEEE Open Journal of the Communications Society 2020 — Jian et al., "Deep Learning for RF Fingerprinting: A Massive Experimental Study"',
        "https://ieeexplore.ieee.org/document/9063411",
    ),
    SP(2),
    heading("3)  Intrusion Detection for IoT Devices via RF Fingerprinting [3]", 3),
    body(
        "This IEEE 2019 conference paper proposes a novel intrusion detection method to identify "
        "unauthorized IoT devices using deep learning on RF fingerprinting features. "
        "Physical-layer features are device-specific and significantly harder to impersonate than "
        "MAC addresses, providing a strong authentication primitive against sophisticated adversaries."
    ),
    lnk(
        '→ [3] IEEE Xplore 2019 — "Intrusion Detection for IoT Devices based on RF Fingerprinting using Deep Learning"',
        "https://ieeexplore.ieee.org/abstract/document/8795319",
    ),
    SP(2),
    heading("4)  Edge AI for RFF Deployment on Resource-Constrained Devices [4]", 3),
    body(
        "Al-Shawabka et al. (Dec 2024, arXiv) present a methodology for deploying RF fingerprinting "
        "on edge devices using TensorFlow Lite. CNN TFLite and Transformer TFLite models achieve "
        "accuracy rates of 0.99 and 0.98 respectively, with model sizes of only 462 KB and 210 KB — "
        "validating on-device inference at the scale of the ESP32-S3 used in MREM."
    ),
    lnk(
        '→ [4] arXiv Dec 2024 — Al-Shawabka et al., "Edge AI-based Radio Frequency Fingerprinting for IoT Networks"',
        "https://arxiv.org/abs/2412.10553",
    ),
    body(
        "<b>MREM Application:</b> Hardware fingerprinting for device identification independent of "
        "MAC addresses, implemented via the ESP32-S3 promiscuous-mode capture pipeline."
    ),
]

# B. BLE & Provisioning
story += [
    SP(4),
    heading("B.  BLE and Provisioning Security", 2),
    SP(2),
    heading("1)  BLE Security Comprehensive Survey [5]", 3),
    body(
        "Hossain and Hossain present a comprehensive taxonomy of security and privacy vulnerabilities "
        "in Bluetooth Low Energy for IoT and wearable devices (IEEE Open Journal of the "
        "Communications Society, 2022). The survey covers MITM attacks, passive eavesdropping, "
        "MAC spoofing, and replay attacks. The Just Works pairing mode — widely used in commodity "
        "IoT — provides no MITM protection, leaving a large fraction of deployed devices vulnerable."
    ),
    lnk(
        '→ [5] IEEE OJCOMS 2022 — Hossain & Hossain, "Security and Privacy Threats for BLE in IoT and Wearable Devices"',
        "https://ieeexplore.ieee.org/document/9706334",
    ),
    SP(2),
    heading("2)  Wi-Fi Provisioning Security [6]", 3),
    body(
        "Argenox Technical Library (2025) documents that the WPS push-button method creates a "
        "deterministic, time-bounded provisioning window exploitable by nearby adversaries. "
        "WPA2 in access-point mode is additionally vulnerable to dictionary attacks when short "
        "default passwords are used during device onboarding — a pervasive issue in consumer IoT."
    ),
    lnk(
        "→ [6] Argenox Technical Library 2025 — BLE Advertising Primer and Provisioning Security",
        "https://www.argenox.com/library/bluetooth-low-energy/ble-advertising-primer/",
    ),
    SP(2),
    heading("3)  Automatic BLE Device Fingerprinting via Static UUIDs [7a]", 3),
    body(
        "Zuo, Wen, Lin, and Zhang (ACM CCS 2019) reveal a fundamental flaw in BLE communication "
        "protocols: companion mobile apps expose static UUIDs that allow attackers to precisely "
        "fingerprint BLE IoT devices. Field tests across 1.28 square miles identified 5,509 "
        "fingerprintable devices and 431 directly vulnerable to unauthorised access."
    ),
    lnk(
        '→ [7a] ACM CCS 2019 — Zuo et al., "Automatic Fingerprinting of Vulnerable BLE IoT Devices with Static UUIDs"',
        "https://dl.acm.org/doi/10.1145/3319535.3354240",
    ),
    SP(2),
    heading("4)  BLE-Guuide: Mobile App-Centric BLE Vulnerability Framework [7b]", 3),
    body(
        "Sivakumaran, Zuo, Lin, and Blasco (ACM ASIA CCS 2023) present Ble-Guuide, a framework "
        "for mobile app-centric security analysis of BLE IoT devices. By mining 17,243 Android APKs "
        "and 12,500+ unique BLE UUIDs from Google Play, the framework reveals that over 70% of "
        "BLE-enabled apps contain at least one security vulnerability including UUID exposure, "
        "Just Works pairing, and absent application-layer authentication."
    ),
    lnk(
        '→ [7b] ACM ASIA CCS 2023 — Sivakumaran et al., "Uncovering Vulnerabilities of BLE IoT from Companion Mobile Apps with Ble-Guuide"',
        "https://dl.acm.org/doi/10.1145/3579856.3595806",
    ),
    body(
        "<b>MREM Application:</b> Real-time detection of provisioning windows and pairing-mode "
        "vulnerabilities, with haptic alert and countdown timer on the TFT display."
    ),
]

# C. Multi-Radio Coexistence
story += [
    SP(4),
    heading("C.  Multi-Radio Coexistence and Cross-Protocol Interference", 2),
    SP(2),
    heading("1)  Experimental Coexistence Assessment [8]", 3),
    body(
        "Giordano et al. (IEEE WoWMoM 2011) present the first experimental study on the simultaneous "
        "coexistence of Wi-Fi, ZigBee, and Bluetooth in the 2.4 GHz ISM band. The study reveals "
        "unexpected packet loss and timing perturbations on channels previously assumed to be "
        "interference-free, establishing coexistence signature patterns that MREM exploits."
    ),
    lnk(
        '→ [8] IEEE WoWMoM 2011 — Giordano et al., "Experimental Assessment of the Coexistence of Wi-Fi, ZigBee, and Bluetooth Devices"',
        "https://ieeexplore.ieee.org/document/5986182",
    ),
    SP(2),
    heading("2)  Packet Traffic Arbitration — Silicon Labs AN1017 [9]", 3),
    body(
        "Silicon Labs Application Note AN1017 describes the IEEE 802.15.2 Packet Traffic Arbitration "
        "(PTA) managed-coexistence scheme that enables coordinated radio sharing on multi-radio "
        "gateways. PTA signalling between co-located radios creates distinctive timing patterns "
        "in the RF environment that MREM uses to infer gateway identity without active injection."
    ),
    lnk(
        '→ [9] Silicon Labs AN1017 — "Zigbee and Thread Coexistence with WiFi"',
        "https://www.silabs.com/documents/public/application-notes/an1017-coexistence-with-wifi.pdf",
    ),
    SP(2),
    heading("3)  Cross-Technology Interference Survey [10]", 3),
    body(
        "Yang, Xu, and Gidlund (International Journal of Distributed Sensor Networks, 2011) survey "
        "cross-technology interference (CTI) mechanisms between IEEE 802.11 and IEEE 802.15.4 "
        "networks in the unlicensed ISM band. The survey demonstrates that high-power Wi-Fi networks "
        "disproportionately disrupt low-power IEEE 802.15.4 devices, introducing latency, packet "
        "corruption, and unpredictable retransmission behaviour — patterns observable passively "
        "by MREM's NRF24L01+ capture pipeline."
    ),
    lnk(
        '→ [10] Int. J. Distributed Sensor Networks 2011 — Yang et al., "Wireless Coexistence between IEEE 802.11 and IEEE 802.15.4 Based Networks: A Survey"',
        "https://doi.org/10.1155/2011/912152",
    ),
    body(
        "<b>MREM Application:</b> Coexistence timing signatures across the tri-radio stack enable "
        "identification of multi-radio gateways without transmitting a single packet."
    ),
]

# Architecture
story += [
    heading("V.  PROPOSED SYSTEM ARCHITECTURE"),
    body(
        "MREM employs a tri-radio distributed architecture to ensure zero packet loss during "
        "high-speed reconnaissance. Table I maps each hardware component to its primary function."
    ),
    SP(4),
]

tdata = [
    [
        Paragraph("<b>Component</b>", sty["TH"]),
        Paragraph("<b>Frequency</b>", sty["TH"]),
        Paragraph("<b>Primary Function</b>", sty["TH"]),
    ],
    [
        Paragraph("ESP32-S3 DevKit", sty["TD"]),
        Paragraph("2.4 GHz", sty["TD"]),
        Paragraph("Main CPU, TFT UI, SD logging, 2.4 GHz Wi-Fi sniffing", sty["TD"]),
    ],
    [
        Paragraph("BW16 RTL8720DN", sty["TD"]),
        Paragraph("2.4/5 GHz + BLE 5.0", sty["TD"]),
        Paragraph("Enterprise Wi-Fi analysis, BLE gateway mapping", sty["TD"]),
    ],
    [
        Paragraph("NRF24L01+", sty["TD"]),
        Paragraph("2.4 GHz (proprietary)", sty["TD"]),
        Paragraph("ShockBurst protocol, sensor/HID sniffing", sty["TD"]),
    ],
    [
        Paragraph('TFT 2.8" ILI9341', sty["TD"]),
        Paragraph("—", sty["TD"]),
        Paragraph("Real-time Exposure Index display, vulnerability heatmap", sty["TD"]),
    ],
    [
        Paragraph("LiPo 3000 mAh", sty["TD"]),
        Paragraph("3.7 V", sty["TD"]),
        Paragraph("10+ hours continuous field operation", sty["TD"]),
    ],
]
t1 = Table(tdata, colWidths=[1.4 * inch, 1.3 * inch, 3.2 * inch])
t1.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), IEEE_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BLUE, WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.4, GRAY_LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
)
story += [
    Paragraph("<b>TABLE I — Hardware-to-Protocol Mapping</b>", sty["Caption"]),
    t1,
    SP(6),
]

story += [
    body(
        "The three radios feed a <b>Correlation Engine</b> that identifies Multi-Radio Gateways "
        "when NRF24 packets and Wi-Fi probe requests share a vendor OUI and exhibit sub-millisecond "
        "timing co-occurrence. A real-time <b>Exposure Index</b> (1–10) is rendered on the TFT "
        "display, with haptic vibration alerting operators when a critical provisioning window is "
        "detected."
    ),
]

# Competitive Analysis
story += [
    heading("VI.  COMPETITIVE ANALYSIS"),
    SP(4),
]
tdata2 = [
    [
        Paragraph("<b>Feature</b>", sty["TH"]),
        Paragraph("<b>Flipper Zero</b>", sty["TH"]),
        Paragraph("<b>HackRF One</b>", sty["TH"]),
        Paragraph("<b>Wi-Fi Pineapple</b>", sty["TH"]),
        Paragraph("<b>MREM</b>", sty["TH"]),
    ],
    ["Multi-Protocol Support", "Partial", "Yes (SDR)", "Wi-Fi Only", "✓ Yes"],
    ["Cross-Protocol Correlation", "✗ No", "✗ No", "✗ No", "✓ Yes"],
    ["Real-Time Risk Score", "✗ No", "✗ No", "✗ No", "✓ Yes"],
    ["Provisioning Detection", "✗ No", "✗ No", "✗ No", "✓ Yes"],
    ["Device Relationships", "✗ No", "✗ No", "✗ No", "✓ Yes"],
    ["Field Ready (Battery)", "✓ Yes", "✗ No", "✓ Yes", "✓ Yes"],
    ["Price (USD)", "$169", "$300", "$99", "< $100"],
]
for i in range(1, len(tdata2)):
    tdata2[i] = [Paragraph(str(c), sty["TD"]) for c in tdata2[i]]
t2 = Table(
    tdata2, colWidths=[1.7 * inch, 0.9 * inch, 0.9 * inch, 1.1 * inch, 0.9 * inch]
)
t2.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), IEEE_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BLUE, WHITE]),
            ("BACKGROUND", (-1, 1), (-1, -1), GREEN_CELL),
            ("GRID", (0, 0), (-1, -1), 0.4, GRAY_LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
)
story += [
    Paragraph("<b>TABLE II — Competitive Tool Comparison</b>", sty["Caption"]),
    t2,
    SP(6),
]
story += [
    body(
        "MREM is the first tool enabling cross-protocol intelligence gathering for multi-radio "
        "IoT environments at under $100, outperforming all existing alternatives on protocol "
        "coverage, analytical capability, and cost."
    ),
]

# Conclusion
story += [
    heading("VII.  CONCLUSION"),
    body(
        "MREM represents the first practical implementation of a tri-radio reconnaissance platform "
        "capable of cross-protocol correlation for multi-radio IoT environments. By surfacing "
        "transition-state vulnerabilities, provisioning windows, and device-to-gateway relationships "
        "that single-protocol tools systematically miss, MREM moves Red Team operations from "
        "active exploitation to strategic intelligence."
    ),
    body(
        "At a total system cost under $100 and 10+ hours of battery life, MREM provides a "
        "cost-effective, field-deployable platform for professional IoT security assessments. "
        "Future development will introduce ML-based behavioural profiling (Q2 2026), multi-MREM "
        "swarm coordination (Q3 2026), and protocol expansion to LoRa, Z-Wave, and Matter/Thread "
        "(Q4 2026). Target venues include USENIX Security, IEEE S&amp;P, and ACM WiSec."
    ),
]

# References
story += [hr(), heading("REFERENCES")]

refs = [
    (
        1,
        'M. Köse, S. Taşcıoğlu, and Z. Telatar, "RF Fingerprinting of IoT Devices Based on Transient Energy Spectrum," <i>IEEE Access</i>, vol. 7, pp. 18715–18726, 2019.',
        "https://ieeexplore.ieee.org/document/8631016",
    ),
    (
        2,
        'T. Jian, B. C. Rendon, E. Ojuba, N. Soltani, Z. Wang, K. Sankhe, A. Gritsenko, J. Dy, K. Chowdhury, and S. Ioannidis, "Deep Learning for RF Fingerprinting: A Massive Experimental Study," <i>IEEE Open Journal of the Communications Society</i>, vol. 1, pp. 122–136, 2020.',
        "https://ieeexplore.ieee.org/document/9063411",
    ),
    (
        3,
        '"Intrusion Detection for IoT Devices Based on RF Fingerprinting Using Deep Learning," in <i>Proc. IEEE International Conference</i>, 2019. [IEEE Xplore Document 8795319]',
        "https://ieeexplore.ieee.org/abstract/document/8795319",
    ),
    (
        4,
        'A. Al-Shawabka, A. Hussain, S. Sciancalepore, G. Oligeri, and P. Papadimitratos, "Edge AI-based Radio Frequency Fingerprinting for IoT Networks," <i>arXiv preprint arXiv:2412.10553</i>, Dec. 2024.',
        "https://arxiv.org/abs/2412.10553",
    ),
    (
        5,
        'Md. S. Hossain and E. Hossain, "Security and Privacy Threats for Bluetooth Low Energy in IoT and Wearable Devices: A Comprehensive Survey," <i>IEEE Open Journal of the Communications Society</i>, vol. 3, pp. 315–348, 2022.',
        "https://ieeexplore.ieee.org/document/9706334",
    ),
    (
        6,
        'Argenox Technologies, "BLE Advertising Primer and Wi-Fi Provisioning Security," <i>Argenox Technical Library</i>, 2025.',
        "https://www.argenox.com/library/bluetooth-low-energy/ble-advertising-primer/",
    ),
    (
        "7a",
        'C. Zuo, H. Wen, Z. Lin, and Y. Zhang, "Automatic Fingerprinting of Vulnerable BLE IoT Devices with Static UUIDs from Mobile Apps," in <i>Proc. ACM CCS</i>, London, UK, 2019, pp. 1–16.',
        "https://dl.acm.org/doi/10.1145/3319535.3354240",
    ),
    (
        "7b",
        'P. Sivakumaran, C. Zuo, Z. Lin, and J. Blasco, "Uncovering Vulnerabilities of BLE IoT from Companion Mobile Apps with Ble-Guuide," in <i>Proc. ACM ASIA CCS</i>, Melbourne, Australia, 2023, pp. 1004–1015.',
        "https://dl.acm.org/doi/10.1145/3579856.3595806",
    ),
    (
        8,
        'S. Giordano, I. Syrotiuk, G. Dini, and S. Eidenbenz, "Experimental Assessment of the Coexistence of Wi-Fi, ZigBee, and Bluetooth Devices," in <i>Proc. IEEE WoWMoM</i>, Lucca, Italy, Jun. 2011.',
        "https://ieeexplore.ieee.org/document/5986182",
    ),
    (
        9,
        'Silicon Laboratories Inc., "AN1017: Zigbee and Thread Coexistence with WiFi," <i>Silicon Labs Application Note</i>, Rev. 2.4, 2021.',
        "https://www.silabs.com/documents/public/application-notes/an1017-coexistence-with-wifi.pdf",
    ),
    (
        10,
        'D. Yang, Y. Xu, and M. Gidlund, "Wireless Coexistence between IEEE 802.11- and IEEE 802.15.4-Based Networks: A Survey," <i>International Journal of Distributed Sensor Networks</i>, vol. 7, no. 1, art. ID 912152, 2011.',
        "https://doi.org/10.1155/2011/912152",
    ),
]

for num, text, url in refs:
    story.append(ref_entry(num, text, url))

doc.build(story)
print("✓ Verified PDF generated successfully.")
