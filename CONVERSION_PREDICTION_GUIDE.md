# 🤖 Conversion Prediction Model: Technical Specification

## 🎯 Overview
The **AI Conversion Prediction Model** extends the CyberNova Analytics platform from descriptive business intelligence (reporting on what happened) to **predictive analytics** (estimating what will happen). By analyzing historical patterns in Southern African digital leads, the model predicts the likelihood of a user converting *before* the conversion actually occurs.

---

## 📌 Business Use Case
For CyberNova Analytics Ltd (Gaborone HQ), this model serves three primary functions:
1. **Lead Prioritization:** Identify high-probability prospects for immediate follow-up by the sales team.
2. **Strategy Optimization:** Analyze which behavioral patterns (e.g., AI Assistant usage) are strongest predictors of success.
3. **Risk Mitigation:** Identify users with low conversion probability despite high activity, signaling a need for intervention or UX adjustments.

---

## ⚙️ System Architecture & Data Flow

### 1. Feature Engineering (The Input)
The system extracts specific "signals" from the `web_logs` table:
*   **Behavioral Features:** Total page views, session duration, and frequency of specific activities (e.g., `CLICK_AI_ASSISTANT`, `REQUEST_DEMO`).
*   **Contextual Features:** Geographic location (e.g., Gaborone vs. Johannesburg), device type, and campaign source.
*   **Performance Features:** Average server response time and HTTP success rates.

### 2. The Model (The Brain)
*   **Algorithm:** Supervised Learning (Logistic Regression or Random Forest).
*   **Target Variable:** `conversion_flag` (Binary: 0 for no conversion, 1 for success).
*   **Training Process:** The model is trained on historical Parquet/SQLite data, learning the weights of different features (e.g., a "Demo Request" might increase probability by 60%).

### 3. Real-Time Integration (The Flow)
1.  **Interaction:** A user interacts with the CyberNova dashboard or website.
2.  **Log Generation:** Interactions are streamed into the `web_logs` database via the `LiveEngine`.
3.  **Prediction Engine:** A background service retrieves the most recent session data and feeds it into the trained model.
4.  **Output:** The model generates a **Probability Score** (0.0 to 1.0).
5.  **Dashboard Display:** The Analyst Dashboard visualizes these scores in the "AI Prediction Panel."

---

## 📊 Dashboard Implementation

### 🛡 Analyst Dashboard: AI Prediction Panel
*   **High-Probability Leads:** A list of active users with a >75% conversion likelihood.
*   **Conversion Drivers:** A chart showing which factors (e.g., "Response Time" or "Job Type") are currently impacting predictions most.
*   **Probability Distribution:** A histogram showing the spread of conversion scores across the current user base.

---

## 📝 Implementation Statement
> "The system integrates a supervised machine learning model to predict user conversion likelihood based on historical IIS log data. The model analyses behavioural patterns such as page views, session activity, campaign source, and response time to estimate the probability of conversion. This enhances the system from descriptive analytics to predictive analytics, enabling proactive business decision-making."

---

## 🚀 Technical Requirements
*   **Library:** `scikit-learn` for model training and inference.
*   **Backend:** `backend/analytics/prediction_model.py` for model logic.
*   **Frontend:** `pages/02_Analyst_Dashboard.py` for visualization.
