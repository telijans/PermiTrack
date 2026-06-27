import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Orlando Permit Intelligence",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design tokens ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;1,14..32,300&family=Syne:wght@700;800&display=swap');

/* ── Reset & base ─────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Gradient background (Streamlit Cloud compatible) ─── */
.stApp,
[data-testid="stAppViewContainer"],
section.main,
.main {
    background: linear-gradient(160deg, #0D1B3E 0%, #1A3468 45%, #2165BF 100%) !important;
    background-attachment: fixed !important;
}

html, body {
    background: #0D1B3E !important;
}

/* Make content transparent to show gradient */
section[data-testid="stMain"],
.block-container {
    background: transparent !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E8EEF8;
}

/* ── Streamlit chrome removal ──────────────────────────── */
#MainMenu, footer { visibility: hidden; }
header { visibility: visible !important; }
header[data-testid="stHeader"] { background: transparent !important; }
.block-container {
    padding: 0 6vw 5rem 6vw !important;
    max-width: 1280px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* ── Main layout centering ────────────────────────────── */
.main .block-container {
    padding-left: clamp(1.5rem, 6vw, 5rem) !important;
    padding-right: clamp(1.5rem, 6vw, 5rem) !important;
}
section[data-testid="stMain"] > div {
    max-width: 1280px;
    margin: 0 auto;
}

/* ── Masthead ──────────────────────────────────────────── */
.masthead {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin: 1.5rem 0 2.5rem 0;
    display: flex;
    align-items: center;
    gap: 2rem;
    box-shadow: 0 8px 48px rgba(13,27,62,0.50), inset 0 1px 0 rgba(255,255,255,0.10);
}
.masthead-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    background: linear-gradient(90deg, #2165BF, #05D3F2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem;
    display: block;
}
.masthead-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    line-height: 1;
    color: #FFFFFF;
}
.masthead-title span {
    background: linear-gradient(110deg, #2165BF 0%, #05D3F2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.masthead-divider {
    width: 1px;
    height: 40px;
    background: rgba(255,255,255,0.18);
    flex-shrink: 0;
}
.masthead-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem;
    color: #7A9CC8;
    line-height: 1.85;
}
.masthead-meta strong { color: #B8D0F0; font-weight: 500; }
.masthead-actions { margin-left: auto; display: flex; align-items: center; gap: 0.75rem; }
.live-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.08em;
    color: #22D07A;
    background: rgba(34,208,122,0.10);
    border: 1px solid rgba(34,208,122,0.25);
    border-radius: 100px;
    padding: 4px 12px;
}
.live-dot {
    width: 6px; height: 6px;
    background: #22D07A;
    border-radius: 50%;
    animation: pulse 2.4s cubic-bezier(0.4,0,0.6,1) infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.25; transform: scale(0.85); }
}

/* ── Glass card base ───────────────────────────────────── */
.glass {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    box-shadow: 0 4px 32px rgba(13,27,62,0.40), inset 0 1px 0 rgba(255,255,255,0.10);
    transition: border-color 0.35s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.35s cubic-bezier(0.34,1.56,0.64,1),
                transform 0.35s cubic-bezier(0.34,1.56,0.64,1);
}
.glass:hover {
    border-color: rgba(33,101,191,0.30);
    box-shadow: 0 8px 48px rgba(33,101,191,0.14), inset 0 1px 0 rgba(5,211,242,0.07);
    transform: translateY(-1px);
}

/* ── KPI row ───────────────────────────────────────────── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
    margin: 0 0 2.5rem;
}
.kpi-card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 18px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 4px 24px rgba(13,27,62,0.30), inset 0 1px 0 rgba(255,255,255,0.10);
    transition: border-color 0.35s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.35s cubic-bezier(0.34,1.56,0.64,1),
                transform 0.35s cubic-bezier(0.34,1.56,0.64,1);
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #2165BF, #05D3F2);
    opacity: 0;
    transition: opacity 0.35s ease;
}
.kpi-card:hover {
    border-color: rgba(33,101,191,0.28);
    box-shadow: 0 8px 40px rgba(33,101,191,0.16), inset 0 1px 0 rgba(5,211,242,0.07);
    transform: translateY(-2px);
}
.kpi-card:hover::before { opacity: 1; }
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #7AAAD8;
    margin-bottom: 0.6rem;
    display: block;
}
.kpi-value {
    font-family: 'Inter', sans-serif;
    font-size: clamp(1.25rem, 2.2vw, 1.75rem);
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.1;
    letter-spacing: -0.01em;
    display: block;
    margin-bottom: 0.5rem;
    word-break: break-word;
    overflow-wrap: break-word;
}
.kpi-delta {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.04em;
    display: flex;
    align-items: center;
    gap: 4px;
}
.kpi-delta.up   { color: #22D07A; }
.kpi-delta.down { color: #FF5A5A; }
.kpi-delta.neutral { color: #7AAAD8; }

/* ── Section labels ────────────────────────────────────── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #05D3F2;
    margin: 2.5rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(5,211,242,0.25), transparent);
}

/* ── Chart wrapper ─────────────────────────────────────── */
.chart-glass {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.chart-glass:hover {
    border-color: rgba(33,101,191,0.22);
    box-shadow: 0 4px 32px rgba(33,101,191,0.10);
}

/* ── Cache / demo notice ───────────────────────────────── */
.cache-notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    letter-spacing: 0.04em;
    color: #FFB84D;
    background: rgba(245,166,35,0.12);
    border: 1px solid rgba(245,166,35,0.30);
    border-radius: 10px;
    padding: 0.6rem 1rem;
    margin-bottom: 1.5rem;
}

