import pandas as pd
from pipeline.mm_feature_engineer import MMFeatureEngineer, SIGNALS
from pipeline.mm_loader import load_transfers, probe
from response.mm_graph_engine import MMGraph


CFG = {"time_unit": "steps", "seconds_per_step": None, "short_window_steps": 2,
       "long_window_steps": 10, "dormancy_steps": 5, "currency_threshold": None}


def test_future_rows_do_not_change_past_features():
    past = pd.DataFrame([
        {"sender": "a", "receiver": "b", "amount": 10, "time_value": 0},
        {"sender": "b", "receiver": "c", "amount": 9, "time_value": 1},
    ])
    future = pd.DataFrame([
        {"sender": "c", "receiver": "a", "amount": 8, "time_value": 3},
        {"sender": "a", "receiver": "d", "amount": 7, "time_value": 4},
    ])
    baseline = MMFeatureEngineer(CFG).transform(past)
    with_future = MMFeatureEngineer(CFG).transform(pd.concat([past, future], ignore_index=True))
    shuffled_future = MMFeatureEngineer(CFG).transform(pd.concat([past, future.iloc[::-1]], ignore_index=True))
    pd.testing.assert_frame_equal(baseline, with_future.iloc[:2])
    pd.testing.assert_frame_equal(baseline, shuffled_future.iloc[:2])
    assert ((with_future[list(SIGNALS)] >= 0) & (with_future[list(SIGNALS)] <= 1)).all().all()


def test_paysim_and_ibm_shapes(tmp_path):
    pay = tmp_path / "paysim.csv"
    pay.write_text("step,type,amount,nameOrig,oldbalanceOrg,newbalanceOrig,nameDest,oldbalanceDest,newbalanceDest,isFraud\n"
                   "0,TRANSFER,100,C1,100,0,C2,0,100,0\n1,TRANSFER,95,C2,100,5,C3,0,95,1\n")
    ibm = tmp_path / "ibm.csv"
    ibm.write_text("Timestamp,From Bank,Account,To Bank,Account.1,Amount Received,Receiving Currency,Payment Format,Is Laundering\n"
                   "2025-01-01 00:00:00,1,A,2,B,100,USD,ACH,0\n2025-01-01 01:00:00,2,B,3,C,95,USD,ACH,1\n")
    for path, time_unit in ((pay, "steps"), (ibm, "ISO string")):
        mapping = probe(path)["candidate_column_map"]
        cfg = {"column_map": mapping, "time_unit": time_unit, "seconds_per_step": 3600,
               "label_positive_values": [1, "1", True]}
        d = pd.concat(list(load_transfers(path, cfg)), ignore_index=True)
        assert len(d) == 2 and d.label.tolist() == [0, 1]
        if path == ibm:
            assert d.sender.tolist() == ["1:A", "2:B"]
        feats = MMFeatureEngineer({**CFG, "time_unit": time_unit, "seconds_per_step": 3600,
                                   "short_window_sec": 7200, "long_window_days": 1, "dormancy_days": 1}).transform(d)
        assert feats.shape == (2, 6)


def test_graph_has_no_fabricated_cluster():
    g = MMGraph()
    assert g.get_mule_cluster("unknown") == {"found": False, "account": "unknown", "nodes": [], "links": [], "rings": []}
    g.add_transfer("t1", "a", "b", 10, .8, "HOLD_TRANSFER")
    g.add_transfer("t2", "b", "a", 9, .9, "FREEZE_RECEIVER")
    observed = g.get_mule_cluster("a")
    assert observed["found"] and observed["rings"]
