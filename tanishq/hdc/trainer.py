"""
HDC Training Pipeline — Robust, Leakage-Free Implementation.
"""
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import HDC_RETRAIN_EPOCHS, FRAUD_OVERSAMPLE_RATIO, RANDOM_STATE
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier

class HDCTrainer:
    def __init__(self, encoder=None, classifier=None):
        self.encoder = encoder or HDCEncoder()
        self.classifier = classifier or HDCClassifier()
    
    def _oversample_fraud(self, X, y):
        """Oversample fraud class dynamically based on class imbalance in the training set."""
        fraud_mask = (y == 1)
        legit_mask = (y == 0)
        n_fraud = int(fraud_mask.sum())
        n_legit = int(legit_mask.sum())
        
        if n_fraud == 0 or n_legit == 0:
            return X, y
            
        fraud_ratio = n_fraud / len(y)
        # If fraud is already > 25%, no duplication needed
        if fraud_ratio >= 0.25:
            return X, y
            
        # Target ~20% fraud in training set
        target_fraud_count = int(n_legit * 0.25)
        needed = target_fraud_count - n_fraud
        num_copies = max(1, needed // n_fraud)
        
        fraud_X = X[fraud_mask]
        fraud_y = y[fraud_mask]
        
        X_oversampled = np.vstack([X] + [fraud_X] * num_copies)
        y_oversampled = np.concatenate([y] + [fraud_y] * num_copies)
        
        rng = np.random.RandomState(RANDOM_STATE)
        shuffle_idx = rng.permutation(len(y_oversampled))
        return X_oversampled[shuffle_idx], y_oversampled[shuffle_idx]
    
    def train(self, signal_matrix, labels, val_signals=None, val_labels=None, retrain_epochs=None, epochs=None, **kwargs):
        """Full training pipeline with strict validation-based threshold calibration.
        
        Args:
            signal_matrix: shape (n_train, n_signals) — training signal matrix
            labels: shape (n_train,) — training labels (0 or 1)
            val_signals: optional shape (n_val, n_signals) — validation signals for threshold calibration
            val_labels: optional shape (n_val,) — validation labels
            retrain_epochs: number of retraining iterations
        """
        if retrain_epochs is None:
            retrain_epochs = epochs if epochs is not None else HDC_RETRAIN_EPOCHS
            
        print(f'  Encoding {len(labels):,} training transactions into hypervectors...')
        encoded_train = self.encoder.encode_batch(signal_matrix)
        
        print(f'  Oversampling fraud class on training data...')
        encoded_os, labels_os = self._oversample_fraud(encoded_train, labels)
        print(f'  After oversampling: {len(labels_os):,} samples (fraud: {(labels_os==1).sum():,}, legit: {(labels_os==0).sum():,})')
        
        print(f'  Initial prototype bundling...')
        self.classifier.initial_train(encoded_os, labels_os)
        
        preds, _ = self.classifier.predict_batch(encoded_train)
        initial_acc = (preds == labels).mean()
        initial_recall = (preds[labels==1] == 1).mean() if (labels==1).sum() > 0 else 0
        initial_precision = (labels[preds==1] == 1).mean() if (preds==1).sum() > 0 else 0
        
        history = {
            'accuracy': [initial_acc],
            'recall': [initial_recall],
            'precision': [initial_precision],
            'errors': []
        }
        
        print(f'  Retraining for {retrain_epochs} epochs...')
        for epoch in range(retrain_epochs):
            errors = self.classifier.retrain_step(encoded_os, labels_os)
            
            # Evaluate on un-oversampled training set
            preds, _ = self.classifier.predict_batch(encoded_train)
            acc = (preds == labels).mean()
            recall = (preds[labels==1] == 1).mean() if (labels==1).sum() > 0 else 0
            precision = (labels[preds==1] == 1).mean() if (preds==1).sum() > 0 else 0
            
            history['accuracy'].append(acc)
            history['recall'].append(recall)
            history['precision'].append(precision)
            history['errors'].append(errors)
            
            if (epoch + 1) % 5 == 0 or epoch == 0:
                print(f'  Epoch {epoch+1:3d}/{retrain_epochs} — Errors: {errors:,}, Acc: {acc:.4f}, Recall: {recall:.4f}, Precision: {precision:.4f}')
        
        # Decision threshold calibration on VALIDATION set if provided (preventing leakage)
        if val_signals is not None and val_labels is not None:
            print(f'  Calibrating decision threshold on VALIDATION set ({len(val_labels):,} samples)...')
            encoded_val = self.encoder.encode_batch(val_signals)
            thresh = self.classifier.calibrate_threshold(encoded_val, val_labels)
        else:
            print(f'  Calibrating decision threshold on training set (no val set provided)...')
            thresh = self.classifier.calibrate_threshold(encoded_train, labels)
            
        print(f'  Optimal decision threshold calibrated to: {thresh:.6f}')
        print(f'  Training complete!')
        return history