/* ── Sidebar ───────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(13,27,62,0.95) 0%, rgba(26,52,104,0.92) 50%, rgba(33,101,191,0.88) 100%) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255,255,255,0.12) !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}
section[data-testid="stSidebar"] * { color: #A8C4E8 !important; }
section[data-testid="stSidebar"] h3 { color: #FFFFFF !important; font-size: 0.8rem !important; letter-spacing: 0.06em !important; }
section[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Tabs ──────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    padding: 5px !important;
    gap: 4px !important;
    margin-bottom: 2rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: #7AAAD8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(180deg, rgba(13,27,62,0.95) 0%, rgba(26,52,104,0.92) 50%, rgba(33,101,191,0.88) 100%) !important;
    color: #EEF2FA !important;
    box-shadow: 0 2px 16px rgba(33,101,191,0.20) !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: rgba(255,255,255,0.05) !important;
    color: #8A9BB8 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Buttons ───────────────────────────────────────────── */
.stDownloadButton > button, .stButton > button {
    background: linear-gradient(135deg, #2165BF, #05D3F2) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.55rem 1.5rem !important;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    box-shadow: 0 4px 20px rgba(33,101,191,0.30) !important;
    letter-spacing: 0.01em !important;
}
.stDownloadButton > button:hover, .stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 32px rgba(33,101,191,0.45) !important;
    filter: brightness(1.08) !important;
}
.stDownloadButton > button:active, .stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
    transition-duration: 0.1s !important;
}

/* ── Dataframe ─────────────────────────────────────────── */
.stDataFrame {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    background: rgba(255,255,255,0.02) !important;
}
.stDataFrame iframe { border-radius: 14px !important; }

