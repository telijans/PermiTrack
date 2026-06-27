# PermiTrack — Orlando Permit Intelligence

A Streamlit app that turns the City of Orlando's public permit data into actionable business intelligence.

## Features

- **Overview tab** — KPI cards, permit volume trends, top neighborhoods by value, valuation tier distribution
- **Contractor leads tab** — searchable lead list with phone numbers, export to CSV, ranked by permit count and project value
- **Neighborhood pulse tab** — 30-day momentum rankings, permit type mix, Main Street district activity

## Data source

City of Orlando SODA API — Permit Applications dataset (`ryhf-m453`)
Endpoint: `https://data.cityoforlando.net/resource/ryhf-m453.json`

**Data Coverage:** Last 12 months of processed permits
**Refresh Rate:** Live API queries on load, cached for 1 hour
**No API key required** for public access

## Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

App opens at `http://localhost:8501`

## Deploy to Streamlit Cloud (free)

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file path: `app.py`
5. Deploy — public URL in ~2 minutes

## Deploy to other platforms

**Railway / Render / Fly.io:**
```bash
# Start command
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Data Loading & Caching

The app uses a **2-tier data loading system**:

1. **Live API** (primary) — Fetches permits from the last 12 months via SODA API
2. **Local cache** (fallback) — Uses `permits_cache.json` if the API is unavailable

**Caching behavior:**
- Streamlit's `@st.cache_data` caches the DataFrame for 1 hour per session
- Cache is written on every successful API call
- If both API and cache fail, app shows an error message

## Customization

**Change data range:**
```python
# In load_data() function, modify:
twelve_months_ago = (datetime.now() - timedelta(days=365))  # Change 365 to desired days
```

**Adjust cache TTL:**
```python
@st.cache_data(ttl=3600)  # Change 3600 to desired seconds
```

**Filter at API level:**
```python
# Add additional filters to the $where clause in load_data()
params = {
    "$where": f"processed_date >= '{twelve_months_ago}' AND neighborhood = 'Downtown'",
    ...
}
```

## Project Structure

```
PermitTrack/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── permits_cache.json        # Auto-generated cache (ignored in git)
└── README.md                 # This file
```

## Key Metrics Explained

- **Avg days to issue:** Average time from permit filed to permit issued (only for permits that have been issued)
- **30-day momentum:** Percent change comparing last 30 days vs. prior 30 days
- **Valuation tiers:** Small (<$50K), Mid ($50K–$500K), Large (>$500K)

## Disclaimer

Data sourced from the City of Orlando. The City does not guarantee accuracy.
See full disclaimer in the app footer.
