import io
from fastapi.testclient import TestClient
from api import app


def test_mm_endpoints_return_observed_graph_only():
    client = TestClient(app)
    assert client.get('/mm/graph/not-present').json()['found'] is False
    response = client.post('/mm/scan', json={
        'transfer_id': 'API-MM-1', 'timestamp': 1, 'sender': 'API-A',
        'receiver': 'API-B', 'amount': 10})
    assert response.status_code == 200
    result = response.json()
    assert set(result['sub_scores']) == {'hdc', 'xgb', 'behaviour', 'anomaly'}
    assert client.get('/mm/graph/API-A').json()['found'] is True
    assert client.get('/mm/results').status_code == 200
    assert client.get('/mm/audit-log').json()['records']


def test_mm_probe_and_legacy_transfer():
    client = TestClient(app)
    csv = b'TX_ID,SENDER_ACCOUNT_ID,RECEIVER_ACCOUNT_ID,TX_AMOUNT,TIMESTAMP,IS_FRAUD\n1,A,B,10,0,False\n'
    response = client.post('/mm/dataset/probe', files={'file': ('small.csv', io.BytesIO(csv), 'text/csv')})
    assert response.status_code == 200
    assert response.json()['candidate_column_map']['sender'] == 'SENDER_ACCOUNT_ID'
    fields = {k: .1 for k in ('fan_out_degree', 'fan_in_degree', 'transit_velocity_sec',
                              'amount_layering_ratio', 'shared_device_cluster', 'account_dormancy_score')}
    assert client.post('/scan-transfer', json=fields).status_code == 200
