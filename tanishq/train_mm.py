"""Train/evaluate MM HDC and XGBoost from raw transfers.

Run from tanishq/: python train_mm.py --config mm_config.json --data "../dataset MM/transactions.csv"
The transaction alert ID is intentionally excluded from features; it encodes the answer.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_recall_curve, precision_score, recall_score, roc_auc_score, roc_curve)
from xgboost import XGBClassifier
from hdc.encoder import HDCEncoder
from hdc.model import HDCClassifier
from pipeline.mm_feature_engineer import MMFeatureEngineer, SIGNALS
from pipeline.mm_loader import load_config, load_transfers
from defend.mm_behaviour import score_matrix as behaviour_scores
from defend.mm_anomaly import MMAnomaly
from defend.risk_engine import RiskEngine

ROOT = Path(__file__).parent


def save_plots(result, output_json):
    """Render held-out ROC/PR curves and confusion counts from saved predictions."""
    if not result.get("metrics"):
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for kind in ("pr", "roc"):
        fig, ax = plt.subplots(figsize=(6, 4))
        for model, curves in result["curves"].items():
            pairs = curves[kind]
            ax.plot([p[0] for p in pairs], [p[1] for p in pairs], label=model.upper())
        ax.set(xlabel="Recall" if kind == "pr" else "False positive rate",
               ylabel="Precision" if kind == "pr" else "True positive rate",
               title=f"Held-out MM {kind.upper()} curve")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_json.with_name(output_json.stem + f"_{kind}.png"), dpi=150)
        plt.close(fig)
    fig, ax = plt.subplots(figsize=(4, 4))
    cm = np.array(result["metrics"]["fused"]["confusion_matrix"])
    ax.imshow(cm, cmap="Blues")
    for (i, j), count in np.ndenumerate(cm):
        ax.text(j, i, f"{count:,}", ha="center", va="center")
    ax.set(xticks=[0,1], yticks=[0,1], xlabel="Predicted", ylabel="Actual", title="Held-out fused confusion matrix")
    fig.tight_layout()
    fig.savefig(output_json.with_name(output_json.stem + "_confusion.png"), dpi=150)
    plt.close(fig)


def hdc_scores(encoder, classifier, x, batch=512):
    scores = []
    for start in range(0, len(x), batch):
        scores.append(classifier.get_fraud_score(encoder.encode_batch(x[start:start+batch])))
    return np.concatenate(scores) if scores else np.array([])


def fuse(hdc, xgb, behaviour, anomaly):
    """Half HDC plus half existing RiskEngine's 40/30/30 component blend."""
    weights = RiskEngine().weights
    return (.5*hdc + .5*(weights["xgb"]*xgb +
                         weights["behaviour"]*behaviour + weights["anomaly"]*anomaly))


def metrics(y, scores, threshold=0.5):
    pred = scores >= threshold
    d = {"n": int(len(y)), "fraud_n": int(y.sum()), "threshold": float(threshold),
         "precision": float(precision_score(y, pred, zero_division=0)),
         "recall": float(recall_score(y, pred, zero_division=0)),
         "f1": float(f1_score(y, pred, zero_division=0)),
         "pr_auc": float(average_precision_score(y, scores)) if len(np.unique(y)) == 2 else None,
         "roc_auc": float(roc_auc_score(y, scores)) if len(np.unique(y)) == 2 else None,
         "confusion_matrix": confusion_matrix(y, pred, labels=[0, 1]).tolist()}
    if len(np.unique(y)) == 2:
        p, r, _ = precision_recall_curve(y, scores)
        d["recall_at_90pct_precision"] = float(max(r[p >= .9], default=0))
    return d


def choose_threshold(y, s):
    if len(np.unique(y)) < 2:
        return .5
    p, r, thresholds = precision_recall_curve(y, s)
    f = 2*p[:-1]*r[:-1] / np.maximum(p[:-1]+r[:-1], 1e-12)
    return float(thresholds[np.argmax(f)]) if len(thresholds) else .5


