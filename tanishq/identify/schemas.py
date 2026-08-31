"""
schemas.py — The Data Validator (Spell-Checker for Attack Data)
================================================================

WHAT THIS FILE DOES (Simple Explanation):
    Imagine you have a form to fill out for each attack. This file defines
    what fields the form has, what type each field should be (text, number, 
    true/false), and checks that everything is filled in correctly.

    In programming, we call these "schemas" or "data classes".

WHY WE NEED IT:
    Without validation, someone could accidentally put a number where text
    should go, or forget a required field. This catches those mistakes early.

HOW IT WORKS:
    We use Python's built-in 'dataclasses' — think of them as fancy templates
    that automatically create classes with the right fields.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# =============================================================================
# ENUMS — These are like dropdown menus. You can only pick from the listed values.
# =============================================================================

class RiskLevel(Enum):
    """
    How risky is this attack variant?
    Think of it like a traffic light system:
        LOW    = 🟢 Green  — Minor concern, monitor it
        MEDIUM = 🟡 Yellow — Moderate risk, investigate
        HIGH   = 🔴 Red    — Serious risk, act quickly
        VERY_HIGH = 🔴🔴 Double Red — Critical, act immediately
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DetectionDifficulty(Enum):
    """
    How hard is it for our system to detect this variant?
        EASY      = Obvious fraud, many red flags
        MODERATE  = Some red flags, needs attention
        HARD      = Few red flags, needs smart analysis
        VERY_HARD = Almost invisible, needs very sensitive detection
    """
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"


class MitigationAction(Enum):
    """
    What should we DO when we detect fraud?
    Ordered from least aggressive to most aggressive:
        STEP_UP  = Ask the user to prove they're really them (e.g., send OTP)
        REVIEW   = Flag for a human analyst to look at
        HOLD     = Pause the transaction temporarily
        BLOCK    = Stop the transaction completely and freeze account
    """
    STEP_UP_AUTHENTICATION = "step_up_authentication"
    REVIEW = "review"
    HOLD = "hold"
    BLOCK = "block"


class SignalDataType(Enum):
    """
    What kind of data does a signal produce?
        BOOLEAN = True/False (e.g., "Is this a new device? Yes or No")
        FLOAT   = A decimal number (e.g., "How far from normal is the amount? 0.7")
    """
    BOOLEAN = "boolean"
    FLOAT = "float"


# =============================================================================
# DATA CLASSES — These are the "form templates" for our attack data
# =============================================================================

@dataclass
class AttackSignal:
    """
    A single detection signal — one "red flag" we watch for.
    
    Example:
        signal_id  = "SIG-001"
        name       = "new_device"
        description = "Transaction from an unrecognized device"
        data_type  = "boolean"  (it's either a new device or not)
        weight     = 0.85  (how important this signal is, 0 to 1)
    """
    signal_id: str          # Unique identifier like "SIG-001"
    name: str               # Short name like "new_device"
    description: str        # Human-readable explanation
    data_type: str          # "boolean" or "float"
    weight: float = 0.5    # How important is this signal (0.0 to 1.0)
    unit: Optional[str] = None  # Unit of measurement (only for float signals)

    def validate(self) -> list[str]:
        """Check if this signal's data is valid. Returns list of errors (empty = all good)."""
        errors = []
        if not self.signal_id.startswith("SIG-"):
            errors.append(f"Signal ID '{self.signal_id}' must start with 'SIG-'")
        if not self.name:
            errors.append("Signal name cannot be empty")
        if not (0.0 <= self.weight <= 1.0):
            errors.append(f"Signal weight {self.weight} must be between 0.0 and 1.0")
        if self.data_type not in ("boolean", "float"):
            errors.append(f"Signal data_type '{self.data_type}' must be 'boolean' or 'float'")
        return errors


