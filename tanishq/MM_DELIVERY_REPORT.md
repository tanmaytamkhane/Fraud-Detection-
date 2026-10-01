# MM-001 delivery and verification

This is a research baseline built from the supplied transfer CSVs. Read [MM_TRAINING_GUIDE.md](MM_TRAINING_GUIDE.md) for the commands, feature formulas, and teammate data intake procedure.

## What the files actually establish

- 1,323,234 transactions; 1,719 labeled fraud (0.130%). The alert file links every fraud transfer and calls 936 `cycle` and 783 `fan_in`. The account file has 10,000 accounts.
- The exact source and timestamp-step duration are unknown. The schema resembles AMLSim; that resemblance is not proof of provenance. The uploaded data has no device, IP, currency, or cash-out event.
- The original XGBoost model file was missing and the detector had a hardcoded comparison fallback. `/scan-transfer` raised a TypeError on its transfer ID. MM features, graph, stream, and presets were substantially precomputed or simulated. The old HDC prototype file did exist, contrary to one possible inference from the prompt.
- ATO and the other category implementation files were not edited. The ATO contract was kept intact; a separate `mm_contract.json` was added because the shared contract file describes ATO fields.

## Measured results

The chronological held-out split is 193,281 transfers with 266 labeled fraud. A score is a ranking score, not a calibrated fraud probability.

| Model | Precision | Recall | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|
| HDC | 3.12% | 15.04% | 1.53% | 84.63% |
| XGBoost | 3.52% | 31.20% | 2.33% | 93.47% |
| Fusion | 3.71% | 21.43% | 2.05% | 90.79% |

The synthetic-world test has 3,371 transfers and 134 injected fraud transfers. Fusion PR-AUC is 63.78% and recall 65.67%; this is a simulator check and cannot substitute for external validation. The PaySim-like and IBM-like fixture trainings only prove schema adaptation. The zero-shot fixture run emits ranked cases with no accuracy claim.

The five-level red-team sweep used 50 injected rings per variant per level. At maximum perturbation, V1–V3 show 0% evasion and V4 4%, but a dense background graph can trigger broad chain actions. The result is **not** evidence of robust detection. No adversarial retraining comparison was run.

## Verification

- `python -m pytest -q`: 18 passed, one Starlette TestClient deprecation warning.
- `python -X utf8 -m identify.registry`: all data valid and all registry self-tests passed.
- `npm run build`: passed. Vite reported a bundle size warning.
- Live API: real dataset probe returned the expected eight columns and draft mapping; a zero-shot upload job completed without accuracy metrics; `/mm/scan`, `/mm/generate`, `/mm/results`, `/mm/stream`, `/mm/rings`, `/mm/audit-log`, `/mm/graph/unknown` all returned 200; unknown graph returned `found:false`. Legacy `/scan-transfer` returned 200 with its six-signal request shape.
- ATO preset and SOC/PM/TB/MRF/GENAI preset routes returned 200; the prior exact output bytes were not captured, so byte-identical regression is **unverified**. Full pytest and registry checks passed.
- In the browser, Dataset Lab showed the saved real metrics, Stream replayed 200 saved scored transfers, Investigate showed an observed two-account MM graph without invented nodes, the raw MM Generator returned 12 events, and Red Team displayed the 50-ring sweep. Browser file-picker automation timed out, so actual in-browser upload was not verified; API upload was.

## Departures and remaining work

- No MM-V5 was introduced. The `cycle` label is known, but the six-feature baseline does not yet establish a reliable cycle-specific classifier.
- Currency threshold defaults to null rather than 10,000 because the currency and jurisdiction are unknown. Step windows remain in steps, not seconds or days.
- The supplied data cannot validate rapid cash-out, device sharing, or dormant-mule detection. Synthetic labels for those variants are training and demo aids only.
- The graph uses observed edges and SCCs, but its network risk is a local unweighted average rather than the requested amount/recency-weighted community model. Dense SCCs can over-escalate chain actions. This must be corrected and tested against legitimate high-degree networks before operational use.
- The SAR text is an evidence-only template, not an LLM-generated narrative. This avoids invented facts, but it does not satisfy the requested live LLM integration.
- The red team has knob perturbations and an evasion table, but no `--adversarial-retrain` before/after study. The generator UI exposes variant and attempt count; the CLI/attack definitions hold the detailed knobs.
- The Dataset Lab currently shows results and configuration, but the browser upload interaction itself remains unverified. Server jobs and feature state are in memory; restart clears them. The UI uses a 150 MB upload limit.
- The original ATO and other category code was preserved, but an exact before/after byte snapshot was not captured before changes.

