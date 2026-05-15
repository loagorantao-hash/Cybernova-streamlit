# Cybernova Analytics: KPI & Dataset Reference

This document provides a detailed explanation of the Key Performance Indicators (KPIs) displayed on the CyberNova dashboards and how they map to the underlying 500,000-record dataset.

## 📊 Summary Metrics (Core KPIs)

| KPI Name | Dataset Field | Description | Calculation |
| :--- | :--- | :--- | :--- |
| **Total Records** | `timestamp` | Total volume of traffic/logs processed. | `COUNT(*)` |
| **Unique Users** | `user_id` | Number of distinct individuals interacting with the platform. | `COUNT(DISTINCT user_id)` |
| **Total Revenue** | `revenue_value` | Cumulative financial value generated from conversions. | `SUM(revenue_value)` |
| **Total Leads** | `lead_flag` | Users who showed significant interest (e.g., demo request). | `SUM(lead_flag)` |
| **Conversions** | `conversion_flag` | Successful transactions or goal completions. | `SUM(conversion_flag)` |
| **Conversion Rate** | Mixed | Percentage of total visits that resulted in a conversion. | `(Conversions / Total Records) * 100` |
| **Avg Response Time** | `response_time_ms` | Server performance metric; average time to handle requests. | `AVG(response_time_ms)` |
| **Total Errors** | `http_status` | Count of failed requests (Client or Server errors). | `COUNT(http_status >= 400)` |
| **Error Rate** | Mixed | Reliability metric; percentage of failed requests. | `(Errors / Total Records) * 100` |

---

## 📈 Analytical Modules

### 1. Product/Service Performance
*   **Service Usage Frequency:** Measures which services (e.g., "Real-time Threat Detection") are most popular based on the `service_name` field.
*   **Revenue by Service:** Identifies which specific services are driving the highest financial value.

### 2. Sales Effectiveness
*   **Sales Funnel:** Visualizes the journey from **Total Visitors** → **Leads** (`lead_flag=True`) → **Converted** (`conversion_flag=True`).
*   **Demo Conversion Ratio:** Specifically measures how many users who performed a "DEMO_REQUEST" (`activity_type`) eventually converted.

### 3. Marketing Effectiveness
*   **Campaign Performance:** Evaluates traffic and revenue grouped by `campaign_type` (e.g., Email, Social, Referral).
*   **Visits Over Time:** A time-series analysis of traffic volume using the `timestamp` field to identify peak usage periods.

### 4. Geographic Analysis
*   **Global Distribution:** Uses the `location` field (Cities like Dubai, London, New York) mapped to ISO country codes to show where traffic originates globally.

---

## 📂 Dataset Field Definitions (CSV)

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `timestamp` | DateTime | The exact moment the log entry was recorded. |
| `user_id` | String | Unique identifier for a specific user (e.g., `USER_4642`). |
| `activity_type` | String | The nature of the action (LOGIN, PAGE_VIEW, DEMO_REQUEST). |
| `service_name` | String | The specific product or feature the user interacted with. |
| `http_status` | Integer | Standard web status codes (200 = Success, 404 = Not Found, 500 = Error). |
| `response_time_ms`| Integer | Server latency in milliseconds. |
| `location` | String | The geographic origin of the request (City/Region). |
| `campaign_type` | String | The marketing channel that brought the user to the site. |
| `lead_flag` | Boolean | `True` if the user is considered a potential sale/lead. |
| `conversion_flag` | Boolean | `True` if the user completed a high-value action (e.g., purchase). |
| `revenue_value` | Float | The dollar amount associated with a conversion. |

---
**Note:** All KPIs are calculated in real-time using high-performance SQL queries directly against the SQLite database to ensure the dashboard remains responsive even with 500,000+ records.