def sample_train(y, max_rows, seed):
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(y == 1)
    neg = np.flatnonzero(y == 0)
    if len(pos) > max_rows // 2:
        pos = rng.choice(pos, max_rows // 2, replace=False)
    n_neg = min(len(neg), max_rows-len(pos))
    return np.sort(np.r_[pos, rng.choice(neg, n_neg, replace=False)])


def run(cfg, path, alerts_path=None):
    started = time.perf_counter()
    eng = MMFeatureEngineer(cfg)
    feature_parts, label_parts, time_parts, id_parts, variant_parts = [], [], [], [], []
    sender_parts, receiver_parts, amount_parts = [], [], []
    last_t = -float("inf")
    for chunk in load_transfers(path, cfg):
        if (chunk["time_value"].diff().dropna() < 0).any() or chunk["time_value"].iloc[0] < last_t:
            raise ValueError("Input must be chronological. Sort by timestamp and transfer_id before training.")
        last_t = float(chunk["time_value"].iloc[-1])
        feature_parts.append(eng.transform(chunk).to_numpy(dtype=np.float32))
        time_parts.append(chunk["time_value"].to_numpy(dtype=np.float64))
        id_parts.append(chunk["transfer_id"].astype(str).to_numpy())
        sender_parts.append(chunk["sender"].astype(str).to_numpy())
        receiver_parts.append(chunk["receiver"].astype(str).to_numpy())
        amount_parts.append(chunk["amount"].to_numpy(dtype=np.float32))
        if "variant" in chunk:
            variant_parts.append(chunk["variant"].fillna("").astype(str).to_numpy())
        if "label" in chunk:
            label_parts.append(chunk["label"].to_numpy(dtype=np.int8))
    x = np.concatenate(feature_parts)
    t = np.concatenate(time_parts)
    ids = np.concatenate(id_parts)
    senders = np.concatenate(sender_parts)
    receivers = np.concatenate(receiver_parts)
    amounts = np.concatenate(amount_parts)
    variants = np.concatenate(variant_parts) if variant_parts else None
    y = np.concatenate(label_parts) if label_parts else None
    if cfg["mode"] == "zero-shot":
        y = None
    notes = ["Features are calculated from prior and current transfers only."]
    if not cfg["column_map"].get("device_id"):
        notes.append("No device ID: shared_device_cluster is zero for every row.")
    if not cfg.get("currency_threshold"):
        notes.append("No currency threshold: amount_layering_ratio uses pass-through only; structuring is unavailable.")
    if cfg["time_unit"] == "steps" and cfg.get("seconds_per_step") is None:
        notes.append("Unknown step duration: transit and dormancy use relative steps, not seconds/days.")
    if y is None and cfg["mode"] != "zero-shot":
        raise ValueError("No label column: set mode=zero-shot and use a pretrained model")
    low, high = np.quantile(t, [.7, .85])
    train = t <= low
    val = (t > low) & (t <= high)
    test = t > high
    if cfg["mode"] == "zero-shot":
        test = np.ones(len(t), dtype=bool)
    elif not train.any() or not val.any() or not test.any():
        raise ValueError("At least three distinct time periods are needed for train/validation/test")
    model_dir = ROOT / cfg.get("model_dir", "models")
    model_dir.mkdir(parents=True, exist_ok=True)
    dim = int(cfg.get("hdc_dim", 2048))
    encoder = HDCEncoder(dim=dim, num_levels=100, num_signals=6, seed=cfg.get("seed", 42))
    hdc = HDCClassifier(dim=dim)
    xgb = XGBClassifier()
    if cfg["mode"] == "zero-shot":
        saved = np.load(model_dir / "hdc_mm_prototypes.npz")
        hdc.prototypes = saved["prototypes"]
        hdc.threshold = float(saved["threshold"][0])
        hdc.is_trained = True
        xgb.load_model(str(model_dir / "xgb_mm_model.json"))
        anomaly = MMAnomaly.load(model_dir)
    else:
        pretrained = None
        if cfg["mode"] == "finetune":
            pretrained = ROOT / cfg.get("pretrained_model_dir", "models/synthetic_mm")
            if not (pretrained / "xgb_mm_model.json").exists():
                raise ValueError(f"Missing source model: {pretrained}")
            source = np.load(pretrained / "hdc_mm_prototypes.npz")
            if source["prototypes"].shape != hdc.prototypes.shape:
                raise ValueError("Pretrained HDC dimension differs from target configuration")
            hdc.prototypes[:] = source["prototypes"]
        tr = np.flatnonzero(train)
        selected = tr[sample_train(y[train], int(cfg.get("max_train_rows", 30000)), cfg.get("seed", 42))]
        if len(np.unique(y[selected])) < 2:
            raise ValueError("Training period must contain both classes")
        # HDC class prototypes are sums of encoded sample vectors; only one batch is held in memory.
        for start in range(0, len(selected), 512):
            ix = selected[start:start+512]
            hv = encoder.encode_batch(x[ix])
            for cls in (0, 1):
                hdc.prototypes[cls] += hv[y[ix] == cls].sum(axis=0)
        hdc.is_trained = True
        xgb = XGBClassifier(n_estimators=140, max_depth=4, learning_rate=.06,
                            subsample=.85, colsample_bytree=.9, tree_method="hist",
                            scale_pos_weight=max(1, int((y[selected] == 0).sum()/max(1, (y[selected] == 1).sum()))),
                            random_state=cfg.get("seed", 42), n_jobs=4, eval_metric="logloss")
        xgb.fit(x[selected], y[selected],
                xgb_model=str(pretrained / "xgb_mm_model.json") if pretrained else None)
        xgb.save_model(str(model_dir / "xgb_mm_model.json"))
        anomaly = MMAnomaly().fit(x[selected[y[selected] == 0]], cfg.get("seed", 42))
        anomaly.save(model_dir)
        np.savez_compressed(model_dir / "hdc_mm_prototypes.npz", prototypes=hdc.prototypes,
                            threshold=np.array([hdc.threshold]))
        (model_dir / "hdc_mm_encoder_meta.json").write_text(json.dumps({"dim": dim, "num_levels": 100, "seed": cfg.get("seed", 42), "signals": SIGNALS}, indent=2))
    if y is None:
        hs = hdc_scores(encoder, hdc, x[test])
        xs = xgb.predict_proba(x[test])[:, 1]
        fused = fuse(hs, xs, behaviour_scores(x[test]), anomaly.score(x[test]))
        top = np.argsort(fused)[-20:][::-1]
        result = {"mode": "zero-shot", "label_status": "unlabeled; no accuracy claim possible",
                  "n_scored": int(test.sum()), "score_quantiles": np.quantile(fused, [0,.5,.9,.99,1]).tolist(),
                  "top_transfers": [{"transfer_id": str(ids[np.flatnonzero(test)[i]]), "risk_score": float(fused[i])} for i in top],
                  "notes": notes}
        import networkx as nx
        g = nx.Graph()
        chosen = np.argsort(fused)[-min(2000, len(fused)):]
        for i in chosen:
            g.add_edge(senders[i], receivers[i], risk=float(fused[i]))
        clusters = []
        for component in nx.connected_components(g):
            if len(component) < 3:
                continue
            sub = g.subgraph(component)
            clusters.append({"accounts": sorted(component)[:30], "account_count": len(component),
                             "max_edge_risk": max(d["risk"] for _, _, d in sub.edges(data=True))})
        result["top_suspicious_components"] = sorted(clusters, key=lambda c: c["max_edge_risk"], reverse=True)[:10]
        notes.append("Suspicious components use observed transfer edges among the top-scored rows; they are leads, not confirmed rings.")
    else:
        vi = np.flatnonzero(val)
        ti = np.flatnonzero(test)
        hv = hdc_scores(encoder, hdc, x[vi])
        xv = xgb.predict_proba(x[vi])[:, 1]
        bv = behaviour_scores(x[vi])
        av = anomaly.score(x[vi])
        vt = {"hdc": choose_threshold(y[vi], hv), "xgb": choose_threshold(y[vi], xv),
              "fused": choose_threshold(y[vi], fuse(hv,xv,bv,av))}
        start_pred = time.perf_counter()
        ht = hdc_scores(encoder, hdc, x[ti])
        xt = xgb.predict_proba(x[ti])[:, 1]
        bt = behaviour_scores(x[ti])
        at = anomaly.score(x[ti])
        pred_sec = time.perf_counter()-start_pred
        scores = {"hdc": ht, "xgb": xt, "fused": fuse(ht,xt,bt,at)}
        result = {"mode": "train", "source": str(path), "n_total": len(x),
                  "split": {"train": int(train.sum()), "validation": int(val.sum()), "test": int(test.sum()),
                            "train_last_time": float(low), "validation_last_time": float(high)},
                  "metrics": {k: metrics(y[ti], s, vt[k]) for k, s in scores.items()},
                  "latency_ms_per_transfer": 1000*pred_sec/len(ti), "notes": notes,
                  "feature_names": list(SIGNALS),
                  "fusion_weights": {"hdc": .5, "xgb": .2, "behaviour": .15, "anomaly": .15}}
        top = np.argsort(scores["fused"])[-100:][::-1]
        rng = np.random.default_rng(cfg.get("seed", 42))
        normal = np.flatnonzero(y[ti] == 0)
        sampled_normal = rng.choice(normal, size=min(100, len(normal)), replace=False)
        chosen = np.r_[top, sampled_normal]
        result["scored_sample"] = [{"transfer_id": str(ids[ti[j]]), "timestamp": float(t[ti[j]]),
             "sender": str(senders[ti[j]]), "receiver": str(receivers[ti[j]]),
             "amount": float(amounts[ti[j]]), "risk_score": float(scores["fused"][j]),
             "is_fraud": bool(y[ti[j]]), "signals": dict(zip(SIGNALS, map(float, x[ti[j]])))}
             for j in chosen]
        # Curves come from actual held-out predictions. Downsample only the points saved.
        result["curves"] = {}
        for k, s in scores.items():
            p, r, _ = precision_recall_curve(y[ti], s)
            fpr, tpr, _ = roc_curve(y[ti], s)
            result["curves"][k] = {"pr": list(zip(p[::max(1,len(p)//300)].tolist(), r[::max(1,len(r)//300)].tolist())),
                                    "roc": list(zip(fpr[::max(1,len(fpr)//300)].tolist(), tpr[::max(1,len(tpr)//300)].tolist()))}
        if variants is not None:
            result["per_variant_detection"] = {}
            for name in sorted(set(variants[ti]) - {"", "nan", "None"}):
                mask = variants[ti] == name
                result["per_variant_detection"][name] = {"count": int(mask.sum()),
                    "recall": float(np.mean(scores["fused"][mask] >= vt["fused"]))}
        if alerts_path:
            alerts = pd.read_csv(alerts_path, usecols=["TX_ID", "ALERT_TYPE"])
            lookup = dict(zip(alerts.TX_ID.astype(str), alerts.ALERT_TYPE))
            result["observed_alert_types"] = {}
            for subtype in sorted(set(lookup.values())):
                mask = np.array([lookup.get(v) == subtype for v in ids[ti]])
                result["observed_alert_types"][subtype] = {"count": int(mask.sum()),
                    "recall": float(np.mean(scores["fused"][mask] >= vt["fused"])) if mask.any() else None}
            notes.append("Alert types are evaluation labels only; cycle and fan_in are the only supplied subtypes.")
    result["runtime_sec"] = round(time.perf_counter()-started, 2)
    out = ROOT / cfg.get("results_path", "results/mm_results.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    save_plots(result, out)
    print(json.dumps({k: v for k, v in result.items() if k != "curves"}, indent=2))
    print(f"Saved {out}")
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="mm_config.json")
    ap.add_argument("--data", required=True)
    ap.add_argument("--alerts")
    args = ap.parse_args()
    run(load_config(args.config), args.data, args.alerts)
