import os, sys
import pandas as pd


HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, '..', 'adv_crim'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import map_cluster as mc
from insights import add_anomaly_score


def test_unknown_rate_and_top1_label():
    s = pd.Series(['Acquaintance', 'Unknown', 'Not determined', 'Undetermined', 'Friend'])
    rate = mc._unknown_rate(s)
    assert 0.39 <= rate <= 0.61  # 3/5 unknown-like
    top1 = mc._top1_label(s)
    assert top1 in ('Acquaintance', 'Friend')


def test_anomaly_score_basic():
    df = pd.DataFrame({
        'PERCENT': [0.10, 0.50],
        'TOTAL': [100, 10],
        'REPORT_GAP_IDX': [0.8, 0.0],
    })
    out = add_anomaly_score(df)
    assert 'anomaly_score' in out.columns
    assert out['anomaly_score'].iloc[0] > out['anomaly_score'].iloc[1]


