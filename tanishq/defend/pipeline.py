from defend.features import FeatureEngine
from defend.behaviour import BehaviourEngine
from defend.baseline import XGBoostBaseline
from defend.anomaly import AnomalyDetector
from defend.risk_engine import RiskEngine
from defend.adaptive_memory import AdaptiveMemory
from defend.explain import ExplanationEngine

from tests.generate_training_data import generate_dataset


class DetectionPipeline:
    """
    Main P3 detection pipeline.

    Flow:

    Raw transactions
        ↓
    Feature extraction
        ↓
    Behaviour analysis
        ↓
    XGBoost
        ↓
    Anomaly detection
        ↓
    Risk fusion
        ↓
    Adaptive memory
        ↓
    Explanation
    """

    def __init__(self, user_profiles):

        self.feature_engine = FeatureEngine(
            user_profiles
        )

        self.behaviour_engine = BehaviourEngine()

        self.xgb = XGBoostBaseline()

        self.anomaly_detector = AnomalyDetector()

        self.risk_engine = RiskEngine()

        self.memory = AdaptiveMemory()

        self.explanation_engine = ExplanationEngine()

    def train(self):
        """
        Train the XGBoost and anomaly detection models.
        """

        training_data = generate_dataset()

        # Train XGBoost
        self.xgb.train(training_data)

        # Train anomaly detector
        self.anomaly_detector.fit(training_data)

    def process(self, transactions):
        """
        Process transactions through the complete
        P3 detection pipeline.

        Returns:
            list of risk result dictionaries
        """

        # --------------------------------------------------
        # 1. Feature extraction
        # --------------------------------------------------

        features = self.feature_engine.transform(
            transactions
        )

        # --------------------------------------------------
        # 2. Behaviour analysis
        # --------------------------------------------------

        behaviour_results = (
            self.behaviour_engine.analyze_dataframe(
                features
            )
        )

        # --------------------------------------------------
        # 3. XGBoost predictions
        # --------------------------------------------------

        xgb_predictions = self.xgb.predict(
            features
        )

        # --------------------------------------------------
        # 4. Anomaly scores
        # --------------------------------------------------

        anomaly_results = self.anomaly_detector.analyze(
            features
        )

        # --------------------------------------------------
        # 5. Risk fusion
        # --------------------------------------------------

        risk_results = []

        for i in range(len(features)):

            risk = self.risk_engine.evaluate(

                transaction_id=features.iloc[i][
                    "transaction_id"
                ],

                xgb_probability=xgb_predictions.iloc[i][
                    "ato_probability"
                ],

                behaviour_score=behaviour_results.iloc[i][
                    "behaviour_score"
                ],

                anomaly_score=anomaly_results.iloc[i][
                    "anomaly_score"
                ]
            )

            risk_results.append(risk)

        # --------------------------------------------------
        # 6. Adaptive memory
        # --------------------------------------------------

        for i, result in enumerate(risk_results):

            feature_dict = features.iloc[i].to_dict()

            self.memory.store(

                transaction_id=result[
                    "transaction_id"
                ],

                features=feature_dict,

                risk_score=result[
                    "risk_score"
                ],

                decision=result[
                    "decision"
                ]
            )

        return risk_results

    def explain(self, transactions, risk_results):
        """
        Generate explanations for processed transactions.

        Returns:
            list of explanation strings
        """

        features = self.feature_engine.transform(
            transactions
        )

        explanations = []

        for i, result in enumerate(risk_results):

            feature_dict = features.iloc[i].to_dict()

            explanation = (
                self.explanation_engine.generate_text(

                    transaction_id=result[
                        "transaction_id"
                    ],

                    features=feature_dict,

                    xgb_probability=result[
                        "xgb_probability"
                    ],

                    behaviour_score=result[
                        "behaviour_score"
                    ],

                    anomaly_score=result[
                        "anomaly_score"
                    ],

                    risk_score=result[
                        "risk_score"
                    ],

                    risk_level=result[
                        "risk_level"
                    ],

                    decision=result[
                        "decision"
                    ]
                )
            )

            explanations.append(
                explanation
            )

        return explanations