@dataclass
class SimulationParameter:
    """
    A "knob" that the simulation team can turn when generating test data.
    
    Example:
        param   = "device_change"
        type    = "boolean"
        default = False
        description = "Whether the simulated transaction comes from a new device"
    """
    param: str              # Parameter name like "device_change"
    type: str               # "boolean" or "float"
    description: str        # What this parameter controls
    default: object = None  # Default value (False for boolean, 0.0 for float)
    range: Optional[list] = None  # Min/max for float params, e.g., [0.0, 1.0]

    def validate(self) -> list[str]:
        """Check if this parameter's data is valid."""
        errors = []
        if not self.param:
            errors.append("Parameter name cannot be empty")
        if self.type not in ("boolean", "float"):
            errors.append(f"Parameter type '{self.type}' must be 'boolean' or 'float'")
        if self.type == "float" and self.range is None:
            errors.append(f"Float parameter '{self.param}' must have a range defined")
        return errors


@dataclass
class Mitigation:
    """
    An action to take when fraud is detected.
    
    Example:
        mitigation_id  = "MIT-001"
        name           = "step_up_authentication"
        description    = "Ask user to verify identity via OTP"
        customer_friction = "medium"  (how annoying is this for the customer)
    """
    mitigation_id: str          # Unique ID like "MIT-001"
    name: str                   # Short name like "step_up_authentication"
    description: str            # What this mitigation does
    severity_impact: str        # What severity level triggers this
    customer_friction: str      # How much this annoys the customer

    def validate(self) -> list[str]:
        """Check if this mitigation's data is valid."""
        errors = []
        if not self.mitigation_id.startswith("MIT-"):
            errors.append(f"Mitigation ID '{self.mitigation_id}' must start with 'MIT-'")
        if not self.name:
            errors.append("Mitigation name cannot be empty")
        return errors


@dataclass
class ActiveSignals:
    """
    Which signals are "ON" for a specific variant, and with what intensity.
    Supports both Account Takeover (ATO) and Money Movement (MM) detection signals.
    """
    new_device: bool = False
    new_location: bool = False
    new_beneficiary: bool = False
    amount_deviation: float = 0.0
    velocity_deviation: float = 0.0
    time_deviation: bool = False
    # Money Movement Signals
    fan_out_degree: float = 0.0
    fan_in_degree: float = 0.0
    transit_velocity_sec: float = 0.0
    amount_layering_ratio: float = 0.0
    shared_device_cluster: bool = False
    account_dormancy_score: float = 0.0
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to a dictionary for easy use."""
        d = {
            "new_device": self.new_device,
            "new_location": self.new_location,
            "new_beneficiary": self.new_beneficiary,
            "amount_deviation": self.amount_deviation,
            "velocity_deviation": self.velocity_deviation,
            "time_deviation": self.time_deviation,
            "fan_out_degree": self.fan_out_degree,
            "fan_in_degree": self.fan_in_degree,
            "transit_velocity_sec": self.transit_velocity_sec,
            "amount_layering_ratio": self.amount_layering_ratio,
            "shared_device_cluster": self.shared_device_cluster,
            "account_dormancy_score": self.account_dormancy_score,
        }
        d.update(self.raw_data)
        return d

    def active_count(self) -> int:
        """Count how many signals are currently active (firing)."""
        count = 0
        for k, v in self.to_dict().items():
            if isinstance(v, bool) and v:
                count += 1
            elif isinstance(v, (int, float)) and v > 0.15:
                count += 1
        return count


@dataclass
class AttackVariant:
    """
    One specific PATTERN of how an attack plays out after compromise.
    
    This is NOT a different attack — it's a different BEHAVIOUR pattern.
    Think of it like this:
        - The attack (ATO) is the disease
        - The variant is how the symptoms show up in a specific patient
    
    Example:
        ATO-V1: New device + new beneficiary + big amount (LOUD and obvious)
        ATO-V4: Known device + known beneficiary + tiny amount change (QUIET and sneaky)
    """
    variant_id: str                     # Like "ATO-V1"
    name: str                           # Human-readable name
    description: str                    # What makes this variant unique
    risk_level: str                     # "low", "medium", "high", "very_high"
    risk_score: float                   # 0.0 (safe) to 1.0 (extremely risky)
    active_signals: ActiveSignals       # Which signals fire in this variant
    simulation_config: dict             # Settings for the simulation team
    expected_mitigation: str            # What action should the system take
    detection_difficulty: str           # How hard to detect: "easy" to "very_hard"
    notes: str = ""                     # Additional context

    def validate(self) -> list[str]:
        """Check if this variant's data is valid."""
        errors = []
        if not any(self.variant_id.startswith(p) for p in ["ATO-V", "MM-V", "GENAI-V", "SOC-V", "PM-V", "MRF-V", "SYN-V", "TB-V"]):
            errors.append(f"Variant ID '{self.variant_id}' must start with a valid prefix")
        if not (0.0 <= self.risk_score <= 1.0):
            errors.append(f"Risk score {self.risk_score} must be between 0.0 and 1.0")
        valid_risk_levels = {"low", "medium", "high", "very_high"}
        if self.risk_level not in valid_risk_levels:
            errors.append(f"Risk level '{self.risk_level}' must be one of {valid_risk_levels}")
        valid_difficulties = {"easy", "moderate", "hard", "very_hard"}
        if self.detection_difficulty not in valid_difficulties:
            errors.append(f"Detection difficulty '{self.detection_difficulty}' must be one of {valid_difficulties}")
        return errors


