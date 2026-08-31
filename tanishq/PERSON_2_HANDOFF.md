# 🤝 Person 1 → Person 2 Integration & Handoff Guide

> **To:** Person 2 (Simulation & Attack Generation Lead)  
> **From:** Person 1 (Attack Intelligence & Ground Truth Owner)  
> **Topic:** Official Attack Contract & Simulation Specifications for Account Takeover (ATO-001)

---

## 🎯 The Rule of Engagement

> [!IMPORTANT]
> **Person 1 defines the ground truth.**  
> As Person 2, your role is to generate synthetic or augmented transaction streams that follow the exact simulation parameters and variant recipes below. Do not invent attack parameters independently.

---

## 📦 What Files You Have in `identify/`

```
identify/
├── contract.json       ← Standalone JSON contract with all simulation configs
├── taxonomy.json       ← Complete attack taxonomy & signal definitions
├── attacks.json        ← Deep encyclopedia of ATO-001 and all 5 variants
├── schemas.py          ← Python dataclasses and validation rules
└── registry.py         ← Python API to query attacks and variants
```

---

## 🚀 Method 1: Using the Python Registry in Your Code

If you are writing Python code in this repository, you can import the registry directly:

```python
from identify.registry import AttackRegistry

# 1. Initialize and load the ground truth
registry = AttackRegistry().load()

# 2. Get the official Attack Contract
contract = registry.get_attack_contract("ATO-001")
print("Allowed simulation knobs:", contract["simulation_parameters"])

# 3. Retrieve specific variant recipes for your generator
v1 = registry.get_variant("ATO-001", "ATO-V1")
print("V1 Simulation Config:", v1.simulation_config)
# Output: {'device_change': True, 'location_change': True, 'beneficiary_change': True, 'amount_change': 0.9, 'velocity_change': 0.3, 'time_change': False}
```

---

## 📄 Method 2: Loading Standalone `contract.json`

If you are using external tools, notebooks, or scripts:

```python
import json

with open("identify/contract.json", "r") as f:
    contract = json.load(f)

# Access variant parameters
v4_config = contract["variants_for_simulation"]["ATO-V4"]["simulation_config"]
print(v4_config)
```

---

## 🎛️ The 6 Simulation Parameters ("The Knobs")

When modifying or creating a simulated transaction stream, only modulate these 6 parameters:

| Parameter | Type | Value Range | Meaning |
|---|---|---|---|
| `device_change` | `bool` | `True` / `False` | Does this transaction originate from an unrecognized device? |
| `location_change` | `bool` | `True` / `False` | Does it originate from an unfamiliar geo-location / IP / address? |
| `beneficiary_change` | `bool` | `True` / `False` | Is money going to a never-before-seen beneficiary / destination? |
| `amount_change` | `float` | `0.0` to `1.0` | Amount deviation factor (`0.0` = normal amount, `1.0` = maximum spike). |
| `velocity_change` | `float` | `0.0` to `1.0` | Frequency acceleration (`0.0` = normal gap, `1.0` = rapid burst). |
| `time_change` | `bool` | `True` / `False` | Does transaction occur at an unusual time (e.g. 3 AM night window)? |

---

## 🧪 The 5 Attack Variant Recipes for Simulation

You must generate test streams for each of these 5 post-compromise behaviors:

### 🔴 ATO-V1: High-Value New Device Takeover (Loud)
* **Objective:** Test baseline detection on obvious attacks.
* **Simulation Configuration:**
  ```python
  {
      "device_change": True,
      "location_change": True,
      "beneficiary_change": True,
      "amount_change": 0.90,      # Huge amount surge
      "velocity_change": 0.30,
      "time_change": False
  }
  ```

### 🔴 ATO-V2: Velocity Burst from Known Device
* **Objective:** Test system when the device is compromised/known, but speed spikes.
* **Simulation Configuration:**
  ```python
  {
      "device_change": False,     # Known device!
      "location_change": False,
      "beneficiary_change": True,
      "amount_change": 0.40,
      "velocity_change": 0.90,    # 10+ rapid transactions in minutes
      "time_change": False
  }
  ```

### 🟡 ATO-V3: Off-Hours Location Shift
* **Objective:** Test travel vs takeover ambiguity.
* **Simulation Configuration:**
  ```python
  {
      "device_change": False,
      "location_change": True,     # New location
      "beneficiary_change": False,
      "amount_change": 0.10,       # Normal amount
      "velocity_change": 0.10,
      "time_change": True          # Night time / unusual hour
  }
  ```

### 🟢 ATO-V4: Subtle Amount Deviation (The Ghost)
* **Objective:** Test sensitivity limits on stealthy long-term fraud.
* **Simulation Configuration:**
  ```python
  {
      "device_change": False,
      "location_change": False,
      "beneficiary_change": False,
      "amount_change": 0.25,       # Barely noticeable deviation
      "velocity_change": 0.10,
      "time_change": False
  }
  ```

### 🟡 ATO-V5: Multi-Signal Low-Intensity (The Chameleon)
* **Objective:** Test HDC's ability to correlate multiple weak anomalies.
* **Simulation Configuration:**
  ```python
  {
      "device_change": False,
      "location_change": True,     # Slight location shift
      "beneficiary_change": False,
      "amount_change": 0.20,       # Slight amount bump
      "velocity_change": 0.30,     # Slightly faster
      "time_change": True          # Slight time shift
  }
  ```

---

## 🛠️ Ready-to-Use Simulation Helper for Person 2

Person 2 can drop this function into their code to inject any variant into a baseline user profile:

```python
import numpy as np

def apply_ato_variant(base_transaction, variant_config):
    """
    Modifies a legitimate baseline transaction according to Person 1's ground truth.
    """
    simulated_txn = base_transaction.copy()
    
    if variant_config["device_change"]:
        simulated_txn["DeviceType"] = "mobile_unrecognized"
        simulated_txn["id_15"] = "New"
        
    if variant_config["location_change"]:
        simulated_txn["addr1"] = 999  # New location code
        simulated_txn["dist1"] = 1500 # High distance
        
    if variant_config["amount_change"] > 0:
        multiplier = 1.0 + (variant_config["amount_change"] * 5.0)
        simulated_txn["TransactionAmt"] *= multiplier
        
    if variant_config["time_change"]:
        # Shift timestamp into 2:00 AM - 4:00 AM window
        simulated_txn["TransactionDT"] = (simulated_txn["TransactionDT"] // 86400) * 86400 + 3 * 3600
        
    return simulated_txn
```

---

## 📬 Person 1 Contact & Verification

Whenever you update your simulation scripts or generate synthetic datasets, you can verify compliance with:
```bash
python -X utf8 -m identify.registry
```
If you need new parameters or signals added to the ground truth, coordinate with Person 1.
