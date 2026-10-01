# Synthetic MM event schema

`python -m simulate.mm_simulator` writes `mm_raw_dataset.csv` and `mm_validation_report.json`. These are synthetic stress-test artifacts, not observed bank data.

| Column | Meaning |
| --- | --- |
| transfer_id | Unique synthetic event ID |
| timestamp | Integer simulation step; physical duration unspecified |
| sender, receiver | Account identifiers |
| amount | Simulated positive transfer amount in unspecified units |
| device_id | Simulated sending device identifier |
| channel | Transfer channel (currently TRANSFER) |
| lookalike_type | `ordinary`, `payroll`, `marketplace`, or empty for injected fraud |
| is_fraud | Injected event label |
| variant_id | MM-V1–V4 for injected events; empty for legitimate events |
| ring_id | Injection group; never use as a model feature |
| hop_level | Injection hop; never use as a model feature |

The injector reads `simulation_config` from MM-001 in `identify/attacks.json`. Its knobs determine fan-in/out width, dwell steps, amount range, pass-through, shared-device probability, and dormant-account preparation. The generator is deterministic for a fixed seed. The features intentionally exclude `variant_id`, `ring_id`, `hop_level`, and `lookalike_type`.
