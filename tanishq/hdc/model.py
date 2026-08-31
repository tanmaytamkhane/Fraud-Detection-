"""
HDC Fraud Classifier Model.
"""
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HDC_DIMENSIONS, HDC_LEARNING_RATE

class HDCClassifier:
    def __init__(self, dim=HDC_DIMENSIONS, num_classes=2, learning_rate=HDC_LEARNING_RATE):
        self.dim = dim
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        # Class prototypes: one hypervector per class
        # class 0 = legitimate, class 1 = fraud
        self.prototypes = np.zeros((num_classes, dim), dtype=np.float32)
        self.threshold = 0.0  # Decision threshold margin: score[1] - score[0] > threshold
        self.is_trained = False
    
    def initial_train(self, encoded_hvs, labels):
        """Initial training: bundle all vectors per class to create prototypes.
        
        Args:
            encoded_hvs: shape (n_samples, dim) — encoded transaction hypervectors
            labels: shape (n_samples,) — 0 or 1
        """
        for c in range(self.num_classes):
            class_mask = labels == c
            if class_mask.sum() > 0:
                self.prototypes[c] = np.sum(encoded_hvs[class_mask], axis=0)
        self.is_trained = True
    
    def _compute_cosine_similarities(self, encoded_hvs):
        """Vectorized cosine similarity against both class prototypes."""
        proto_norms = np.linalg.norm(self.prototypes, axis=1, keepdims=True)
        proto_norms = np.maximum(proto_norms, 1e-10)
        normalized_protos = self.prototypes / proto_norms
        
        hv_norms = np.linalg.norm(encoded_hvs, axis=1, keepdims=True)
        hv_norms = np.maximum(hv_norms, 1e-10)
        normalized_hvs = encoded_hvs / hv_norms
        
        # (n_samples, num_classes)
        return normalized_hvs @ normalized_protos.T
    
    def predict_batch(self, encoded_hvs, threshold=None):
        """Predict classes for a batch. Returns (predictions, similarity_scores)."""
        scores = self._compute_cosine_similarities(encoded_hvs)
        t = self.threshold if threshold is None else threshold
        
        # Binary prediction using threshold on similarity difference (fraud - legit)
        diff = scores[:, 1] - scores[:, 0]
        predictions = (diff > t).astype(np.int32)
        
        return predictions, scores
    
    def calibrate_threshold(self, encoded_hvs, labels, metric='f1'):
        """Finds the optimal decision threshold on training data."""
        scores = self._compute_cosine_similarities(encoded_hvs)
        diffs = scores[:, 1] - scores[:, 0]
        
        # Search over candidate thresholds from min to max diff
        candidates = np.linspace(np.percentile(diffs, 1), np.percentile(diffs, 99), 100)
        best_thresh = 0.0
        best_score = -1.0
        
        for c in candidates:
            preds = (diffs > c).astype(np.int32)
            tp = np.sum((labels == 1) & (preds == 1))
            fp = np.sum((labels == 0) & (preds == 1))
            fn = np.sum((labels == 1) & (preds == 0))
            
            if metric == 'f1':
                prec = tp / max(tp + fp, 1)
                rec = tp / max(tp + fn, 1)
                score = (2 * prec * rec) / max(prec + rec, 1e-6)
            else:
                tn = np.sum((labels == 0) & (preds == 0))
                score = 0.5 * (tp / max(tp + fn, 1) + tn / max(tn + fp, 1))
                
            if score > best_score:
                best_score = score
                best_thresh = c
                
        self.threshold = float(best_thresh)
        return self.threshold
    
    def retrain_step(self, encoded_hvs, labels):
        """One retraining step: for each misclassified sample, 
        subtract from wrong prototype and add to correct prototype.
        Returns number of misclassifications.
        """
        predictions, _ = self.predict_batch(encoded_hvs, threshold=0.0)
        misclassified = predictions != labels
        num_errors = misclassified.sum()
        
        for i in np.where(misclassified)[0]:
            correct_class = labels[i]
            wrong_class = predictions[i]
            # Move correct prototype closer
            self.prototypes[correct_class] += self.learning_rate * encoded_hvs[i]
            # Move wrong prototype away
            self.prototypes[wrong_class] -= self.learning_rate * encoded_hvs[i]
        
        return num_errors
    
    def get_fraud_score(self, encoded_hvs):
        """Get fraud probability score for each transaction.
        Returns continuous values scaled in [0, 1] for AUC-ROC calculation."""
        scores = self._compute_cosine_similarities(encoded_hvs)
        diff = scores[:, 1] - scores[:, 0]
        # Sigmoid scaling around threshold
        return 1.0 / (1.0 + np.exp(-15.0 * (diff - self.threshold)))

if __name__ == '__main__':
    print("Testing HDC Classifier...")
    model = HDCClassifier(dim=1000, num_classes=2)
    n_samples = 100
    hvs = np.random.choice([-1, 1], size=(n_samples, 1000)).astype(np.float32)
    labels = np.random.randint(0, 2, size=n_samples)
    model.initial_train(hvs, labels)
    preds, scores = model.predict_batch(hvs)
    print(f"Accuracy on training set after initial train: {(preds == labels).mean():.4f}")
