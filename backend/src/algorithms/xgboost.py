import os
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit

from algorithms.algorithm import Algorithm

class XGBModel(Algorithm):
    def __init__(self, model_path: str = "models/xgb_model.joblib", random_state: int = 42):
        self.name = "xgb"
        self.is_fitted = False
        self.model = None
        self.model_path = model_path
        self.random_state = random_state
        self.best_params = {}
        self.load_model()

    def fit(self, X: pd.DataFrame, y: pd.Series, optimize: bool = False):
        if optimize:
            self.model, self.best_params = self._optimize_param(X, y)
        else:
            self.model.fit(X, y)
        self.is_fitted = True
        self.save_model()

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        return self.model.predict_proba(X)

    def get_best_params(self) -> dict:
        return self.best_params

    def _optimize_param(self, X: pd.DataFrame, y: pd.Series) -> tuple:
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.05, 0.1],
            'subsample': [0.7, 1.0]
        }
        tscv = TimeSeriesSplit(n_splits=5)
        search = RandomizedSearchCV(
            estimator=XGBClassifier(
                objective='multi:softprob',
                num_class=3,
                eval_metric='mlogloss',
                random_state=self.random_state,
                n_estimators=100,
                max_depth = 7,
                learning_rate = 0.05,
                subsample = 0.7
            ),
            param_distributions=param_grid,
            n_iter=10,
            cv=tscv,
            scoring='f1_macro',
            verbose=1,
            n_jobs=-1,
            random_state=self.random_state
        )
        search.fit(X, y)
        return search.best_estimator_, search.best_params_

    def load_model(self):
        """Load the model from the specified path if it exists, else initialize a new one."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_fitted = True
        else:
            self.model = XGBClassifier(
                objective='multi:softprob',
                num_class=3,
                eval_metric='mlogloss',
                random_state=self.random_state,
                n_estimators=100,
                max_depth = 7,
                learning_rate = 0.05,
                subsample = 0.7
            )

    def save_model(self):
        """Save the trained model to the specified path."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"[INFO] XGBoost model saved to {self.model_path}")