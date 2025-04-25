import os
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import (
    ParameterGrid,
    RandomizedSearchCV,
    TimeSeriesSplit
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

class XGBModel:
    def __init__(self, model_path: str = "models/xgb_model.joblib", random_state: int = 42):
        self.name = "xgb"
        self.is_fitted = False
        self.model = None
        self.pipeline = None
        self.model_path = model_path
        self.random_state = random_state
        self.best_params = {}
        self.loadModel()
    
    def rolling_zscore(self, df: pd.DataFrame, window: int = 720) -> pd.DataFrame:
        """Apply rolling z-score for feature scaling."""
        return (df - df.rolling(window=window, min_periods=1).mean()) / \
               df.rolling(window=window, min_periods=1).std().replace(0, 1)  # Avoid division by zero
    
    def fit(self, X: pd.DataFrame, y: pd.Series, optimize: bool = False, apply_rolling_zscore: bool = True, window: int = 720):
        """
        Fit the model to the data.
        
        Args:
            X: Features DataFrame
            y: Target Series
            optimize: Whether to perform hyperparameter optimization
            apply_rolling_zscore: Whether to apply rolling z-score normalization
            window: Window size for rolling calculations
        """
        # Apply rolling z-score if requested
        if apply_rolling_zscore:
            X = self.rolling_zscore(X, window=window)
            # Handle any NaN values that might result from rolling operations
            X = X.fillna(0)
            # Make sure y is aligned with X after scaling
            y = y.loc[X.index]
            
        if optimize:
            self.pipeline, self.best_params = self._optimize_param(X, y)
        else:
            if self.pipeline is None:
                # Create a new pipeline with scaling and model
                xgb = XGBClassifier(
                    objective='multi:softmax',
                    num_class=3,
                    eval_metric='mlogloss',
                    random_state=self.random_state
                )
                self.pipeline = Pipeline(steps=[("scaler", StandardScaler()), ("model", xgb)])
            
            self.pipeline.fit(X, y)
        
        self.is_fitted = True
        self.saveModel()

    def predict(self, X: pd.DataFrame, apply_rolling_zscore: bool = True, window: int = 720) -> np.ndarray:
        """
        Make predictions on new data.
        
        Args:
            X: Features DataFrame
            apply_rolling_zscore: Whether to apply rolling z-score normalization
            window: Window size for rolling calculations
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
            
        # Apply rolling z-score if requested
        if apply_rolling_zscore:
            X = self.rolling_zscore(X, window=window)
            X = X.fillna(0)
            
        return self.pipeline.predict(X)
    
    def predict_proba(self, X: pd.DataFrame, apply_rolling_zscore: bool = True, window: int = 720) -> np.ndarray:
        """
        Get probability estimates for each class.
        
        Args:
            X: Features DataFrame
            apply_rolling_zscore: Whether to apply rolling z-score normalization
            window: Window size for rolling calculations
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
            
        # Apply rolling z-score if requested
        if apply_rolling_zscore:
            X = self.rolling_zscore(X, window=window)
            X = X.fillna(0)
            
        return self.pipeline.predict_proba(X)

    def get_best_params(self) -> dict:
        return self.best_params

    def _optimize_param(self, X: pd.DataFrame, y: pd.Series) -> tuple:
        """Optimize model parameters using time series cross-validation."""
        # Create the base classifier
        xgb = XGBClassifier(
            objective='multi:softmax',
            num_class=3,
            eval_metric='mlogloss',
            random_state=self.random_state
        )
        
        # Split data for validation
        n = len(X)
        val_idx = int(n * 0.7)  # 70% train, 30% validation
        X_train, X_val = X.iloc[:val_idx], X.iloc[val_idx:]
        y_train, y_val = y.iloc[:val_idx], y.iloc[val_idx:]

        # Create a pipeline with scaling and the classifier
        pipeline = Pipeline(steps=[("scaler", StandardScaler()), ("model", xgb)])
        
        # Set up parameter grid for the model
        param_grid = {
            'model__n_estimators': [50, 100, 200],
            'model__max_depth': [3, 5, 7],
            'model__learning_rate': [0.01, 0.05, 0.1],
            'model__subsample': [0.7, 1.0]
        }

        best_score = -np.inf
        best_model = None
        best_params = None

        for params in ParameterGrid(param_grid):
            # Create a pipeline with current params
            current_model = XGBClassifier(
                objective='multi:softmax',
                num_class=3,
                eval_metric='mlogloss',
                random_state=self.random_state,
                n_estimators=params['model__n_estimators'],
                max_depth=params['model__max_depth'],
                learning_rate=params['model__learning_rate'],
                subsample=params['model__subsample']
            )
            
            current_pipeline = Pipeline(steps=[("scaler", StandardScaler()), ("model", current_model)])
            
            # Fit the pipeline
            current_pipeline.fit(X_train, y_train)
            
            # Calculate score on validation set
            # Use log loss for classification problems
          
            y_pred = current_pipeline.predict(X_val)
            score = f1_score(y_val, y_pred, average='macro')
            
            # Extract clean params for printing
            clean_params = {k.replace('model__', ''): v for k, v in params.items()}
            print(f"Params: {clean_params}, Score: {score:.4f}")
            
            if score > best_score:
                best_score = score
                best_model = current_pipeline
                best_params = clean_params
        
        print(f"Best parameters: {best_params}, Best validation F1 score: {best_score:.4f}")

        return best_model, best_params

    def loadModel(self): 
        if os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
            self.is_fitted = True
        else:
            # Create a new pipeline with scaling and model
            xgb = XGBClassifier(
                objective='multi:softmax',
                num_class=3,
                eval_metric='mlogloss',
                random_state=self.random_state
            )
            self.is_fitted = False

    def saveModel(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
        print(f"[INFO] XGBoost pipeline saved to {self.model_path}")