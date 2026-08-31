"""
__init__.py — Makes 'identify' a Python package
=================================================

This file tells Python that the 'identify' folder is a package 
(a collection of related Python files that work together).

Without this file, Python wouldn't know how to import from this folder.
"""

from identify.schemas import (
    AttackSignal,
    SimulationParameter,
    Mitigation,
    ActiveSignals,
    AttackVariant,
    AttackDefinition,
    RiskLevel,
    DetectionDifficulty,
    MitigationAction,
)
from identify.registry import AttackRegistry

__all__ = [
    "AttackRegistry",
    "AttackSignal",
    "SimulationParameter",
    "Mitigation",
    "ActiveSignals",
    "AttackVariant",
    "AttackDefinition",
    "RiskLevel",
    "DetectionDifficulty",
    "MitigationAction",
]