/* ── Metrics (fallback) ────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetricLabel"] { color: #7AAAD8 !important; font-size: 0.72rem !important; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; font-weight: 700 !important; }

/* ── Inputs ────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #E8EEF8 !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: rgba(33,101,191,0.5) !important;
    box-shadow: 0 0 0 3px rgba(33,101,191,0.12) !important;
    outline: none !important;
}

/* ── Spinner ───────────────────────────────────────────── */
.stSpinner > div { border-top-color: #2165BF !important; }

/* ── Chart captions ───────────────────────────────────── */
.chart-caption {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.6rem !important;
    font-weight: 400 !important;
    color: #B8D0F0 !important;
    margin: -0.5rem 0 1.25rem 0 !important;
    line-height: 1.4 !important;
    text-align: center !important;
    display: block !important;
    letter-spacing: 0.01em;
}

/* ── Disclaimer ────────────────────────────────────────── */
.disclaimer {
    font-family: 'DM Mono', monospace;
    font-size: 0.60rem;
    color: rgba(255,255,255,0.70);
    margin-top: 3rem;
    padding-top: 1.25rem;
    border-top: 1px solid rgba(255,255,255,0.10);
    line-height: 1.8;
    letter-spacing: 0.02em;
}

/* ── Scrollbar ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.20); border-radius: 100px; }
::-webkit-scrollbar-thumb:hover { background: rgba(5,211,242,0.40); }

/* ── Selection ─────────────────────────────────────────── */
::selection { background: rgba(33,101,191,0.35); color: #EEF2FA; }

/* ════════════════════════════════════════════════════════════════════
   MOBILE RESPONSIVENESS
   ════════════════════════════════════════════════════════════════════ */

/* ── Tablet and below (≤768px) ──────────────────────────── */
@media (max-width: 768px) {
    /* KPI cards: 2 columns on tablet */
    .kpi-row {
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 1rem !important;
    }

    .kpi-card {
        padding: 1rem 1.2rem !important;
    }

    /* Masthead adjustments */
    .masthead {
        padding: 1.5rem !important;
        gap: 1.5rem !important;
    }

    .masthead-title {
        font-size: 1.75rem !important;
    }

    /* Reduce container padding */
    .block-container {
        padding: 0 4vw 4rem 4vw !important;
    }

    .main .block-container {
        padding-left: clamp(1rem, 4vw, 3rem) !important;
        padding-right: clamp(1rem, 4vw, 3rem) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        padding: 0.45rem 1rem !important;
        font-size: 0.78rem !important;
    }

    /* Charts */
    .chart-glass {
        padding: 1rem !important;
    }
}

/* ── Mobile and below (≤480px) ──────────────────────────── */
@media (max-width: 480px) {
    /* KPI cards: 1 column on mobile */
    .kpi-row {
        grid-template-columns: 1fr !important;
        gap: 0.875rem !important;
        margin: 0 0 2rem !important;
    }

    .kpi-card {
        padding: 1rem !important;
    }

    .kpi-value {
        font-size: clamp(1.15rem, 5vw, 1.5rem) !important;
    }

    /* Masthead: stack vertically */
    .masthead {
        flex-direction: column !important;
        align-items: flex-start !important;
        padding: 1.25rem 1rem !important;
        gap: 1rem !important;
    }

    .masthead-title {
        font-size: 1.5rem !important;
    }

    .masthead-eyebrow {
        font-size: 0.6rem !important;
    }

    .masthead-divider {
        display: none !important; /* Hide vertical divider when stacked */
    }

    .masthead-meta {
        font-size: 0.62rem !important;
    }

    .masthead-actions {
        margin-left: 0 !important;
        width: 100%;
    }

    /* Container padding */
    .block-container {
        padding: 0 1rem 3rem 1rem !important;
    }

    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        padding: 4px !important;
        gap: 3px !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.4rem 0.75rem !important;
        font-size: 0.75rem !important;
    }

    /* Buttons: full width on mobile */
    .stDownloadButton > button, .stButton > button {
        padding: 0.5rem 1rem !important;
        font-size: 0.78rem !important;
        width: 100% !important;
    }

    /* Section labels */
    .section-label {
        font-size: 0.58rem !important;
        margin: 2rem 0 0.875rem !important;
    }

    /* Charts */
    .chart-glass {
        padding: 0.875rem !important;
        margin-bottom: 1rem !important;
    }

    .chart-caption {
        font-size: 0.58rem !important;
        margin: -0.375rem 0 1rem 0 !important;
    }

    /* Ensure no horizontal overflow */
    body, .stApp, .main {
        overflow-x: hidden !important;
    }
}

/* ── Small mobile (≤375px) ──────────────────────────────── */
@media (max-width: 375px) {
    .masthead-title {
        font-size: 1.35rem !important;
    }

    .kpi-card {
        padding: 0.875rem !important;
    }

    .kpi-label {
        font-size: 0.58rem !important;
    }

    .block-container {
        padding: 0 0.875rem 2.5rem 0.875rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.375rem 0.625rem !important;
        font-size: 0.7rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── Data layer ─────────────────────────────────────────────────────────────────
CACHE_FILE = Path(__file__).parent / "permits_cache.json"
CACHE_MAX_AGE_HOURS = 12
SODA_URL = "https://data.cityoforlando.net/resource/ryhf-m453.json"


@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    """Load permit data — live API → local cache."""
    # 1. Try live API
    try:
        # Fetch last 12 months of processed permits
        twelve_months_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        params = {
            "$where": f"processed_date >= '{twelve_months_ago}'",
            "$order": "processed_date DESC",
            "$limit": 50000  # High limit to get all records in the 12-month window
        }
        resp = requests.get(SODA_URL, params=params, timeout=15)
        resp.raise_for_status()
        records = resp.json()
        if records:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w") as f:
                json.dump({"fetched_at": datetime.now().isoformat(), "records": records}, f)
            return pd.DataFrame(records), "live", datetime.now()
    except Exception:
        pass

    # 2. Try local cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE) as f:
                payload = json.load(f)
            return pd.DataFrame(payload["records"]), "cache", datetime.fromisoformat(payload["fetched_at"])
        except Exception:
            pass

    # 3. No data available
    st.error("Unable to load data. Please check your internet connection and try again.")
    st.stop()


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Type-cast and enrich the raw dataframe."""
    if df.empty:
        return df

    # Column name normalization: map snake_case API columns to lowercase demo columns
    column_mapping = {
        'permit_number': 'permitnumber',
        'application_type': 'applicationtype',
        'parcel_number': 'parcelno',
        'processed_date': 'processeddate',
        'issue_permit_date': 'issuepermidate',
        'pending_issuance_date': 'pendingissuancedate',
        'collect_permit_fees_date': 'collectpermitfeesdate',
        'estimated_cost': 'estimatedcost',
        'contractor_name': 'contractorname',
        'contractor_address': 'contractoraddress',
        'contractor_phone_number': 'contractorphone',
        'permit_address': 'permitaddress',
        'square_footage': 'squarefootage',
        'of_cycles': 'numberofcycles',
        'of_pdoxwkflw': 'numberofpdoxwkflw',
        'application_status': 'applicationstatus',
        'property_owner_name': 'propertyownername',
        'parcel_owner_name': 'parcelownername',
        'plan_review_type': 'planreviewtype',
        'under_review_date': 'underreviewdate',
        'prescreen_completed_date': 'prescreencompleteddate',
        'project_name': 'projectname',
        'commissioner_district': 'commissionerdistrict',
        'private_provider': 'privateprovider',
        'private_provider_company_name': 'privateprovidercompanyname',
        'private_provider_qualifier_name': 'privateproviderqualifiername',
        'pdoxbatch_date': 'projectdoxbatchdate',
        'review_started_date_excluding': 'reviewstarteddateexcludingprescreen',
        'day_to_issuance': 'daystoissuepermit',
        'mainstreet_district': 'mainstreetdistrict',
        'final_date': 'finaldate',
        'coo_date': 'coodate',
        'coc_date': 'cocdate',
        'temp_coo_date': 'tempcoodate'
    }

    # Rename columns that exist in the dataframe
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    # Add empty columns if they don't exist
    if 'contractorphone' not in df.columns:
        df['contractorphone'] = ""
    if 'mainstreetdistrict' not in df.columns:
        df['mainstreetdistrict'] = "Not in district"

    # If daystoissuepermit still doesn't exist (not in API), calculate it
    if 'daystoissuepermit' not in df.columns:
        if 'processeddate' in df.columns and 'issuepermidate' in df.columns:
            df['processeddate_temp'] = pd.to_datetime(df['processeddate'], errors='coerce')
            df['issuepermidate_temp'] = pd.to_datetime(df['issuepermidate'], errors='coerce')
            df['daystoissuepermit'] = (df['issuepermidate_temp'] - df['processeddate_temp']).dt.days
            df.drop(['processeddate_temp', 'issuepermidate_temp'], axis=1, inplace=True)

    # Dates
    for col in ["processeddate", "issuepermidate", "finaldate", "coodate", "cocdate", "pendingissuancedate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Numerics
    for col in ["estimatedcost", "daystoissuepermit", "squarefootage", "numberofcycles"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Text cleanup
    df["contractorname"] = df.get("contractorname", pd.Series(dtype=str)).fillna("Owner-builder").replace("", "Owner-builder")
    df["neighborhood"] = df.get("neighborhood", pd.Series(dtype=str)).fillna("Unassigned")
    df["mainstreetdistrict"] = df.get("mainstreetdistrict", pd.Series(dtype=str)).fillna("Not in district")
    df["applicationtype"] = df.get("applicationtype", pd.Series(dtype=str)).str.strip()

    # Calculated columns
    df["valuation_tier"] = pd.cut(
        df["estimatedcost"],
        bins=[0, 50_000, 500_000, float("inf")],
        labels=["Small (<$50K)", "Mid ($50K–$500K)", "Large (>$500K)"],
        right=True
    )
    df["year_month"] = df["processeddate"].dt.to_period("M").astype(str)
    df["has_contractor"] = df["contractorname"].ne("Owner-builder")

    return df


# ── Load ───────────────────────────────────────────────────────────────────────
with st.spinner("Fetching Orlando permit data…"):
    raw_df, data_source, fetched_at = load_data()

df = clean(raw_df)

# ── Masthead ───────────────────────────────────────────────────────────────────
fetched_str = fetched_at.strftime("%b %d, %Y %H:%M") if fetched_at else "unknown"

# Build source pill
if data_source == "live":
    pill_html = '<span class="live-pill"><span class="live-dot"></span>Live API</span>'
else:
    pill_html = '<span class="live-pill" style="color: #FFB84D; background: rgba(255,184,77,0.10); border-color: rgba(255,184,77,0.25);"><span class="live-dot" style="background: #FFB84D; animation: none;"></span>Cached</span>'

st.markdown(f"""
<div class="masthead">
  <div>
    <span class="masthead-eyebrow">Orlando · Permit Intelligence</span>
    <h1 class="masthead-title">Permi<span>Track</span></h1>
  </div>
  <div class="masthead-divider"></div>
  <div class="masthead-meta">
    <strong>{len(df):,}</strong> records &nbsp;·&nbsp; <strong>Updated</strong> {fetched_str}
  </div>
  <div class="masthead-actions">
    {pill_html}
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar filters ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")

    # Date range
    min_date = df["processeddate"].min().date() if not df["processeddate"].isna().all() else datetime(2020,1,1).date()
    max_date = df["processeddate"].max().date() if not df["processeddate"].isna().all() else datetime.today().date()
    default_start = max_date - timedelta(days=365)

    # Ensure default_start is not before min_date
    if default_start < min_date:
        default_start = min_date

    date_range = st.date_input(
        "Date range",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # App type filter
    app_types = sorted(df["applicationtype"].dropna().unique().tolist())
    selected_types = st.multiselect("Application type", app_types, default=[])

    # Neighborhood filter
    neighborhoods = sorted(df["neighborhood"].dropna().unique().tolist())
    selected_neighborhoods = st.multiselect("Neighborhood", neighborhoods, default=[])

    # Valuation tier
    tiers = ["Small (<$50K)", "Mid ($50K–$500K)", "Large (>$500K)"]
    selected_tiers = st.multiselect("Valuation tier", tiers, default=[])

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.62rem;color:#4A6A9A;font-family:monospace;line-height:1.9;letter-spacing:0.04em'>
    Data: City of Orlando<br>
    SODA API · ryhf-m453<br>
    Refreshes daily at 7 AM
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ──────────────────────────────────────────────────────────────
fdf = df.copy()

if len(date_range) == 2:
    start_dt = pd.Timestamp(date_range[0])
    end_dt = pd.Timestamp(date_range[1])
    fdf = fdf[fdf["processeddate"].between(start_dt, end_dt)]

if selected_types:
    fdf = fdf[fdf["applicationtype"].isin(selected_types)]

if selected_neighborhoods:
    fdf = fdf[fdf["neighborhood"].isin(selected_neighborhoods)]

if selected_tiers:
    fdf = fdf[fdf["valuation_tier"].isin(selected_tiers)]

if data_source == "cache" and fetched_at:
    age_h = (datetime.now() - fetched_at).seconds // 3600
    st.markdown(f'<div class="cache-notice">⚠ Showing cached data from {fetched_str} ({age_h}h ago) — live API unavailable</div>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Contractor leads", "🗺 Neighborhood pulse"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    # KPIs
    total_permits = len(fdf)
    total_value = fdf["estimatedcost"].sum()
    avg_days_raw = fdf["daystoissuepermit"].mean()
    unique_contractors = fdf["contractorname"].nunique()

    # Format avg days - handle NaN gracefully
    if pd.isna(avg_days_raw):
        avg_days_display = "—"
        avg_days_delta = "no issued permits in period"
    else:
        avg_days_display = f"{avg_days_raw:.0f}"
        # Count how many permits have been issued
        issued_count = fdf["daystoissuepermit"].notna().sum()
        avg_days_delta = f"based on {issued_count:,} issued permits"

    # MoM change — anchor to data's own max date
    data_max = fdf["processeddate"].max()
    this_month = data_max.replace(day=1)
    last_month = (this_month - timedelta(days=1)).replace(day=1)
    this_m_count = len(fdf[fdf["processeddate"] >= pd.Timestamp(this_month)])
    last_m_count = len(fdf[fdf["processeddate"].between(pd.Timestamp(last_month), pd.Timestamp(this_month))])
    mom_pct = ((this_m_count - last_m_count) / last_m_count * 100) if last_m_count > 0 else 0
    mom_label = f"{'↑' if mom_pct >= 0 else '↓'} {abs(mom_pct):.1f}% vs last month"
    mom_class = "up" if mom_pct >= 0 else "down"

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label">Permits filed</div>
        <div class="kpi-value">{total_permits:,}</div>
        <div class="kpi-delta {mom_class}">{mom_label}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total estimated value</div>
        <div class="kpi-value">${total_value/1_000_000:.1f}M</div>
        <div class="kpi-delta neutral">across filtered period</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg days to issue</div>
        <div class="kpi-value">{avg_days_display}</div>
        <div class="kpi-delta neutral">{avg_days_delta}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Active contractors</div>
        <div class="kpi-value">{unique_contractors:,}</div>
        <div class="kpi-delta neutral">unique names in period</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="section-label">Permit volume over time</div>', unsafe_allow_html=True)
        vol = fdf.groupby("year_month").size().reset_index(name="count")
        vol = vol.sort_values("year_month")
        fig = px.area(vol, x="year_month", y="count",
                      color_discrete_sequence=["#2165BF"])
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=260,
            xaxis=dict(showgrid=False, title="", tickangle=-45, tickfont=dict(size=10, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="", tickfont=dict(size=10, family="DM Mono", color="#B8D0F0")),
            showlegend=False
        )
        fig.update_traces(fillcolor="rgba(33,101,191,0.12)", line_width=2, line_color="#05D3F2")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<p class="chart-caption">Each point shows how many permits were filed in that month. Rising peaks mean construction is picking up; dips suggest slower periods.</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-label">By application type</div>', unsafe_allow_html=True)
        by_type = fdf["applicationtype"].value_counts().head(8).reset_index()
        by_type.columns = ["type", "count"]
        fig2 = px.bar(by_type, x="count", y="type", orientation="h",
                      color_discrete_sequence=["#2165BF"])
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=260,
            xaxis=dict(showgrid=False, title="", tickfont=dict(size=10, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=10, family="DM Mono", color="#B8D0F0")),
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('<p class="chart-caption">Breakdown of what kind of work is being permitted — building, electrical, plumbing, and so on. The longest bar is the most common type in your selected period.</p>', unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-label">Value by neighborhood (top 15)</div>', unsafe_allow_html=True)
        nbhd_val = fdf.groupby("neighborhood")["estimatedcost"].sum().nlargest(15).reset_index()
        fig3 = px.bar(nbhd_val, x="estimatedcost", y="neighborhood", orientation="h",
                      color_discrete_sequence=["#2165BF"])
        fig3.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=340,
            xaxis=dict(showgrid=False, title="", tickformat="$,.0f", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0"), autorange="reversed"),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('<p class="chart-caption">Total dollar value of all permitted projects per neighborhood. A longer bar means more construction money is flowing into that area.</p>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="section-label">Valuation tier distribution</div>', unsafe_allow_html=True)
        tier_counts = fdf["valuation_tier"].value_counts().reset_index()
        tier_counts.columns = ["tier", "count"]
        fig4 = px.pie(tier_counts, values="count", names="tier",
                      color_discrete_sequence=["#1A3A6E", "#2165BF", "#05D3F2"],
                      hole=0.55)
        fig4.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), height=340,
            legend=dict(
                font=dict(size=10, family="DM Mono", color="#B8D0F0"),
                bgcolor="rgba(0,0,0,0)", borderwidth=0,
                orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        fig4.update_traces(
            textfont=dict(family="DM Mono", size=10, color="#FFFFFF"),
            textinfo="percent",
            hovertemplate="<b>%{label}</b><br>%{value:,} permits<br>%{percent}<extra></extra>",
            marker=dict(line=dict(color="rgba(255,255,255,0.06)", width=2))
        )
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('<p class="chart-caption">Shows whether activity is dominated by small jobs (under $50K), mid-size projects ($50K–$500K), or large developments (over $500K).</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CONTRACTOR LEADS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown('<div class="section-label">Find contractor leads</div>', unsafe_allow_html=True)

    search_col, work_col, min_col = st.columns([2, 2, 1])

    with search_col:
        name_search = st.text_input("Search contractor name", placeholder="e.g. Smith, ABC Electric…")
    with work_col:
        worktypes = sorted(fdf["worktype"].dropna().unique().tolist()) if "worktype" in fdf.columns else []
        selected_work = st.multiselect("Work type", worktypes)
    with min_col:
        min_value = st.number_input("Min project value ($)", value=0, step=10000, format="%d")

    # Apply lead filters
    leads = fdf[fdf["contractorname"] != "Owner-builder"].copy()

    if name_search:
        leads = leads[leads["contractorname"].str.contains(name_search, case=False, na=False)]
    if selected_work:
        leads = leads[leads["worktype"].isin(selected_work)]
    if min_value > 0:
        leads = leads[leads["estimatedcost"] >= min_value]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Contractors found", f"{leads['contractorname'].nunique():,}")
    with k2:
        st.metric("Total permits", f"{len(leads):,}")
    with k3:
        st.metric("Total value", f"${leads['estimatedcost'].sum()/1_000_000:.1f}M")
    with k4:
        st.metric("Avg value / permit", f"${leads['estimatedcost'].mean():,.0f}")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="section-label">Top contractors by permit count</div>', unsafe_allow_html=True)
        top_contractors = (
            leads.groupby("contractorname")
            .agg(permits=("permitnumber", "count"), total_value=("estimatedcost", "sum"))
            .sort_values("permits", ascending=False)
            .head(15)
            .reset_index()
        )
        fig5 = px.bar(top_contractors, x="permits", y="contractorname", orientation="h",
                      color_discrete_sequence=["#2165BF"])
        fig5.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=360,
            xaxis=dict(showgrid=False, title="Permit count", title_font=dict(color="#FFFFFF", size=9), tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0"), autorange="reversed"),
            showlegend=False
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown('<p class="chart-caption">The most active contractors by number of permits filed. High permit counts indicate contractors with a steady pipeline of work in Orlando.</p>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-label">Top contractors by project value</div>', unsafe_allow_html=True)
        top_by_val = (
            leads.groupby("contractorname")["estimatedcost"]
            .sum().nlargest(15).reset_index()
        )
        fig6 = px.bar(top_by_val, x="estimatedcost", y="contractorname", orientation="h",
                      color_discrete_sequence=["#2165BF"])
        fig6.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=360,
            xaxis=dict(showgrid=False, title="Total value", title_font=dict(color="#FFFFFF", size=9), tickformat="$,.0f", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0"), autorange="reversed"),
            showlegend=False
        )
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown('<p class="chart-caption">The same contractors ranked by the total dollar value of their projects. A contractor with fewer permits but a long bar here is working on higher-value jobs.</p>', unsafe_allow_html=True)

    # Lead table
    st.markdown('<div class="section-label">Contractor lead list — export ready</div>', unsafe_allow_html=True)

    display_cols = ["contractorname", "contractorphone", "permitaddress", "applicationtype",
                    "worktype", "estimatedcost", "valuation_tier", "processeddate", "neighborhood"]
    available_cols = [c for c in display_cols if c in leads.columns]

    lead_table = (
        leads[available_cols]
        .sort_values("estimatedcost", ascending=False)
        .rename(columns={
            "contractorname": "Contractor",
            "contractorphone": "Phone",
            "permitaddress": "Address",
            "applicationtype": "Type",
            "worktype": "Work type",
            "estimatedcost": "Est. value",
            "valuation_tier": "Tier",
            "processeddate": "Filed",
            "neighborhood": "Neighborhood"
        })
    )

    if "Est. value" in lead_table.columns:
        lead_table["Est. value"] = lead_table["Est. value"].apply(
            lambda x: f"${x:,.0f}" if pd.notna(x) else "—"
        )
    if "Filed" in lead_table.columns:
        lead_table["Filed"] = lead_table["Filed"].dt.strftime("%b %d, %Y")

    st.dataframe(lead_table, use_container_width=True, height=380)

    # Export button
    csv = lead_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download leads as CSV",
        data=csv,
        file_name=f"orlando_contractor_leads_{datetime.today().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — NEIGHBORHOOD PULSE
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown('<div class="section-label">Activity by neighborhood</div>', unsafe_allow_html=True)

    # Neighborhood summary
    nbhd = (
        fdf.groupby("neighborhood")
        .agg(
            permits=("permitnumber", "count"),
            total_value=("estimatedcost", "sum"),
            avg_value=("estimatedcost", "mean"),
            avg_days=("daystoissuepermit", "mean"),
            unique_contractors=("contractorname", "nunique")
        )
        .reset_index()
        .sort_values("permits", ascending=False)
    )

    # MoM velocity per neighborhood — anchor to data's own max date so it works on any dataset
    data_max_date = fdf["processeddate"].max()
    recent = fdf[fdf["processeddate"] >= data_max_date - timedelta(days=30)]
    prior = fdf[fdf["processeddate"].between(
        data_max_date - timedelta(days=60),
        data_max_date - timedelta(days=30)
    )]
    recent_counts = recent.groupby("neighborhood").size().rename("recent")
    prior_counts = prior.groupby("neighborhood").size().rename("prior")
    velocity = pd.concat([recent_counts, prior_counts], axis=1).fillna(0)
    velocity["velocity_pct"] = ((velocity["recent"] - velocity["prior"]) / velocity["prior"].replace(0, 1) * 100).round(1)
    nbhd = nbhd.merge(velocity[["velocity_pct"]], on="neighborhood", how="left")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<div class="section-label">Permit volume — top 20 neighborhoods</div>', unsafe_allow_html=True)
        top20 = nbhd.head(20)
        fig7 = px.bar(top20, x="permits", y="neighborhood", orientation="h",
                      color="total_value",
                      color_continuous_scale=["#1A2340", "#2165BF", "#05D3F2"],
                      labels={"permits": "Permits", "total_value": "Est. value"})
        fig7.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=480,
            xaxis=dict(showgrid=False, title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0"), autorange="reversed"),
            coloraxis_colorbar=dict(title="Value", tickformat="$,.0f", tickfont=dict(size=8, color="#B8D0F0"), title_font=dict(color="#FFFFFF", size=9))
        )
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('<p class="chart-caption">Total permits per neighborhood over your selected period. Bar color reflects total project value — brighter means more dollars flowing in.</p>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-label">30-day momentum (MoM change %)</div>', unsafe_allow_html=True)
        momentum = nbhd[nbhd["velocity_pct"].notna()].nlargest(20, "permits")
        momentum = momentum.sort_values("velocity_pct", ascending=True)
        colors = ["#22D07A" if v >= 0 else "#FF5A5A" for v in momentum["velocity_pct"]]
        fig8 = go.Figure(go.Bar(
            x=momentum["velocity_pct"],
            y=momentum["neighborhood"],
            orientation="h",
            marker_color=colors,
            text=momentum["velocity_pct"].apply(lambda x: f"{x:+.0f}%"),
            textposition="outside",
            textfont=dict(size=9, family="DM Mono", color="#B8D0F0")
        ))
        fig8.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10, b=10, l=0, r=0), height=480,
            xaxis=dict(showgrid=False, title="MoM % change", title_font=dict(color="#FFFFFF", size=9), zeroline=True, zerolinecolor="rgba(255,255,255,0.08)",
                       tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
            yaxis=dict(showgrid=False, title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
            showlegend=False
        )
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown('<p class="chart-caption">Compares the most recent 30 days of permit filings to the 30 days before that. Green means activity is growing; red means it slowed down.</p>', unsafe_allow_html=True)

    # Permit type mix per neighborhood
    st.markdown('<div class="section-label">Permit type mix by neighborhood (top 12)</div>', unsafe_allow_html=True)
    top12_nbhd = nbhd.head(12)["neighborhood"].tolist()
    mix = fdf[fdf["neighborhood"].isin(top12_nbhd)].groupby(
        ["neighborhood", "applicationtype"]).size().reset_index(name="count")
    fig9 = px.bar(mix, x="neighborhood", y="count", color="applicationtype",
                  barmode="stack",
                  color_discrete_sequence=["#2165BF","#05D3F2","#3B82C4","#0EA5C9","#6366F1","#8B5CF6"])
    fig9.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=0, r=0), height=320,
        xaxis=dict(showgrid=False, title="", tickangle=-35, tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
        legend=dict(title="", font=dict(size=9, family="DM Mono", color="#B8D0F0"), bgcolor="rgba(0,0,0,0)", borderwidth=0)
    )
    st.plotly_chart(fig9, use_container_width=True)
    st.markdown('<p class="chart-caption">For each neighborhood, shows the mix of permit types. A neighborhood dominated by one color is specializing in that type of work — useful for spotting where new construction vs. renovation is happening.</p>', unsafe_allow_html=True)

    # Main Street districts
    if "mainstreetdistrict" in fdf.columns:
        st.markdown('<div class="section-label">Main Street district activity</div>', unsafe_allow_html=True)
        ms = (fdf[fdf["mainstreetdistrict"] != "Not in district"]
              .groupby("mainstreetdistrict")
              .agg(permits=("permitnumber", "count"), value=("estimatedcost", "sum"))
              .reset_index().sort_values("permits", ascending=False))
        if not ms.empty:
            fig10 = px.bar(ms, x="mainstreetdistrict", y="permits",
                           color="value",
                           color_continuous_scale=["#1A2340", "#2165BF"],
                           labels={"mainstreetdistrict": "", "permits": "Permits", "value": "Est. value"})
            fig10.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=0, r=0), height=240,
                xaxis=dict(showgrid=False, tickangle=-20, tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="", tickfont=dict(size=9, family="DM Mono", color="#B8D0F0")),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig10, use_container_width=True)
            st.markdown('<p class="chart-caption">Activity within Orlando\'s designated Main Street commercial corridors. Taller bars with brighter color mean higher-value projects in that district.</p>', unsafe_allow_html=True)

    # Neighborhood data table
    st.markdown('<div class="section-label">Full neighborhood summary table</div>', unsafe_allow_html=True)
    nbhd_display = nbhd.copy()
    nbhd_display["total_value"] = nbhd_display["total_value"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
    nbhd_display["avg_value"] = nbhd_display["avg_value"].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "—")
    nbhd_display["avg_days"] = nbhd_display["avg_days"].apply(lambda x: f"{x:.0f}" if pd.notna(x) else "—")
    nbhd_display["velocity_pct"] = nbhd_display["velocity_pct"].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "—")
    nbhd_display.columns = ["Neighborhood", "Permits", "Total value", "Avg value",
                             "Avg days", "Contractors", "30d momentum"]
    st.dataframe(nbhd_display, use_container_width=True, height=340)

# ── Disclaimer ─────────────────────────────────────────────────────────────────
current_year = datetime.now().year
st.markdown(f"""
<div class="disclaimer">
Data sourced from the City of Orlando Permit Applications dataset via the SODA API.
The City of Orlando does not guarantee the accuracy of this information and will not be responsible for any error or omission,
or for the use of, or the results obtained from the use of this information.
All data is provided for informational purposes only. Attempts to derive specific addresses from Business Tax Receipt data are strictly prohibited per City policy.
</div>
<div style="text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06);">
  <p style="font-family: 'DM Mono', monospace; font-size: 0.58rem; color: rgba(255,255,255,0.50); letter-spacing: 0.02em; margin: 0;">
    © {current_year} Telijans, LLC. All rights reserved.
  </p>
</div>
""", unsafe_allow_html=True)