@dataclass
class AttackDefinition:
    """
    The COMPLETE definition of an attack type. This is the top-level "encyclopedia entry".
    
    It contains:
        - Basic info (ID, name, category)
        - What the attacker wants (objective)
        - What must be true first (preconditions)  
        - What it looks like (observable behaviour)
        - What happens to money (payment consequences)
        - How AI makes it worse (GenAI enhancement)
        - Red flags to watch for (detection signals)
        - How to stop it (mitigations)
        - Test settings (simulation parameters)
        - Different patterns (variants)
    """
    attack_id: str                              # Like "ATO-001"
    name: str                                   # "Account Takeover"
    code: str                                   # "ATO"
    category: str                               # "account_compromise"
    attack_objective: dict                      # What the attacker wants
    preconditions: dict                         # What must be true first
    observable_behaviour: dict                  # What it looks like
    payment_consequences: dict                  # What happens to money
    genai_enhancement: dict                     # How AI makes it worse
    signals: list[str]                          # List of signal names
    simulation_parameters: list[SimulationParameter]  # Test knobs
    mitigations: list[str]                      # Response actions
    detection_signals: dict                     # Detailed signal config
    variants: list[AttackVariant]               # All behavioural patterns

    def validate(self) -> list[str]:
        """Validate the entire attack definition. Returns list of errors."""
        errors = []

        # Check attack ID format
        if not any(self.attack_id.startswith(p) for p in ["ATO-", "MM-", "GENAI-", "SOC-", "PM-", "MRF-", "SYN-", "TB-"]):
            errors.append(f"Attack ID '{self.attack_id}' must start with a valid prefix")

        # Check we have at least one signal
        if len(self.signals) == 0:
            errors.append("Attack must have at least one signal defined")

        # Check we have at least one variant
        if len(self.variants) == 0:
            errors.append("Attack must have at least one variant defined")

        # Check we have at least one mitigation
        if len(self.mitigations) == 0:
            errors.append("Attack must have at least one mitigation defined")

        # Validate all simulation parameters
        for param in self.simulation_parameters:
            errors.extend(param.validate())

        # Validate all variants
        for variant in self.variants:
            errors.extend(variant.validate())

        return errors

    def get_variant(self, variant_id: str) -> Optional[AttackVariant]:
        """Look up a specific variant by its ID."""
        for variant in self.variants:
            if variant.variant_id == variant_id:
                return variant
        return None

    def get_contract(self) -> dict:
        """
        Generate the ATTACK CONTRACT — the standardized JSON that other 
        team members use. This is what Person 2, 3, 4 will consume.
        """
        return {
            "attack_id": self.attack_id,
            "name": self.name,
            "signals": self.signals,
            "simulation_parameters": [p.param for p in self.simulation_parameters],
            "mitigations": self.mitigations
        }


# =============================================================================
# HELPER FUNCTIONS — Utilities for working with the schemas
# =============================================================================

