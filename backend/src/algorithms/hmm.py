from typing import Any, Dict, Optional
from hmmlearn.hmm import GaussianHMM
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ParameterGrid
import os
import joblib
import numpy as np
import pandas as pd

from algorithms.algorithm import Algorithm
from errors.base_exception import BacktesterError

class HMMRegimeModel(Algorithm):

    def __init__(self, modelPath: str = "models/hmm_model.joblib", randomState: int = 42):
        self.name = "hmm"
        self.isFitted = False
        self.model = None
        self.modelPath = modelPath
        self.randomState = randomState
        self.bestParams = {}

        self.loadModel()

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None, optimize: bool = True):
        """Train or optimize the model."""
        if optimize:
            self.model, self.bestParams = self.gridSearch(X)

        else:
            self.model.fit(X)
        
        self.isFitted = True
        self.saveModel()

    def predict(self, X):
        """Return the regime state with highest probability."""
        if not self.isFitted:
            raise BacktesterError("algorithm/model-not-fitted")
        return self.model.predict(X)
    
    def predictProba(self, X):
        """Return the probabilities for each regime state."""
        if not self.isFitted:
            raise BacktesterError("algorithm/model-not-fitted")
        return self.model.predict_proba(X)
    
    def gridSearch(self, X):
        """Perform grid search for hyperparameter optimization."""
        param_grid = {
            "n_components": [3, 4, 5],
            "covariance_type": ["diag", "full"],
            "validation_size": [0.1, 0.2, 0.3]
        }

        bestScore = -np.inf
        bestModel = None
        bestParams = None

        for param in ParameterGrid(param_grid):

            n = len(X)
            valIdx = int(n * (1 - param["validation_size"]))
            X_train, X_val = X[:valIdx], X[valIdx:]
            
            model = GaussianHMM(
                n_components = param["n_components"],
                covariance_type = param["covariance_type"],
                n_iter = 1000,
                random_state = self.randomState
            )

            pipeline = Pipeline(steps= [("scaler", StandardScaler()), ("model", model)])

            pipeline.fit(X_train)
            score = pipeline.score(X_val)

            if score > bestScore:
                bestScore = score
                bestModel = pipeline
                bestParams = param
            
            print(f"Best parameters: {bestParams}, Best validation log-likelihood: {bestScore}")

        return bestModel, bestParams
    
    def loadModel(self): 
        """Load the model from the model path if exist, else initialize the model with default hyperparameters."""
        if os.path.exists(self.modelPath):
            self.model = joblib.load(self.modelPath)
        else:
            self.model = Pipeline(steps=[
                ("scaler", StandardScaler()),
                ("model", GaussianHMM(
                    n_components=5, 
                    covariance_type="full", 
                    n_iter=1000, 
                    random_state=self.randomState
                    ))]
            )
                
    def saveModel(self):
        """Save the model to the path given."""
        os.makedirs(os.path.dirname(self.modelPath), exist_ok=True)
        joblib.dump(self.model, self.modelPath)
        print(f"[INFO] HMM model saved to {self.modelPath}")