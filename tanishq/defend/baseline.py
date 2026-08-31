import pandas as pd

from xgboost import XGBClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


class XGBoostBaseline:

    def __init__(self):

        self.feature_columns = [
            "new_device",
            "new_beneficiary",
            "amount_deviation",
            "velocity_deviation",
            "location_change",
            "time_deviation"
        ]

        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42
        )

        self.is_trained = False

    def train(self, dataframe):

        X = dataframe[self.feature_columns]
        y = dataframe["label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )

        print("\nTraining XGBoost...")

        self.model.fit(
            X_train,
            y_train
        )

        self.is_trained = True

        predictions = self.model.predict(X_test)

        probabilities = self.model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(
                y_test,
                predictions
            ),

            "precision": precision_score(
                y_test,
                predictions,
                zero_division=0
            ),

            "recall": recall_score(
                y_test,
                predictions,
                zero_division=0
            ),

            "f1": f1_score(
                y_test,
                predictions,
                zero_division=0
            )
        }

        return {
            "X_test": X_test,
            "y_test": y_test,
            "predictions": predictions,
            "probabilities": probabilities,
            "metrics": metrics
        }

    def predict(self, dataframe):

        if not self.is_trained:
            raise RuntimeError(
                "Model must be trained before prediction."
            )

        X = dataframe[self.feature_columns]

        probabilities = self.model.predict_proba(X)[:, 1]

        predictions = (
            probabilities >= 0.5
        ).astype(int)

        return pd.DataFrame({
            "ato_probability": probabilities,
            "prediction": predictions
        })

    def feature_importance(self):

        if not self.is_trained:
            raise RuntimeError(
                "Model must be trained first."
            )

        return pd.DataFrame({
            "feature": self.feature_columns,
            "importance": self.model.feature_importances_
        }).sort_values(
            "importance",
            ascending=False
        )