def signals_from_dict(data: dict) -> ActiveSignals:
    """
    Convert a dictionary (from JSON) into an ActiveSignals object.
    """
    return ActiveSignals(
        new_device=data.get("new_device", False),
        new_location=data.get("new_location", False),
        new_beneficiary=data.get("new_beneficiary", False),
        amount_deviation=data.get("amount_deviation", 0.0),
        velocity_deviation=data.get("velocity_deviation", 0.0),
        time_deviation=data.get("time_deviation", False),
        fan_out_degree=data.get("fan_out_degree", 0.0),
        fan_in_degree=data.get("fan_in_degree", 0.0),
        transit_velocity_sec=data.get("transit_velocity_sec", 0.0),
        amount_layering_ratio=data.get("amount_layering_ratio", 0.0),
        shared_device_cluster=data.get("shared_device_cluster", False),
        account_dormancy_score=data.get("account_dormancy_score", 0.0),
        raw_data=data
    )


def variant_from_dict(data: dict) -> AttackVariant:
    """
    Convert a dictionary (from JSON) into an AttackVariant object.
    """
    return AttackVariant(
        variant_id=data["variant_id"],
        name=data["name"],
        description=data["description"],
        risk_level=data["risk_level"],
        risk_score=data["risk_score"],
        active_signals=signals_from_dict(data["active_signals"]),
        simulation_config=data["simulation_config"],
        expected_mitigation=data["expected_mitigation"],
        detection_difficulty=data["detection_difficulty"],
        notes=data.get("notes", "")
    )


def sim_param_from_dict(data: dict) -> SimulationParameter:
    """
    Convert a dictionary (from JSON) into a SimulationParameter object.
    """
    return SimulationParameter(
        param=data["param"],
        type=data["type"],
        description=data["description"],
        default=data.get("default"),
        range=data.get("range")
    )


def attack_from_dict(data: dict) -> AttackDefinition:
    """
    Convert a full attack dictionary (from JSON) into an AttackDefinition object.
    This is the main function that builds the complete attack from raw data.
    """
    return AttackDefinition(
        attack_id=data["attack_id"],
        name=data["name"],
        code=data["code"],
        category=data["category"],
        attack_objective=data["attack_objective"],
        preconditions=data["preconditions"],
        observable_behaviour=data["observable_behaviour"],
        payment_consequences=data["payment_consequences"],
        genai_enhancement=data["genai_enhancement"],
        signals=data["signals"],
        simulation_parameters=[sim_param_from_dict(p) for p in data["simulation_parameters"]],
        mitigations=data["mitigations"],
        detection_signals=data["detection_signals"],
        variants=[variant_from_dict(v) for v in data["variants"]]
    )


# =============================================================================
# SELF-TEST — Run this file directly to verify the schemas work
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  SCHEMAS SELF-TEST")
    print("=" * 60)

    # Test 1: Create an ActiveSignals object
    signals = ActiveSignals(
        new_device=True,
        new_beneficiary=True,
        amount_deviation=0.9
    )
    print(f"\n✅ ActiveSignals created: {signals.active_count()} signals active")

    # Test 2: Create a variant
    variant = AttackVariant(
        variant_id="ATO-V1",
        name="Test Variant",
        description="Test description",
        risk_level="very_high",
        risk_score=0.95,
        active_signals=signals,
        simulation_config={},
        expected_mitigation="block",
        detection_difficulty="easy"
    )
    errors = variant.validate()
    print(f"✅ AttackVariant created: {variant.variant_id} — {len(errors)} validation errors")

    # Test 3: Create a SimulationParameter
    param = SimulationParameter(
        param="device_change",
        type="boolean",
        description="Whether device changes"
    )
    errors = param.validate()
    print(f"✅ SimulationParameter created: {param.param} — {len(errors)} validation errors")

    # Test 4: Test enum values
    print(f"✅ RiskLevel values: {[r.value for r in RiskLevel]}")
    print(f"✅ MitigationAction values: {[m.value for m in MitigationAction]}")

    print(f"\n{'=' * 60}")
    print(f"  ALL SCHEMA TESTS PASSED ✅")
    print(f"{'=' * 60}")
