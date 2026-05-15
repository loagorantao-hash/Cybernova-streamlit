# CyberNova Analytics Ltd — Gaborone HQ

Enterprise-grade AI-Driven Cybersecurity & Sales Intelligence Platform designed to monitor digital resilience across Southern Africa.

## Overview

CyberNova Analytics processes up to 500,000 synthetic IIS web server logs to provide role-based business intelligence for SMEs, financial institutions, and government agencies. It features a modern 2026 SaaS design system (dark mode glassmorphism) and evaluates sales strategy, AI Assistant adoption, and regional performance.

## Key Features
- **3 Role-Based Dashboards**: Website User (Client), Business Analyst (Sales Team), System Administrator.
- **Sales Strategy Assessment**: Evaluates team performance, conversion efficiency, and job placements across Southern Africa.
- **AI Assistant Tracking**: Dedicated metrics for AI Advisory interactions, Demo Requests, and Event Participation.
- **Advanced Analytics**: Conversion funnels, Response Time vs. Revenue scatterplots, geographic choropleth maps, and descriptive statistics (Mean, Std Dev).
- **Data Ingestion**: Processes 500K records with built-in data cleaning pipelines (duplicate removal, null handling).

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
