"""
Evaluation metrics for the fraud detection model.
"""
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

def confusion_matrix(y_true, y_pred):
    """
    Compute confusion matrix counts.
    
    Args:
        y_true (np.ndarray): True labels (0 or 1).
        y_pred (np.ndarray): Predicted labels (0 or 1).
        
    Returns:
        dict: tp, fp, tn, fn counts.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    
    return {'tp': int(tp), 'fp': int(fp), 'tn': int(tn), 'fn': int(fn)}

def precision(y_true, y_pred):
    """Compute precision."""
    cm = confusion_matrix(y_true, y_pred)
    if cm['tp'] + cm['fp'] == 0:
        return 0.0
    return cm['tp'] / (cm['tp'] + cm['fp'])

def recall(y_true, y_pred):
    """Compute recall."""
    cm = confusion_matrix(y_true, y_pred)
    if cm['tp'] + cm['fn'] == 0:
        return 0.0
    return cm['tp'] / (cm['tp'] + cm['fn'])

def f1_score(y_true, y_pred):
    """Compute F1 score."""
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)

def accuracy(y_true, y_pred):
    """Compute overall accuracy."""
    cm = confusion_matrix(y_true, y_pred)
    total = cm['tp'] + cm['fp'] + cm['tn'] + cm['fn']
    if total == 0:
        return 0.0
    return (cm['tp'] + cm['tn']) / total

def auc_roc(y_true, scores):
    """
    Compute AUC-ROC manually using trapezoidal rule.
    
    Args:
        y_true (np.ndarray): True labels.
        scores (np.ndarray): Predicted scores (higher means more likely fraud).
        
    Returns:
        float: AUC-ROC score.
    """
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)
    
    if len(np.unique(y_true)) < 2:
        return np.nan
        
    # Sort by scores descending
    desc_score_indices = np.argsort(scores)[::-1]
    y_true_sorted = y_true[desc_score_indices]
    
    tpr_list = [0.0]
    fpr_list = [0.0]
    
    P = np.sum(y_true == 1)
    N = np.sum(y_true == 0)
    
    if P == 0 or N == 0:
        return np.nan
        
    tp = 0
    fp = 0
    
    for i in range(len(y_true_sorted)):
        if y_true_sorted[i] == 1:
            tp += 1
        else:
            fp += 1
            
        tpr_list.append(tp / P)
        fpr_list.append(fp / N)
            
    tpr_arr = np.array(tpr_list)
    fpr_arr = np.array(fpr_list)
    
    trapezoid_fn = getattr(np, "trapezoid", None) or np.trapz
    auc = trapezoid_fn(tpr_arr, fpr_arr)
    return float(auc)

def classification_report(y_true, y_pred, scores=None):
    """
    Generate and print a complete classification report.
    
    Args:
        y_true (np.ndarray): True labels.
        y_pred (np.ndarray): Predicted labels.
        scores (np.ndarray, optional): Predicted scores.
        
    Returns:
        dict: All computed metrics.
    """
    cm = confusion_matrix(y_true, y_pred)
    acc = accuracy(y_true, y_pred)
    prec = precision(y_true, y_pred)
    rec = recall(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    metrics = {
        'confusion_matrix': cm,
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1_score': f1
    }
    
    print("--- Classification Report ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("Confusion Matrix:")
    print(f"  TP: {cm['tp']:<6} FP: {cm['fp']:<6}")
    print(f"  FN: {cm['fn']:<6} TN: {cm['tn']:<6}")
    
    if scores is not None:
        auc = auc_roc(y_true, scores)
        metrics['auc_roc'] = auc
        print(f"AUC-ROC:   {auc:.4f}")
        
    print("-----------------------------")
    
    return metrics

if __name__ == '__main__':
    print("Testing metrics...")
    y_t = np.array([0, 0, 1, 1, 0, 1])
    y_p = np.array([0, 1, 1, 0, 0, 1])
    s = np.array([0.1, 0.8, 0.9, 0.4, 0.2, 0.85])
    
    report = classification_report(y_t, y_p, s)
