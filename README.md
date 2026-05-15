# CyberNova Analytics

Enterprise-grade Web Log Analytics Platform built with Streamlit, Pandas, and Plotly, designed for CET333 Product Development.

## Overview

CyberNova Analytics processes up to 500,000 synthetic IIS web server logs to provide role-based business intelligence dashboards. It features a modern 2026 SaaS design system (dark mode glassmorphism) and satisfies 22 functional requirements.

## Key Features
- **3 Role-Based Dashboards**: Website User, Business Analyst, System Administrator.
- **Advanced Analytics**: Conversion funnels, campaign ROI, geographic choropleth maps, and statistical distributions.
- **Data Ingestion**: Processes 500K records from Parquet files with built-in data cleaning pipelines (duplicate removal, null handling).
- **Export Capabilities**: Download filtered views to CSV or Excel.
- **Modern UI**: Streamlit application wrapped in a custom dark glassmorphism CSS theme with responsive metrics and charts.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database & Seed Users**:
   ```bash
   python scripts/init_db.py
   ```
   This creates the SQLite database and seeds three default users:
   - `admin@cybernova.com` (Admin@2026!)
   - `analyst@cybernova.com` (Analyst@2026!)
   - `user@cybernova.com` (User@2026!)

3. **Provide Data**:
   Place your existing 500K records Parquet file at `data/raw/web_logs.parquet`. If you don't have one, run `python scripts/seed_data.py` to generate it.

4. **Run Application**:
   ```bash
   streamlit run app.py
   ```
   py -m streamlit run app.py
