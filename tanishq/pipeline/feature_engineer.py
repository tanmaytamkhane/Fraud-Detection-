import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    DEVICE_RISK_WEIGHTS, ADDRESS_MISMATCH_WEIGHTS, AMOUNT_ZSCORE_CAP,
    VELOCITY_MEDIAN_FRAUD, VELOCITY_MEDIAN_LEGIT, NIGHT_HOURS,
    PRODUCT_FRAUD_RATES, SIGNAL_NAMES
)

def compute_device_risk(df) -> pd.Series:
    """Computes device risk signal in [0, 1]."""
    has_identity = df['has_identity'].astype(int)
    
    device_type_mobile = df['DeviceType'].map({'mobile': 1, 'desktop': 0}).fillna(0.5)
    id_15_found = df['id_15'].map({'Found': 1, 'New': 0}).fillna(0.5)
    id_28_found = df['id_28'].map({'Found': 1, 'New': 0}).fillna(0.5)
    
    w_has_id = DEVICE_RISK_WEIGHTS.get('has_identity', 0.25)
    w_mobile = DEVICE_RISK_WEIGHTS.get('device_type_mobile', 0.25)
    w_id15 = DEVICE_RISK_WEIGHTS.get('id_15_found', 0.25)
    w_id28 = DEVICE_RISK_WEIGHTS.get('id_28_found', 0.25)
    
    score = (has_identity * w_has_id +
             device_type_mobile * w_mobile +
             id_15_found * w_id15 +
             id_28_found * w_id28)
    
    return score.clip(0, 1)

def compute_address_mismatch(df) -> pd.Series:
    """Computes address mismatch signal in [0, 1]."""
    M4_M2 = (df['M4'] == 'M2').astype(int)
    M5_T = (df['M5'] == 'T').astype(int)
    dist1_norm = (df['dist1'] / 1000).clip(upper=1.0).fillna(0)
    
    w_m4 = ADDRESS_MISMATCH_WEIGHTS.get('M4_M2', 0.33)
    w_m5 = ADDRESS_MISMATCH_WEIGHTS.get('M5_T', 0.33)
    w_dist1 = ADDRESS_MISMATCH_WEIGHTS.get('dist1_high', 0.34)
    
    score = (M4_M2 * w_m4 + M5_T * w_m5 + dist1_norm * w_dist1)
    return score.clip(0, 1)

def compute_amount_deviation(df) -> pd.Series:
    """Computes amount deviation signal in [0, 1]."""
    grouped = df.groupby('card1')['TransactionAmt']
    user_mean = grouped.transform('mean')
    user_std = grouped.transform('std').fillna(1).replace(0, 1)
    
    z_score = ((df['TransactionAmt'] - user_mean) / user_std).abs()
    z_score = z_score.clip(upper=AMOUNT_ZSCORE_CAP)
    return z_score / AMOUNT_ZSCORE_CAP

def compute_velocity(df) -> pd.Series:
    """Computes velocity signal in [0, 1]."""
    # Sort by TransactionDT within each card1
    df_sorted = df.sort_values(['card1', 'TransactionDT'])
    
    time_since_last = df_sorted.groupby('card1')['TransactionDT'].diff()
    
    # For first transaction of each card1, use median time gap
    median_gap = time_since_last.median()
    if pd.isna(median_gap):
        median_gap = 86400  # Fallback
        
    time_since_last = time_since_last.fillna(median_gap)
    
    velocity_score = 1 - (time_since_last / 86400).clip(upper=1.0)
    
    # Rank normalizations
    C1_norm = df_sorted['C1'].rank(pct=True).fillna(0.5)
    C13_norm = df_sorted['C13'].rank(pct=True).fillna(0.5)
    
    score = 0.5 * velocity_score + 0.25 * C1_norm + 0.25 * C13_norm
    
    # Realign index to original df
    score = score.reindex(df.index).fillna(0.5).clip(0, 1)
    return score

def compute_time_anomaly(df) -> pd.Series:
    """Computes time anomaly signal in [0, 1]."""
    hour = (df['TransactionDT'] % 86400) / 3600
    is_night = hour.apply(lambda x: 1 if 0 <= x < 6 else 0)
    
    user_mean_hour = df.groupby('card1')['TransactionDT'].transform(lambda x: ((x % 86400) / 3600).mean())
    hour_deviation = ((hour - user_mean_hour).abs() / 12.0).clip(upper=1.0)
    
    score = 0.5 * is_night + 0.5 * hour_deviation
    return score.clip(0, 1)

def compute_channel_risk(df) -> pd.Series:
    """Computes channel risk signal in [0, 1]."""
    max_fraud = 0.1169
    product_risk = df['ProductCD'].map(PRODUCT_FRAUD_RATES).fillna(0) / max_fraud
    
    email_risk = df['P_emaildomain'].apply(lambda x: 1 if x == 'anonymous.com' else (0.5 if pd.isna(x) else 0))
    
    card_type_risk = df['card6'].map({'credit': 0.3, 'debit': 0.7}).fillna(0.5)
    
    score = 0.5 * product_risk + 0.3 * email_risk + 0.2 * card_type_risk
    return score.clip(0, 1)

def engineer_features(df) -> pd.DataFrame:
    """Engineers all 6 fraud detection features and returns a DataFrame with signals."""
    print("Computing features...")
    device_risk = compute_device_risk(df)
    address_mismatch = compute_address_mismatch(df)
    amount_deviation = compute_amount_deviation(df)
    velocity = compute_velocity(df)
    time_anomaly = compute_time_anomaly(df)
    channel_risk = compute_channel_risk(df)
    
    out_cols = ['TransactionID']
    if 'isFraud' in df.columns:
        out_cols.append('isFraud')
        
    out_df = df[out_cols].copy()
    out_df['device_risk'] = device_risk
    out_df['address_mismatch'] = address_mismatch
    out_df['amount_deviation'] = amount_deviation
    out_df['velocity'] = velocity
    out_df['time_anomaly'] = time_anomaly
    out_df['channel_risk'] = channel_risk
    
    signals = ['device_risk', 'address_mismatch', 'amount_deviation', 'velocity', 'time_anomaly', 'channel_risk']
    
    print("Signal Statistics:")
    for sig in signals:
        print(f"{sig}: mean={out_df[sig].mean():.4f}, std={out_df[sig].std():.4f}, min={out_df[sig].min():.4f}, max={out_df[sig].max():.4f}")
        
    if 'isFraud' in out_df.columns:
        print("\nCorrelation with isFraud:")
        for sig in signals:
            corr = out_df['isFraud'].corr(out_df[sig])
            print(f"{sig}: {corr:.4f}")
            
    return out_df

if __name__ == '__main__':
    from pipeline.loader import load_data
    
    print("Loading a 10% sample for feature engineering...")
    df_sample = load_data(sample_frac=0.1)
    
    df_features = engineer_features(df_sample)
    
    print("\nResult shape:", df_features.shape)
    print("First 5 rows:")
    print(df_features.head())
