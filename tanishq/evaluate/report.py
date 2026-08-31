"""
Results report generation.
"""
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluate.metrics import classification_report, auc_roc

try:
    from config import SIGNAL_NAMES
except ImportError:
    # Fallback if config is not available during standalone testing
    SIGNAL_NAMES = [f"Signal_{i}" for i in range(6)]

def generate_report(y_true, y_pred, scores=None, signal_matrix=None, labels=None):
    """
    Generate a human-readable results report.
    
    Args:
        y_true (np.ndarray): True labels.
        y_pred (np.ndarray): Predicted labels.
        scores (np.ndarray, optional): Fraud scores.
        signal_matrix (np.ndarray, optional): Feature matrix (n_samples, n_signals).
        labels (np.ndarray, optional): Labels for signal analysis (usually same as y_true).
        
    Returns:
        dict: The metrics dict.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    n_samples = len(y_true)
    n_fraud = np.sum(y_true == 1)
    fraud_rate = (n_fraud / n_samples) * 100 if n_samples > 0 else 0
    
    print("\n" + "=" * 50)
    print("FRAUD DETECTION EVALUATION REPORT")
    print("=" * 50)
    
    print("\n[ Dataset Summary ]")
    print(f"Total Samples: {n_samples:,}")
    print(f"Fraud Cases:   {n_fraud:,}")
    print(f"Fraud Rate:    {fraud_rate:.2f}%")
    print()
    
    # Delegate to classification_report which prints and returns metrics
    metrics = classification_report(y_true, y_pred, scores)
    
    if signal_matrix is not None and labels is not None:
        print("\n[ Per-Signal Importance Analysis ]")
        signal_matrix = np.asarray(signal_matrix)
        labels = np.asarray(labels)
        
        fraud_mask = (labels == 1)
        legit_mask = (labels == 0)
        
        print(f"{'Signal Name':<20} | {'Fraud Mean':<12} | {'Legit Mean':<12}")
        print("-" * 50)
        
        n_features = signal_matrix.shape[1]
        for i in range(min(n_features, len(SIGNAL_NAMES))):
            s_name = SIGNAL_NAMES[i]
            
            f_mean = np.mean(signal_matrix[fraud_mask, i]) if np.any(fraud_mask) else 0.0
            l_mean = np.mean(signal_matrix[legit_mask, i]) if np.any(legit_mask) else 0.0
            
            print(f"{s_name:<20} | {f_mean:<12.4f} | {l_mean:<12.4f}")
            
    print("=" * 50 + "\n")
    return metrics

if __name__ == '__main__':
    print("Testing report generation...")
    y_t = np.array([0, 0, 0, 1, 1, 0, 1, 0, 0, 1])
    y_p = np.array([0, 0, 1, 1, 0, 0, 1, 0, 0, 1])
    s = np.array([0.1, 0.2, 0.6, 0.9, 0.4, 0.3, 0.8, 0.2, 0.1, 0.85])
    X = np.random.rand(10, 6)
    
    generate_report(y_t, y_p, s, X, y_t)
