import os, sys, tempfile
import pandas as pd

HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, '..', 'adv_crim'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reporting import write_report


def _make_view():
    return pd.DataFrame({
        'MURDGRP': [1,2,3],
        'SEX': [2,2,2],
        'MSA_LABEL': ['A','B','C'],
        'WEAPON_LABEL': ['X','Y','Z'],
        'TOTAL': [20, 15, 12],
        'SOLVED': [4, 6, 5],
        'PERCENT': [0.20, 0.40, 0.42],
        'UNSOLVED': [16, 9, 7],
        'REPORT_GAP_IDX': [0.7, 0.2, 0.8],
    })


def test_write_markdown(tmp_path):
    view = _make_view()
    outdir = tmp_path
    p = write_report(view, 'msa', str(outdir), fmt='md', title='T')
    assert os.path.exists(p)
    with open(p, 'r', encoding='utf-8') as f:
        txt = f.read()
    assert 'Analyst Insights' in txt


def test_write_html(tmp_path):
    view = _make_view()
    outdir = tmp_path
    p = write_report(view, 'msa', str(outdir), fmt='html', title='T')
    assert os.path.exists(p)
    with open(p, 'r', encoding='utf-8') as f:
        txt = f.read()
    assert '<h2>Analyst Insights</h2>' in txt


def test_write_csv(tmp_path):
    view = _make_view()
    outdir = tmp_path
    p = write_report(view, 'msa', str(outdir), fmt='csv', title='T')
    assert os.path.exists(p)
    # also sidecar insights
    side = os.path.splitext(p)[0] + '_insights.txt'
    assert os.path.exists(side)


