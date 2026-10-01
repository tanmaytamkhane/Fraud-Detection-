# Money Movement ML: current workflow

## What the supplied files support

`dataset MM/transactions.csv` has 1,323,234 transfers over integer steps 0–199; 1,719 are marked fraud (0.130%). `alerts.csv` joins those 1,719 IDs and contains 783 `fan_in` and 936 `cycle` alert types. `accounts.csv` has 10,000 accounts, but its account-level `IS_FRAUD` is not used as a transaction feature. The source is AMLSim-like by schema, but its exact download/generation provenance remains unverified.

The user-supplied `dataset MM/` directory stays local and is excluded from GitHub because provenance and redistribution rights are unconfirmed. After cloning, place the three CSVs under `dataset MM/` before reproducing the real-data training run. The included synthetic fixtures and simulator remain available without that dataset.

The file has no device/IP, currency, withdrawal channel, or timestamp-step duration. Accordingly, shared-device is zero, currency-threshold structuring is unavailable, and dwell/dormancy are measured in steps. **Do not present the supplied file as evidence of MM-V1 cash-out or MM-V4 dormant mule performance.** `ALERT_ID`, alert type, account `IS_FRAUD`, ring IDs, and future activity are excluded from training features.

## Reproduce training

From `tanishq/`:

```powershell
python -m pipeline.mm_loader --probe "../dataset MM/transactions.csv"
python train_mm.py --config mm_config.json --data "../dataset MM/transactions.csv" --alerts "../dataset MM/alerts.csv"
python -m simulate.mm_simulator
python train_mm.py --config mm_synthetic_config.json --data simulate/mm_raw_dataset.csv
python -m pytest -q
```

The probe creates `mm_config.draft.json` for human confirmation. For a teammate's data, copy it to a project-specific config and confirm the sender, receiver, amount, timestamp, and label fields. If `TIMESTAMP` is a step, get its duration from the generating system and set `seconds_per_step`; until then, leave it null and choose windows in steps. Set the reporting/structuring threshold only after confirming currency and jurisdiction. For unlabeled data, set `mode` to `zero-shot` and remove the `label` mapping; the output contains score distribution and top transfers, with no accuracy claim.

## Feature definitions

All features are computed sequentially from transfers up to and including the current row, sorted by timestamp and ID. `fan_out_degree = 1−exp(−distinct_recent_receivers/4)`. `fan_in_degree = 1−exp(−distinct_recent_senders/4)`. `transit_velocity_sec = exp(−dwell/short_window)` where dwell is in configured time units. `amount_layering_ratio` is capped recent outbound/inbound amount, averaged with the within-band fraction only when a currency threshold is known. `shared_device_cluster = 1−exp(−(accounts_on_device−1)/3)`, or zero when device ID is absent. `account_dormancy_score = 1−exp(−largest_prior_activity_gap/dormancy_window)`. Fixed squashing constants avoid fitting normalization on later rows. The `transit_velocity_sec` name is retained for compatibility even when physical seconds are unknown.

Chronological split: train through step 140, validation through 170, test after 170. All fraud in the train period plus a seeded normal sample of up to 30,000 total train rows fit the models. Class weighting affects XGBoost training only. Thresholds are chosen on validation. Metrics and ROC/PR points come from the untouched test period. Saved models are `models/hdc_mm_prototypes.npz`, `models/hdc_mm_encoder_meta.json`, and `models/xgb_mm_model.json`.

The final MM score is 50% HDC plus 50% of the existing `RiskEngine` component blend (40% XGBoost, 30% behaviour, 30% anomaly), so total weights are 50%, 20%, 15%, and 15%. The anomaly component is an Isolation Forest percentile fitted to normal training examples; it is not a calibrated fraud probability. The behaviour component is a transparent rule score. Fused scores are therefore research ranking scores; action tiers are demo policy outputs and require calibration and analyst review before operational use.

## Measured outcome and next data

See `results/mm_results.json` for exact, reproducible numbers. The current raw-data model has low precision and PR-AUC. It is a research baseline, not a production decision system. The synthetic-world result in `results/mm_synthetic_results.json` is a separate simulator check with a much higher fraud prevalence and must not be compared as a real-world accuracy estimate.

The next data request should include: provenance/license, step duration and timezone, currency and jurisdiction, device/IP where permitted, cash-out/withdrawal events, account history long enough for dormancy, case-level verified labels for cash-out and mule chains, and a definition of whether labels mark a transfer, account, or complete ring. Keep a later temporal holdout and, ideally, a different generator or institution for external validation. Public options include [IBM AMLSim](https://github.com/IBM/AMLSim) for graph patterns, [IBM AML-Data](https://github.com/IBM/AML-Data) for synthetic laundering transfers, and [PaySim's original paper](https://www.msc-les.org/proceedings/emss/2016/EMSS2016_249.pdf) for mobile-money cash-out behavior. Their labels describe different tasks and should not be merged without remapping.

The UI Dataset Lab accepts CSVs up to 150 MB for training; jobs and uploaded files are local to the running backend process. Use the CLI for larger inputs. Its in-memory job state and online feature history are not durable across server restarts.

## Current measured results

On the supplied file's 193,281-transfer chronological test split (266 labeled fraud), fused precision is **3.71%**, recall **21.43%**, PR-AUC **2.05%**, and ROC-AUC **90.79%**. XGBoost alone has higher PR-AUC (**2.33%**) and recall (**31.20%**) than the proposed fusion. The fused score must not be advertised as an improvement. The test prevalence is about 0.138%, so ROC-AUC alone is misleading for operational use. The `cycle` and `fan_in` labels are the only observed subtypes; their fused recalls are 22.14% and 20.74%, respectively. No subtype metric proves cash-out or dormant-mule detection.

On the separate synthetic generator, fused PR-AUC is 63.78% and recall is 65.67%, at a far higher simulated fraud prevalence. These figures check that the pipeline responds to injected patterns; they are not an external validation result. The saved zero-shot run contains ranked cases without any accuracy metrics.

`python -m simulate.mm_red_team --attempts 50` wrote `results/mm_red_team.json` with 50 rings per variant and perturbation level. At full perturbation, the reported evasion rates are 0% for V1–V3 and 4% for V4. **Do not interpret this as adversarial robustness:** the same simulator supplies both training and attacks, and a dense background graph can cause broad `BLOCK_CHAIN` escalation. Review legitimate-transfer false positives and tighten cycle evidence before treating this as a decision policy. No adversarial retraining comparison has been completed.

## Practical next sequence

1. Confirm the uploaded files' provenance and license, the duration of one timestamp step, currency, and which fraud labels were independently verified. Keep `seconds_per_step` and `reporting_threshold` null until the answers are known.
2. Obtain transactions with actual withdrawal/cash-out events, account age and prior activity, and device/IP if permitted. Ask for case-level links between transfers and mule networks. Separate confirmed types from analyst hypotheses.
3. Use Dataset Lab to probe the column mapping, then train in a separate project config. Preserve the chronological holdout and compare HDC, XGBoost, and fusion on PR-AUC, recall at a fixed review capacity, and false-positive burden. Do not tune on test.
4. Use the raw-event Generator and MM Red Team pages to study failure modes. Add legitimate payroll, marketplace, and high-degree-business examples, especially when testing graph escalation.
5. Before any real intervention, calibrate scores and actions on independently labeled data, evaluate by time and institution, measure analyst workload, and require analyst review for account-level or chain-level actions.