## File manifest

The following lists changed and new workspace files at the time of the original build. `dataset MM/*` are user-supplied and were not edited; they are excluded from GitHub pending provenance and redistribution confirmation. Generated model, fixture, plot, and result files are included so the runs are reviewable.

- `Frontend/src/App.jsx` — Frontend MM route, API, or graph integration.
- `Frontend/src/api/client.js` — Frontend MM route, API, or graph integration.
- `Frontend/src/components/Navbar.jsx` — Frontend MM route, API, or graph integration.
- `Frontend/src/components/NetworkGraph.jsx` — Frontend MM route, API, or graph integration.
- `Frontend/src/pages/DatasetLabPage.jsx` — MM UI integration or existing page update.
- `Frontend/src/pages/DefenderPage.jsx` — MM UI integration or existing page update.
- `Frontend/src/pages/GeneratorPage.jsx` — MM UI integration or existing page update.
- `Frontend/src/pages/InvestigatePage.jsx` — MM UI integration or existing page update.
- `Frontend/src/pages/MMRedTeamPage.jsx` — MM UI integration or existing page update.
- `Frontend/src/pages/StreamPage.jsx` — MM UI integration or existing page update.
- `dataset MM/accounts.csv` — User-supplied dataset; inspected, not edited.
- `dataset MM/alerts.csv` — User-supplied dataset; inspected, not edited.
- `dataset MM/transactions.csv` — User-supplied dataset; inspected, not edited.
- `tanishq/MM_DELIVERY_REPORT.md` — Verification, deviations, and file manifest.
- `tanishq/MM_TRAINING_GUIDE.md` — Data intake, reproduction commands, and limitations.
- `tanishq/api.py` — Additive MM API routes and legacy MM endpoint repair.
- `tanishq/defend/mm_adapter.py` — MM detector, score component, scanner, or explanation.
- `tanishq/defend/mm_anomaly.py` — MM detector, score component, scanner, or explanation.
- `tanishq/defend/mm_behaviour.py` — MM detector, score component, scanner, or explanation.
- `tanishq/defend/mm_explain.py` — MM detector, score component, scanner, or explanation.
- `tanishq/defend/mm_scanner.py` — MM detector, score component, scanner, or explanation.
- `tanishq/defend/mule_detector.py` — MM detector, score component, scanner, or explanation.
- `tanishq/identify/MM_RESEARCH.md` — MM taxonomy, contract, or research.
- `tanishq/identify/attacks.json` — MM taxonomy, contract, or research.
- `tanishq/identify/mm_contract.json` — MM taxonomy, contract, or research.
- `tanishq/identify/taxonomy.json` — MM taxonomy, contract, or research.
- `tanishq/mm_config.json` — Dataset mapping, feature windows, or training configuration.
- `tanishq/mm_synthetic_config.json` — Dataset mapping, feature windows, or training configuration.
- `tanishq/models/fixture_ibm/hdc_mm_encoder_meta.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_ibm/hdc_mm_prototypes.npz` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_ibm/mm_anomaly.joblib` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_ibm/mm_anomaly_quantiles.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_ibm/xgb_mm_model.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_paysim/hdc_mm_encoder_meta.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_paysim/hdc_mm_prototypes.npz` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_paysim/mm_anomaly.joblib` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_paysim/mm_anomaly_quantiles.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/fixture_paysim/xgb_mm_model.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/hdc_mm_encoder_meta.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/hdc_mm_prototypes.npz` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/mm_anomaly.joblib` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/mm_anomaly_quantiles.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/synthetic_mm/hdc_mm_encoder_meta.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/synthetic_mm/hdc_mm_prototypes.npz` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/synthetic_mm/mm_anomaly.joblib` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/synthetic_mm/mm_anomaly_quantiles.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/synthetic_mm/xgb_mm_model.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/models/xgb_mm_model.json` — Persisted trained model or encoder/anomaly metadata.
- `tanishq/pipeline/mm_feature_engineer.py` — Dataset adapter, schema, causal feature engineering, or variant hint.
- `tanishq/pipeline/mm_loader.py` — Dataset adapter, schema, causal feature engineering, or variant hint.
- `tanishq/pipeline/mm_schema.py` — Dataset adapter, schema, causal feature engineering, or variant hint.
- `tanishq/pipeline/mm_variant_labeler.py` — Dataset adapter, schema, causal feature engineering, or variant hint.
- `tanishq/response/mm_engine.py` — Observed graph, MM decisions, or evidence-only SAR draft.
- `tanishq/response/mm_graph_engine.py` — Observed graph, MM decisions, or evidence-only SAR draft.
- `tanishq/response/mm_sar.py` — Observed graph, MM decisions, or evidence-only SAR draft.
- `tanishq/results/mm_fixture_ibm_results.json` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_ibm_results_confusion.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_ibm_results_pr.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_ibm_results_roc.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_ibm_stdout.txt` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_paysim_results.json` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_paysim_results_confusion.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_paysim_results_pr.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_paysim_results_roc.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_fixture_paysim_stdout.txt` — Measured run result, chart, or execution log.
- `tanishq/results/mm_red_team.json` — Measured run result, chart, or execution log.
- `tanishq/results/mm_red_team_stdout.txt` — Measured run result, chart, or execution log.
- `tanishq/results/mm_results.json` — Measured run result, chart, or execution log.
- `tanishq/results/mm_results_confusion.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_results_pr.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_results_roc.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_synthetic_results.json` — Measured run result, chart, or execution log.
- `tanishq/results/mm_synthetic_results_confusion.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_synthetic_results_pr.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_synthetic_results_roc.png` — Measured run result, chart, or execution log.
- `tanishq/results/mm_synthetic_training_stdout.txt` — Measured run result, chart, or execution log.
- `tanishq/results/mm_training_stdout.txt` — Measured run result, chart, or execution log.
- `tanishq/results/mm_zero_shot_results.json` — Measured run result, chart, or execution log.
- `tanishq/simulate/MM_DATA_DICTIONARY.md` — Synthetic account world, attack injection, stress test, or validation artifact.
- `tanishq/simulate/mm_raw_dataset.csv` — Synthetic account world, attack injection, stress test, or validation artifact.
- `tanishq/simulate/mm_red_team.py` — Synthetic account world, attack injection, stress test, or validation artifact.
- `tanishq/simulate/mm_simulator.py` — Synthetic account world, attack injection, stress test, or validation artifact.
- `tanishq/simulate/mm_validation_report.json` — Synthetic account world, attack injection, stress test, or validation artifact.
- `tanishq/simulate/mm_world.py` — Synthetic account world, attack injection, stress test, or validation artifact.
- `tanishq/tests/fixtures/generate_mm_shapes.py` — Generated adapter fixture or fixture config.
- `tanishq/tests/fixtures/ibm_config.json` — Generated adapter fixture or fixture config.
- `tanishq/tests/fixtures/ibm_like.csv` — Generated adapter fixture or fixture config.
- `tanishq/tests/fixtures/mm_unlabeled_sample.csv` — Generated adapter fixture or fixture config.
- `tanishq/tests/fixtures/mm_zero_shot_config.json` — Generated adapter fixture or fixture config.
- `tanishq/tests/fixtures/paysim_config.json` — Generated adapter fixture or fixture config.
- `tanishq/tests/fixtures/paysim_like.csv` — Generated adapter fixture or fixture config.
- `tanishq/tests/test_mm_api.py` — MM regression and feature tests.
- `tanishq/tests/test_mm_features.py` — MM regression and feature tests.
- `tanishq/train_mm.py` — Chronological MM HDC/XGBoost/anomaly training and evaluation.
