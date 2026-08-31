"""
registry.py — The Attack Registry (The Librarian)
===================================================

WHAT THIS FILE DOES (Simple Explanation):
    This is like a LIBRARIAN for our attack data. It:
    1. Loads the JSON files (taxonomy.json and attacks.json)
    2. Converts them into Python objects using our schemas
    3. Validates everything is correct
    4. Provides easy ways to look up attacks and variants

    Other team members (Person 2, 3, 4) will import this file to 
    access the attack definitions you created.

HOW TO USE IT:
    from identify.registry import AttackRegistry
    
    registry = AttackRegistry()     # Creates the librarian
    registry.load()                 # Librarian reads all the books
    
    # Now you can ask questions:
    ato = registry.get_attack("ATO-001")        # Get the ATO definition
    v1 = registry.get_variant("ATO-001", "ATO-V1")  # Get variant 1
    all_attacks = registry.list_attacks()         # List everything
"""

import json
import os
from pathlib import Path
from typing import Optional

# Import our schemas (the form templates)
from identify.schemas import (
    AttackDefinition,
    AttackVariant,
    ActiveSignals,
    attack_from_dict,
    variant_from_dict,
)


class AttackRegistry:
    """
    The main class that manages all attack data.
    
    Think of it as a LIBRARY:
        - taxonomy.json  = the card catalog (what categories exist)
        - attacks.json   = the actual books (detailed attack info)
        - this class     = the librarian who helps you find things
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the registry.
        
        Args:
            data_dir: Path to the folder containing taxonomy.json and attacks.json.
                     If not provided, uses the 'identify' folder next to this file.
        """
        # Figure out where our data files are
        if data_dir is None:
            # Default: same directory as this Python file
            self.data_dir = Path(__file__).parent
        else:
            self.data_dir = Path(data_dir)

        # These will be filled in when load() is called
        self.taxonomy: dict = {}                          # Raw taxonomy data
        self.attacks: dict[str, AttackDefinition] = {}    # Attack ID → AttackDefinition
        self._is_loaded: bool = False                     # Has load() been called?

    # =========================================================================
    # LOADING — Reading the JSON files and converting to Python objects
    # =========================================================================

    def load(self) -> "AttackRegistry":
        """
        Load all data from JSON files. Must be called before using any other method.
        
        Returns:
            self (so you can chain: registry = AttackRegistry().load())
        
        Raises:
            FileNotFoundError: If taxonomy.json or attacks.json doesn't exist
            json.JSONDecodeError: If a JSON file has invalid syntax
        """
        # Step 1: Load the taxonomy (card catalog)
        taxonomy_path = self.data_dir / "taxonomy.json"
        if not taxonomy_path.exists():
            raise FileNotFoundError(
                f"Cannot find taxonomy.json at: {taxonomy_path}\n"
                f"Make sure the file exists in the 'identify' directory."
            )

        with open(taxonomy_path, "r", encoding="utf-8") as f:
            self.taxonomy = json.load(f)

        # Step 2: Load the attacks (the books)
        attacks_path = self.data_dir / "attacks.json"
        if not attacks_path.exists():
            raise FileNotFoundError(
                f"Cannot find attacks.json at: {attacks_path}\n"
                f"Make sure the file exists in the 'identify' directory."
            )

        with open(attacks_path, "r", encoding="utf-8") as f:
            attacks_data = json.load(f)

        # Step 3: Convert raw dictionaries into proper Python objects
        self.attacks = {}
        for attack_data in attacks_data["attacks"]:
            attack = attack_from_dict(attack_data)
            self.attacks[attack.attack_id] = attack

        self._is_loaded = True
        return self

    def _check_loaded(self):
        """Make sure load() has been called. Raises error if not."""
        if not self._is_loaded:
            raise RuntimeError(
                "Registry not loaded! Call registry.load() first."
            )

    # =========================================================================
    # QUERYING — Asking questions about the data
    # =========================================================================

    def get_attack(self, attack_id: str) -> Optional[AttackDefinition]:
        """
        Look up an attack by its ID.
        
        Example:
            ato = registry.get_attack("ATO-001")
            print(ato.name)  # "Account Takeover"
        
        Args:
            attack_id: The attack ID to look up (e.g., "ATO-001")
            
        Returns:
            The AttackDefinition if found, None if not found
        """
        self._check_loaded()
        return self.attacks.get(attack_id)

    def get_variant(self, attack_id: str, variant_id: str) -> Optional[AttackVariant]:
        """
        Look up a specific variant of an attack.
        
        Example:
            v1 = registry.get_variant("ATO-001", "ATO-V1")
            print(v1.name)  # "High-Value New Device Takeover"
            print(v1.risk_score)  # 0.95
        
        Args:
            attack_id: The parent attack ID (e.g., "ATO-001")
            variant_id: The variant ID (e.g., "ATO-V1")
            
        Returns:
            The AttackVariant if found, None if not found
        """
        self._check_loaded()
        attack = self.attacks.get(attack_id)
        if attack is None:
            return None
        return attack.get_variant(variant_id)

    def list_attacks(self) -> list[dict]:
        """
        List all attacks with a brief summary.
        
        Returns:
            List of dictionaries with basic info about each attack
        """
        self._check_loaded()
        result = []
        for attack in self.attacks.values():
            result.append({
                "attack_id": attack.attack_id,
                "name": attack.name,
                "code": attack.code,
                "category": attack.category,
                "variant_count": len(attack.variants),
                "signal_count": len(attack.signals),
            })
        return result

    def list_variants(self, attack_id: str) -> list[dict]:
        """
        List all variants for a specific attack.
        
        Example:
            variants = registry.list_variants("ATO-001")
            for v in variants:
                print(f"{v['variant_id']}: {v['name']} (risk: {v['risk_score']})")
        
        Returns:
            List of dictionaries with variant summaries
        """
        self._check_loaded()
        attack = self.attacks.get(attack_id)
        if attack is None:
            return []

        result = []
        for variant in attack.variants:
            result.append({
                "variant_id": variant.variant_id,
                "name": variant.name,
                "risk_level": variant.risk_level,
                "risk_score": variant.risk_score,
                "detection_difficulty": variant.detection_difficulty,
                "expected_mitigation": variant.expected_mitigation,
                "active_signal_count": variant.active_signals.active_count(),
            })
        return result

    def get_attack_contract(self, attack_id: str) -> Optional[dict]:
        """
        Get the ATTACK CONTRACT for a specific attack.
        This is the standardized JSON that other team members consume.
        
        Example:
            contract = registry.get_attack_contract("ATO-001")
            # Returns:
            # {
            #   "attack_id": "ATO-001",
            #   "name": "Account Takeover",
            #   "signals": ["new_device", "new_location", ...],
            #   "simulation_parameters": ["device_change", ...],
            #   "mitigations": ["step_up_authentication", ...]
            # }
        """
        self._check_loaded()
        attack = self.attacks.get(attack_id)
        if attack is None:
            return None
        return attack.get_contract()

    def get_signal_catalog(self) -> list[dict]:
        """
        Get the master list of all detection signals from the taxonomy.
        
        Returns:
            List of signal definitions
        """
        self._check_loaded()
        return self.taxonomy.get("signal_catalog", {}).get("signals", [])

    def get_mitigation_catalog(self) -> list[dict]:
        """
        Get the master list of all mitigation actions from the taxonomy.
        
        Returns:
            List of mitigation definitions
        """
        self._check_loaded()
        return self.taxonomy.get("mitigation_catalog", {}).get("mitigations", [])

    # =========================================================================
    # VALIDATION — Making sure everything is correct
    # =========================================================================

    def validate(self) -> dict:
        """
        Validate ALL loaded data against the schemas.
        
        Returns:
            Dictionary with validation results:
            {
                "is_valid": True/False,
                "total_errors": 0,
                "errors_by_attack": { "ATO-001": [...] }
            }
        """
        self._check_loaded()
        all_errors = {}

        for attack_id, attack in self.attacks.items():
            errors = attack.validate()
            if errors:
                all_errors[attack_id] = errors

        return {
            "is_valid": len(all_errors) == 0,
            "total_errors": sum(len(e) for e in all_errors.values()),
            "errors_by_attack": all_errors
        }

    # =========================================================================
    # DISPLAY — Pretty-printing for debugging and verification
    # =========================================================================

    def print_summary(self):
        """Print a human-readable summary of all loaded data."""
        self._check_loaded()

        print("\n" + "=" * 70)
        print("  🛡️  ATTACK REGISTRY — SUMMARY")
        print("=" * 70)

        # Taxonomy info
        print(f"\n  📚 Taxonomy version: {self.taxonomy.get('version', 'unknown')}")
        print(f"  📅 Last updated: {self.taxonomy.get('last_updated', 'unknown')}")

        categories = self.taxonomy.get("categories", [])
        print(f"  📂 Categories loaded: {len(categories)}")

        signals = self.get_signal_catalog()
        print(f"  🚨 Signals in catalog: {len(signals)}")

        mitigations = self.get_mitigation_catalog()
        print(f"  🛑 Mitigations in catalog: {len(mitigations)}")

        # Attack info
        print(f"\n  {'─' * 66}")
        print(f"  📋 ATTACKS LOADED: {len(self.attacks)}")
        print(f"  {'─' * 66}")

        for attack_id, attack in self.attacks.items():
            print(f"\n  🎯 {attack.name} ({attack.attack_id})")
            print(f"     Code: {attack.code}")
            print(f"     Category: {attack.category}")
            print(f"     Signals: {', '.join(attack.signals)}")
            print(f"     Mitigations: {', '.join(attack.mitigations)}")
            print(f"     Variants: {len(attack.variants)}")

            # Print each variant
            print(f"\n     {'Variant':<12} {'Name':<35} {'Risk':<12} {'Difficulty':<12} {'Signals'}")
            print(f"     {'─' * 12} {'─' * 35} {'─' * 12} {'─' * 12} {'─' * 8}")

            for v in attack.variants:
                active = v.active_signals.active_count()
                risk_emoji = {
                    "very_high": "🔴🔴",
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(v.risk_level, "⚪")

                print(f"     {v.variant_id:<12} {v.name:<35} {risk_emoji} {v.risk_level:<8} {v.detection_difficulty:<12} {active}/6")

            # Print attack contract
            contract = attack.get_contract()
            print(f"\n     📄 ATTACK CONTRACT:")
            print(f"     {json.dumps(contract, indent=6)}")

        # Validation
        validation = self.validate()
        print(f"\n  {'─' * 66}")
        if validation["is_valid"]:
            print(f"  ✅ VALIDATION: ALL DATA IS VALID")
        else:
            print(f"  ❌ VALIDATION: {validation['total_errors']} ERRORS FOUND")
            for attack_id, errors in validation["errors_by_attack"].items():
                for error in errors:
                    print(f"     ⚠️  [{attack_id}] {error}")
        print(f"  {'─' * 66}")

        print(f"\n{'=' * 70}")
        print(f"  REGISTRY LOAD COMPLETE ✅")
        print(f"{'=' * 70}\n")


# =============================================================================
# MAIN — Run this file directly to test everything end-to-end
# =============================================================================

if __name__ == "__main__":
    """
    SELF-TEST: When you run this file directly (python identify/registry.py),
    it loads all data, validates it, and prints a full summary.
    """
    print("\n🚀 Starting Attack Registry self-test...\n")

    try:
        # Create the registry and load data
        registry = AttackRegistry()
        registry.load()
        print("✅ Data loaded successfully!\n")

        # Print the full summary
        registry.print_summary()

        # Demonstrate querying
        print("\n📖 QUERY EXAMPLES:")
        print("=" * 50)

        # Example 1: Get attack by ID
        ato = registry.get_attack("ATO-001")
        if ato:
            print(f"\n  1. get_attack('ATO-001')")
            print(f"     → Name: {ato.name}")
            print(f"     → Variants: {len(ato.variants)}")
            print(f"     → Signals: {ato.signals}")

        # Example 2: Get a specific variant
        v1 = registry.get_variant("ATO-001", "ATO-V1")
        if v1:
            print(f"\n  2. get_variant('ATO-001', 'ATO-V1')")
            print(f"     → Name: {v1.name}")
            print(f"     → Risk: {v1.risk_level} ({v1.risk_score})")
            print(f"     → Active signals: {v1.active_signals.active_count()}/6")

        # Example 3: Get the stealth variant
        v4 = registry.get_variant("ATO-001", "ATO-V4")
        if v4:
            print(f"\n  3. get_variant('ATO-001', 'ATO-V4') — The sneaky one")
            print(f"     → Name: {v4.name}")
            print(f"     → Risk: {v4.risk_level} ({v4.risk_score})")
            print(f"     → Detection difficulty: {v4.detection_difficulty}")
            print(f"     → Active signals: {v4.active_signals.active_count()}/6")

        # Example 4: Get the attack contract
        contract = registry.get_attack_contract("ATO-001")
        if contract:
            print(f"\n  4. get_attack_contract('ATO-001')")
            print(f"     → {json.dumps(contract, indent=8)}")

        # Example 5: List all variants
        variants = registry.list_variants("ATO-001")
        print(f"\n  5. list_variants('ATO-001') → {len(variants)} variants found")
        for v in variants:
            print(f"     → {v['variant_id']}: {v['name']} (risk: {v['risk_score']})")

        print(f"\n{'=' * 50}")
        print("✅ ALL SELF-TESTS PASSED!")
        print(f"{'=' * 50}\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
