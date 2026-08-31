import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    TRAIN_TRANSACTION, TRAIN_IDENTITY,
    TEST_TRANSACTION, TEST_IDENTITY,
    TRANSACTION_COLUMNS, IDENTITY_COLUMNS
)

def load_data(sample_frac=None):
    """
    Loads and merges the IEEE-CIS fraud detection train dataset.
    
    Reads train_transaction.csv and train_identity.csv with specific columns.
    LEFT JOINs them on TransactionID.
    Adds has_identity boolean column.
    """
    print(f"Loading transaction data from {TRAIN_TRANSACTION}...")
    df_trans = pd.read_csv(TRAIN_TRANSACTION, usecols=TRANSACTION_COLUMNS)
    df_id = pd.read_csv(TRAIN_IDENTITY, usecols=IDENTITY_COLUMNS)
    
    df = pd.merge(df_trans, df_id, on='TransactionID', how='left')
    df['has_identity'] = df['DeviceType'].notna()
    
    if sample_frac is not None:
        df = df.sample(frac=sample_frac, random_state=42)
        
    print(f"Total rows: {len(df)}")
    if 'isFraud' in df.columns:
        print(f"Fraud count: {df['isFraud'].sum()}")
    print(f"Identity coverage: {df['has_identity'].mean():.2%}")
    
    return df

def load_test_data():
    """
    Loads and merges the IEEE-CIS fraud detection test dataset.
    """
    # Test set lacks 'isFraud'
    trans_cols = [c for c in TRANSACTION_COLUMNS if c != 'isFraud']
    
    print(f"Loading test transaction data from {TEST_TRANSACTION}...")
    df_trans = pd.read_csv(TEST_TRANSACTION, usecols=trans_cols)
    df_id = pd.read_csv(TEST_IDENTITY, usecols=IDENTITY_COLUMNS)
    
    df = pd.merge(df_trans, df_id, on='TransactionID', how='left')
    df['has_identity'] = df['DeviceType'].notna()
    
    return df

if __name__ == '__main__':
    df_sample = load_data(sample_frac=0.1)
    print("Shape:", df_sample.shape)
    print("Columns:", list(df_sample.columns))


def load_simulated_data(sample_frac=None, legit_multiplier=1.0, simulated_path=None):
    """
    Load Person 2's simulated ATO dataset and pair with real legitimate transactions.

    Person 2's simulate/ato_dataset.csv contains only attack rows (isFraud=1).
    This function adds real isFraud==0 rows from the IEEE-CIS data to create
    a balanced dataset with ground-truth variant_id labels.

    Args:
        sample_frac: If set, sample this fraction of the IEEE-CIS data before
                     extracting legitimate rows (speeds up loading).
        legit_multiplier: Number of legitimate rows = len(attack_df) * legit_multiplier.
        simulated_path: Override path to the simulated CSV. Defaults to
                        PROJECT_ROOT / 'simulate' / 'ato_dataset.csv'.

    Returns:
        pd.DataFrame with all columns feature_engineer.py needs, plus 'variant_id'.
    """
    import numpy as np

    project_root = Path(__file__).parent.parent

    # 1. Load attack rows from Person 2's simulated dataset
    sim_path = Path(simulated_path) if simulated_path else project_root / 'simulate' / 'ato_dataset.csv'
    print(f"Loading simulated ATO data from {sim_path}...")
    attack_df = pd.read_csv(sim_path)
    print(f"  Attack rows: {len(attack_df)} (all isFraud=1)")

    if sample_frac is not None:
        attack_df = attack_df.sample(frac=sample_frac, random_state=42)
        print(f"  Subsampled to {len(attack_df)} attack rows (sample_frac={sample_frac})")

    # Coerce has_identity to int (simulated CSV may store as bool string)
    if 'has_identity' in attack_df.columns:
        attack_df['has_identity'] = attack_df['has_identity'].map(
            {True: 1, False: 0, 'True': 1, 'False': 0, 1: 1, 0: 0}
        ).fillna(0).astype(int)

    # 2. Load real IEEE-CIS data and extract legitimate rows
    print("Loading IEEE-CIS data for legitimate transaction samples...")
    ieee_df = load_data(sample_frac=sample_frac)
    legit_df = ieee_df[ieee_df['isFraud'] == 0].copy()

    n_legit = int(len(attack_df) * legit_multiplier)
    if n_legit > len(legit_df):
        n_legit = len(legit_df)
    legit_sample = legit_df.sample(n=n_legit, random_state=42)
    legit_sample['variant_id'] = 'LEGITIMATE'
    print(f"  Sampled {len(legit_sample)} legitimate rows (multiplier={legit_multiplier})")

    # 3. Concatenate, shuffle, return
    combined = pd.concat([attack_df, legit_sample], ignore_index=True)
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"  Combined dataset: {len(combined)} rows")
    print(f"  Fraud rate: {combined['isFraud'].mean():.2%}")
    variant_counts = combined['variant_id'].value_counts()
    print(f"  Variant distribution:")
    for v, c in variant_counts.items():
        print(f"    {v}: {c}")

    return combined
