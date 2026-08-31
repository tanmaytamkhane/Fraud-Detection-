"""
config.py — Central Configuration
===================================
All paths, column selections, hyperparameters, and thresholds in one place.
Change settings here — everything else reads from this file.
"""

from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
IDENTIFY_DIR = PROJECT_ROOT / "identify"

# Dataset files
TRAIN_TRANSACTION = DATA_DIR / "train_transaction.csv"
TRAIN_IDENTITY = DATA_DIR / "train_identity.csv"
TEST_TRANSACTION = DATA_DIR / "test_transaction.csv"
TEST_IDENTITY = DATA_DIR / "test_identity.csv"

# =============================================================================
# COLUMNS TO LOAD (memory-efficient — only what we need)
# =============================================================================

TRANSACTION_COLUMNS = [
    # Core
    "TransactionID", "isFraud", "TransactionDT", "TransactionAmt",
    # Card info (user identity proxy)
    "ProductCD", "card1", "card2", "card3", "card4", "card5", "card6",
    # Address
    "addr1", "addr2", "dist1",
    # Email
    "P_emaildomain", "R_emaildomain",
    # Counting features (velocity signals)
    "C1", "C2", "C5", "C6", "C13", "C14",
    # Time-delta features
    "D1", "D3", "D4", "D10", "D15",
    # Match flags (address mismatch signals)
    "M4", "M5", "M6",
]

IDENTITY_COLUMNS = [
    "TransactionID",
    "DeviceType", "DeviceInfo",
    "id_01", "id_02",
    "id_05", "id_06",
    "id_11",
    "id_15", "id_16",
    "id_28", "id_29",
    "id_30", "id_31",
    "id_33",
    "id_35", "id_36", "id_37", "id_38",
]

# =============================================================================
# FEATURE ENGINEERING SETTINGS
# =============================================================================

# Signal 1: device_risk
DEVICE_RISK_WEIGHTS = {
    "has_identity": 0.35,       # Whether identity data exists (3.79x fraud ratio)
    "device_type_mobile": 0.20, # Mobile devices = higher risk (10.17% vs 6.52%)
    "id_15_found": 0.25,        # id_15=Found = higher fraud in this dataset
    "id_28_found": 0.20,        # id_28=Found = higher fraud in this dataset
}

# Signal 2: address_mismatch
ADDRESS_MISMATCH_WEIGHTS = {
    "M4_M2": 0.50,              # M4=M2 = address mismatch (3.10x ratio)
    "M5_T": 0.20,               # M5=T = match flag
    "dist1_high": 0.30,         # High distance from normal
}

# Signal 3: amount_deviation
AMOUNT_ZSCORE_CAP = 5.0         # Cap z-scores at ±5 (prevents outlier dominance)

# Signal 4: velocity
VELOCITY_MEDIAN_FRAUD = 3376    # Fraud median time-since-last (seconds)
VELOCITY_MEDIAN_LEGIT = 6047    # Legit median time-since-last (seconds)

# Signal 5: time_anomaly
NIGHT_HOURS = (0, 6)            # Night = 12am to 6am

# Signal 6: channel_risk — fraud rates per ProductCD
PRODUCT_FRAUD_RATES = {
    "C": 0.1169,  # 11.69% — highest risk
    "S": 0.0590,  # 5.90%
    "H": 0.0477,  # 4.77%
    "R": 0.0378,  # 3.78%
    "W": 0.0204,  # 2.04% — lowest risk
}

# =============================================================================
# HDC HYPERPARAMETERS
# =============================================================================

HDC_DIMENSIONS = 10_000         # Hypervector dimensionality
HDC_NUM_LEVELS = 100            # Quantization levels for continuous signals
HDC_LEARNING_RATE = 1.0         # How much to adjust prototypes on misclassification
HDC_RETRAIN_EPOCHS = 30         # Number of retraining iterations
HDC_SEED = 42                   # Random seed for reproducibility

# =============================================================================
# TRAINING SETTINGS
# =============================================================================

TRAIN_TEST_SPLIT = 0.2          # 80% train, 20% validation
RANDOM_STATE = 42               # Reproducible splits
FRAUD_OVERSAMPLE_RATIO = 3.0    # Oversample fraud by 3x to handle imbalance (3.5% → ~10%)

# =============================================================================
# OUTPUT SIGNAL NAMES (the 6 signals our model uses)
# =============================================================================

SIGNAL_NAMES = [
    "device_risk",
    "address_mismatch",
    "amount_deviation",
    "velocity",
    "time_anomaly",
    "channel_risk",
]

NUM_SIGNALS = len(SIGNAL_NAMES)
