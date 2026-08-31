# `simulate/` — ATO-001 Synthetic Data Generator (Person 2's Generate pillar)

Implements the official contract Person 1 published in
`identify/contract.json` and `PERSON_2_HANDOFF.md`. Generates synthetic
Account Takeover transactions for all 5 official variants (ATO-V1
through ATO-V5), grounded in real per-account behavioral baselines.

## Setup

Place the real IEEE-CIS files at (matches `config.py`):
```
data/train_transaction.csv
data/train_identity.csv
```

## Usage

```bash
# Generate all 5 official variants
python -m simulate.generate_dataset

# Generate just one variant (faster iteration)
python -m simulate.generate_dataset --variant ATO-V4

# Use a data sample while iterating
python -m simulate.generate_dataset --sample-frac 0.1

# Validate the output against the official signal catalog
python -m simulate.validate
```

## Files

| File | Purpose |
|---|---|
| `profile_builder.py` | `build_user_profile()` — per-account (card1) behavioral baseline: avg amount, known devices/addresses/categories/email domains, usual hours, real inter-transaction gap |
| `ato_simulator.py` | `apply_ato_variant()` + `generate_velocity_burst()` + `simulate_ato()` — implements the 6 official knobs against real per-account baselines |
| `generate_dataset.py` | Entry point. Loads data via `pipeline.loader` (team's shared loader), pulls variant configs from `identify.registry.AttackRegistry`, writes `ato_dataset.csv` |
| `validate.py` | Computes the official signal catalog's metrics (new_device, new_location, amount_deviation, time_deviation — see caveat below on new_beneficiary) for normal vs. each variant, so deviations can be sanity-checked before handoff |
| `ato_dataset.csv` | The packaged deliverable — synthetic ATO-001 transactions, all 5 variants, `is_synthetic=True` |
| `data_dictionary.md` | Column-by-column documentation, including what's a real field vs. a documented substitute |

## What's different from Person 1's reference `apply_ato_variant()`

Same 6-knob contract, same 5 variant configs — but every perturbed
value here is resampled from the real dataset's own distribution or
scaled from the account's own profile, instead of a hardcoded sentinel
(their reference uses `addr1 = 999`, `dist1 = 1500`,
`DeviceType = "mobile_unrecognized"`). This keeps the generator
compliant with the project's own fidelity requirement (CLAUDE.md
Section 2: "fidelity claims must be backed by something checkable, not
just asserted"). Semantics and output direction are identical either
way — this is an implementation refinement, not a contract change.

## Open items requiring Person 1 coordination

- **`beneficiary_change`**: no real IEEE-CIS field exists for this.
  Currently substituted with `ProductCD` + `P_emaildomain` shifts —
  flagged at runtime and in `data_dictionary.md`. Needs sign-off or a
  better substitute field.
- **Velocity/time knob interaction**: bursts (`velocity_change > 0`)
  can incidentally shift transactions into different hours even when
  `time_change: false`. Documented in `data_dictionary.md` — flagging
  here in case Person 1 or Person 3 want it constrained differently.

## Verify compliance with the ground truth

```bash
python -X utf8 -m identify.registry
```
