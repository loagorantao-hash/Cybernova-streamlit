import pandas as pd
import numpy as np
try:
    from sklearn.linear_model import LogisticRegression
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
from backend.database.queries import get_dataframe
import pickle
import os

class PredictionEngine:
    def __init__(self, model_path="data/models/conversion_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_columns = [
            'page_views', 'session_duration_s', 'has_demo_request', 
            'has_ai_interaction', 'avg_response_time', 'is_gaborone_hq'
        ]
        
        if not os.path.exists("data/models"):
            os.makedirs("data/models")
            
        self.load_model()

    def load_model(self):
        """Load model from disk or train a synthetic one if missing."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
            except:
                self.train_initial_model()
        else:
            self.train_initial_model()

    def train_initial_model(self):
        """Train a baseline model with synthetic data or actual DB data."""
        if not HAS_SKLEARN:
            print("Warning: scikit-learn not found. Skipping model training.")
            return

        # For the prototype, we'll create a baseline model that weights 
        # 'demo_request' and 'ai_interaction' highly.
        X = np.array([
            [1, 10, 0, 0, 200, 1],
            [10, 600, 1, 1, 150, 1],
            [5, 300, 0, 1, 400, 0],
            [2, 50, 0, 0, 800, 0],
            [15, 1200, 1, 0, 100, 1]
        ])
        y = np.array([0, 1, 0, 0, 1])
        
        self.model = LogisticRegression()
        self.model.fit(X, y)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)

    def get_features_for_session(self, session_id):
        """Extract features for a specific session from the DB."""
        query = f"""
            SELECT 
                COUNT(*) as page_views,
                (MAX(timestamp) - MIN(timestamp)) as session_duration_s,
                SUM(CASE WHEN activity_type = 'REQUEST_DEMO' THEN 1 ELSE 0 END) as has_demo_request,
                SUM(CASE WHEN activity_type = 'CLICK_AI_ASSISTANT' THEN 1 ELSE 0 END) as has_ai_interaction,
                AVG(response_time_ms) as avg_response_time,
                SUM(CASE WHEN location = 'Gaborone' THEN 1 ELSE 0 END) as is_gaborone_hq
            FROM web_logs
            WHERE session_id = '{session_id}'
        """
        df = get_dataframe(query)
        if df.empty:
            return None
            
        # Ensure binary flags
        df['has_demo_request'] = df['has_demo_request'].apply(lambda x: 1 if x > 0 else 0)
        df['has_ai_interaction'] = df['has_ai_interaction'].apply(lambda x: 1 if x > 0 else 0)
        df['is_gaborone_hq'] = df['is_gaborone_hq'].apply(lambda x: 1 if x > 0 else 0)
        
        return df[self.feature_columns].values

    def predict_conversion(self, session_id):
        """Predict probability of conversion for a session."""
        if not HAS_SKLEARN or self.model is None:
            return 0.5 # Return neutral probability if AI is offline
            
        features = self.get_features_for_session(session_id)
        if features is None:
            return 0.0
            
        prob = self.model.predict_proba(features)[0][1]
        return float(prob)

    def get_top_predicted_leads(self, limit=10):
        """Get sessions with high predicted probability that haven't converted yet."""
        # Note: In a real system, we'd iterate sessions. For the demo, we'll sample.
        query = """
            SELECT DISTINCT session_id, user_id, location, campaign_type
            FROM web_logs 
            WHERE conversion_flag = 0
            LIMIT 50
        """
        df = get_dataframe(query)
        if df.empty:
            return pd.DataFrame()
            
        results = []
        for _, row in df.iterrows():
            prob = self.predict_conversion(row['session_id'])
            results.append({
                'user_id': row['user_id'],
                'session_id': row['session_id'],
                'location': row['location'],
                'campaign': row['campaign_type'],
                'probability': prob
            })
            
        res_df = pd.DataFrame(results).sort_values('probability', ascending=False)
        return res_df.head(limit)
