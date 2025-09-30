# map_cluster.py
# Usage (baseline):  python map_cluster.py input.csv
# Examples:
#   python map_cluster.py input.csv --group msa --focus-sex male --threshold 0.25 --outdir out
#   python map_cluster.py input.csv --no-filter  # just build groups & aggregates

import argparse, re, os
import pandas as pd
import hashlib  # add
# add near imports/helpers
import re
_REL_UNK_RE = re.compile(r'unknown|not\s+determined|undetermined|unspecified|not\s+specified', re.I)

def _unknown_rate(series, pat=_REL_UNK_RE):
    s = series.astype('string')  # keeps NA
    empty_or_na = s.isna() | s.str.strip().eq('')
    hits        = s.str.contains(pat, na=False)
    return (empty_or_na | hits).mean()

def _top1_label(series, pat=_REL_UNK_RE):
    s = series.astype('string')
    known = (~s.isna()) & (~s.str.strip().eq('')) & (~s.str.contains(pat, na=False))
    vc = s[known].value_counts()
    return vc.index[0] if len(vc) else '—'


def _pos_hash8(s):  # add
    h = int(hashlib.md5(str(s).encode('utf-8')).hexdigest(), 16)
    return (h % 100_000_000) or 1  # 1..99,999,999


# --- helpers (minimal) ---
def _digits_or_zero(x):
    """Extract numeric digits from CNTYFIPS/MSA strings like '030180' or 'Anchorage, AK' -> 0."""
    if pd.isna(x): return 0
    s = ''.join(re.findall(r'\d+', str(x)))
    return int(s) if s else 0

def _victim_sex_code(v):
    """SPSS-style: 1=Male, 2=Female, 9=Unknown."""
    v = str(v).strip().upper()
    if v in ('M','MALE'): return 1
    if v in ('F','FEMALE'): return 2
    return 9

def _offender_unknown(offsex):
    """OFFSEX 'U' => unknown -> Not Solved. We also treat 'Unknown or not reported' as U."""
    v = str(offsex).strip().upper()
    return v.startswith('U')

def _weapon_code(series):
    """WEAPON numeric; FBI has codes, but CSVs often have strings. We create stable codes per file."""
    # If already numeric, keep it; else factorize strings to ints.
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).astype(int)
    codes, _ = pd.factorize(series.fillna('Unknown').astype(str), sort=True)
    return pd.Series(codes, index=series.index).astype(int)

# --- core ---
def build_groups(df, solved_source='offsex'):
    # Compute SOLVED per SPSS logic

    # REPLACE SOLVED block
    if solved_source == 'offsex':
        df['SOLVED'] = 1
        cond_unknown = df['OffSex'].astype(str).str.upper().str[0].eq('U')
        df.loc[cond_unknown, 'SOLVED'] = 0
    else:  # 'field'
        df['SOLVED'] = (df['Solved'].astype(str).str.strip().str.upper()
                        .map({'YES':1,'Y':1,'NO':0,'N':0})
                        .fillna(0).astype(int))

    # ADD year/decade
    df['YEAR_NUM'] = pd.to_numeric(df['Year'], errors='coerce')
    df['DECADE']   = ((df['YEAR_NUM'] // 10) * 10).astype('Int64')


    # Victim sex numeric
    df['SEX'] = df['VicSex'].apply(_victim_sex_code)

    # Numeric CNTY and MSA (extract digits; non-numeric -> 0)
    df['CNTY'] = df['CNTYFIPS'].apply(_digits_or_zero)
    df['MSA_NUM'] = df['MSA'].apply(_digits_or_zero)

    # Weapon numeric code (auto map if strings)
    df['WEAPON_CODE'] = _weapon_code(df['Weapon'])

    # Group IDs
    has_cnty_num = df['CNTY'] > 0
    mgrp1_numeric  = (df['CNTY'] * 1000) + (df['SEX'] * 100) + df['WEAPON_CODE']
    mgrp1_fallback = df.apply(lambda r: _pos_hash8(f"{r['CNTYFIPS']}|{r['SEX']}|{r['WEAPON_CODE']}"), axis=1)
    df['MURDGRP1']  = mgrp1_numeric.where(has_cnty_num, mgrp1_fallback)
    
    has_msa_num   = df['MSA_NUM'] > 0
    mgrp2_numeric = (df['MSA_NUM'] * 1000) + (df['SEX'] * 100) + df['WEAPON_CODE']
    mgrp2_fallback = df.apply(lambda r: _pos_hash8(f"{r['MSA']}|{r['SEX']}|{r['WEAPON_CODE']}"), axis=1)
    df['MURDGRP2'] = mgrp2_numeric.where(has_msa_num, mgrp2_fallback)
    

    return df


# change signature to accept the switch
def aggregate(df, group='county', by_decade=False, relcirc=False):

    if group == 'county':
        keys = ['MURDGRP1', 'SEX', 'CNTY_LABEL', 'WEAPON_CODE']
        gid = 'MURDGRP1'
        label_aggs = {
            'WEAPON_LABEL': ('WEAPON_LABEL', 'first'),
        }
    else:
        keys = ['MURDGRP2', 'SEX', 'MSA_LABEL', 'WEAPON_CODE']
        gid = 'MURDGRP2'
        label_aggs = {
            'WEAPON_LABEL': ('WEAPON_LABEL', 'first'),
        }

    if by_decade:
        keys = keys + ['DECADE']

    # >>> NEW: optional Relationship/Circumstance stats
    relcirc_aggs = {}
    if relcirc:
        relcirc_aggs = {
            'REL_UNK_RATE':  ('Relationship', _unknown_rate),
            'REL_TOP1':      ('Relationship', _top1_label),
            'CIRC_UNK_RATE': ('Circumstance', _unknown_rate),
            'CIRC_TOP1':     ('Circumstance', _top1_label),
        }

    g = (df.groupby(keys, dropna=False)
           .agg(TOTAL=('SOLVED','count'),
                SOLVED=('SOLVED','sum'),
                PERCENT=('SOLVED','mean'),
                **label_aggs,
                **relcirc_aggs)
           .reset_index())

    g['UNSOLVED'] = g['TOTAL'] - g['SOLVED']
    g = g.sort_values(['UNSOLVED','TOTAL'], ascending=[False, False]).reset_index(drop=True)
    g.rename(columns={gid:'MURDGRP'}, inplace=True)
    
    if relcirc:
        g['REPORT_GAP_IDX'] = (g.get('REL_UNK_RATE', 0) + g.get('CIRC_UNK_RATE', 0)) / 2
    
    
    
    
    return g

def filter_view(agg, focus_sex='female', threshold=0.33, min_total=10, min_known_rel=0.0):
    view = agg.copy()
    if focus_sex in ('male','female'):
        sex_code = 1 if focus_sex == 'male' else 2
        view = view[view['SEX'] == sex_code]
    view = view[(view['MURDGRP'] > 0) & (view['PERCENT'] <= float(threshold))]
    view = view[view['TOTAL'] >= int(min_total)]
    # apply only if column exists AND threshold > 0
    if min_known_rel > 0 and 'REL_UNK_RATE' in view.columns:
        known_share = 1 - view['REL_UNK_RATE'].fillna(0.0)
        view = view[known_share >= float(min_known_rel)]
    return view.reset_index(drop=True)

def main():
    import os
    ap = argparse.ArgumentParser(description="MAP-style clustering & solvability analysis from SHR-like CSV.")
    ap.add_argument('csv',  help='Input CSV with columns like CNTYFIPS, MSA, VicSex, OffSex, Weapon, etc.')
    ap.add_argument('--group', choices=['county','msa'], default='county', help='County (MURDGRP1) or MSA (MURDGRP2).')
    ap.add_argument('--focus-sex', choices=['female','male','all'], default='female', help='Victim sex filter per SPSS snippet.')
    ap.add_argument('--threshold', type=float, default=0.33, help='Max solved percentage to keep (≤).')
    ap.add_argument('--outdir', default='.', help='Directory for outputs.')
    ap.add_argument('--no-filter', action='store_true', help='Skip the filtering step; just emit aggregates.')
    # ADD (near other add_argument lines)
    ap.add_argument('--min-total', type=int, default=10, help='Drop clusters with TOTAL < this.')
    # argparse
    ap.add_argument('--solved-source', choices=['offsex','field'], default='field',
                    help="How to compute SOLVED...")

    ap.add_argument('--by-decade', action='store_true', help='Include DECADE in grouping.')
    ap.add_argument('--top', type=int, default=10, help='How many rows to print.')
    
    
    # add with the others
    ap.add_argument('--dump-msa', help='Exact MSA_LABEL to export (e.g., "Chicago-Naperville-Joliet, IL-IN-WI").')
    ap.add_argument('--dump-weapon', help='Exact WEAPON_LABEL to export (e.g., "Weapon Not Reported").')
    ap.add_argument('--dump-out', default='out/dump_cases.csv', help='CSV path to write case-level rows.')
    # add with your other args
    ap.add_argument('--relcirc', action='store_true',
                    help='Add Relationship/Circumstance unknown rates & top category per cluster.')
                        
    ap.add_argument('--min-known-rel', type=float, default=0.0,
                    help='Require at least this share of known Relationship (0.0–1.0).')
                        
    # with your other args
    ap.add_argument('--min-decade', type=int, default=0,
                    help='Keep only cases with DECADE >= this (e.g., 2000).')
                    



    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    df = pd.read_csv(args.csv, dtype=str, keep_default_na=False).replace({'': pd.NA})
    # after reading df
    offsex_proxy = df['OffSex'].astype(str).str.upper().str[0].eq('U').map({True:0, False:1})
    field_truth  = df['Solved'].astype(str).str.strip().str.upper().map({'YES':1,'Y':1,'NO':0,'N':0}).fillna(0).astype(int)
    mismatch = (offsex_proxy != field_truth).mean()
    if mismatch > 0.10:
        print(f"[Warn] 'OffSex' proxy disagrees with dataset 'Solved' on {mismatch:.0%} of rows; using --solved-source field.")

    # Standardize key columns if user has different casing
    required = ['CNTYFIPS','MSA','VicSex','OffSex','Weapon']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing columns: {missing}. Ensure CSV headers match or rename accordingly.")

    df = build_groups(df, solved_source=args.solved_source)
    
    # ensure labels exist (keep if you already set these earlier)
    df['CNTY_LABEL']   = df['CNTYFIPS'].astype(str).str.strip()
    df['MSA_LABEL']    = df['MSA'].astype(str).str.strip()
    df['WEAPON_LABEL'] = df['Weapon'].astype(str).str.strip()
    
        
    if args.min_decade:
        mindec = int(args.min_decade) - (int(args.min_decade) % 10)  # floor to decade
        df = df[df['DECADE'].ge(mindec)]
        print(f"[Filter] DECADE >= {mindec}: {len(df)} rows remain")   
    
    
    
    # in build_groups
    df['OffAge_num'] = pd.to_numeric(df['OffAge'], errors='coerce').replace({999: pd.NA})
    df['VicAge_num'] = pd.to_numeric(df['VicAge'], errors='coerce')

    # --- CASE-LEVEL DUMP (runs before aggregate/filter) ---
    if args.dump_msa and args.dump_weapon:
        # start from original case rows, respect focus-sex if set
        q = df.copy()
        if args.focus_sex in ('male','female'):
            q = q[q['SEX'] == (1 if args.focus_sex == 'male' else 2)]

        # match exact MSA + weapon label (case-sensitive to keep it clean)
        m_mask = q['MSA_LABEL']    == args.dump_msa
        w_mask = q['WEAPON_LABEL'] == args.dump_weapon
        q = q[m_mask & w_mask].copy()

        # light, readable column set (auto-intersect if some are missing)
        cols = [
            'ID','Year','Month','State','MSA_LABEL','CNTY_LABEL',
            'Ori','Agency','VicSex','VicAge','OffSex','OffAge',
            'Weapon','WEAPON_LABEL','Relationship','Circumstance','Subcircum','Situation',
            'Solved','SOLVED'  # dataset vs computed
        ]
        cols = [c for c in cols if c in q.columns]
        q = q[cols].sort_values(['Year','Month'], ascending=True)

        import os
        os.makedirs(os.path.dirname(args.dump_out), exist_ok=True)
        q.to_csv(args.dump_out, index=False)
        print(f"[Dump] {len(q)} case rows -> {args.dump_out}")
    
    
    
    

    agg = aggregate(df, group=args.group, by_decade=args.by_decade, relcirc=args.relcirc)
    agg_path = os.path.join(args.outdir, f'AGGREGATE_{args.group.upper()}.csv')
    
    
    
    agg.to_csv(agg_path, index=False)

    if args.no_filter:
        print(f"[OK] Aggregates written: {agg_path}")
        return

    view = filter_view(agg,
                       focus_sex=args.focus_sex,
                       threshold=args.threshold,
                       min_total=args.min_total,
                       min_known_rel=args.min_known_rel)
    
    loc_col = 'MSA_LABEL' if args.group == 'msa' else 'CNTY_LABEL'
    cols = ['MURDGRP', 'SEX', loc_col, 'WEAPON_LABEL', 'TOTAL', 'SOLVED', 'PERCENT', 'UNSOLVED']
    # optional columns (only if present)
    for c in ['DECADE','REL_UNK_RATE','REL_TOP1','CIRC_UNK_RATE','CIRC_TOP1']:
        if c in view.columns: cols.append(c)
    print(view[[c for c in cols if c in view.columns]].head(args.top).to_string(index=False))   
        
    
    
    if view.empty:
        print("[Per-weapon top (≤3 each)]\n(no rows after filtering)")
        return
        
    if args.group == 'msa':
        loc_col = 'MSA_LABEL' if 'MSA_LABEL' in view.columns else ('MSA_NUM' if 'MSA_NUM' in view.columns else None)
    else:
        loc_col = 'CNTY_LABEL' if 'CNTY_LABEL' in view.columns else ('CNTY' if 'CNTY' in view.columns else None)       

    view_path = os.path.join(args.outdir, f'FILTERED_{args.group.upper()}_{args.focus_sex}_pct{args.threshold:.2f}.csv')
    view.to_csv(view_path, index=False)
    
    # optional: codebook for WEAPON_CODE -> WEAPON_LABEL
    codebook = (df[['WEAPON_CODE','WEAPON_LABEL']]
                .drop_duplicates()
                .sort_values('WEAPON_CODE'))
    codebook.to_csv(os.path.join(args.outdir, 'WEAPON_CODEBOOK.csv'), index=False)
    
    loc_col = 'MSA_LABEL' if args.group == 'msa' else 'CNTY_LABEL'
    wtop = (view.sort_values(['WEAPON_LABEL','UNSOLVED'], ascending=[True, False])
                .groupby('WEAPON_LABEL', group_keys=False)
                .head(min(args.top, 3)))

    print("\n[Per-weapon top (≤3 each)]")
    cols_to_show = ['WEAPON_LABEL', 'UNSOLVED', 'TOTAL', 'PERCENT']
    if loc_col:
        cols_to_show.insert(1, loc_col)  # show location if we have one
    print(wtop[ [c for c in cols_to_show if c in wtop.columns] ].to_string(index=False))
        
    
    
    # Top 20 preview
    print(f"[OK] Aggregates: {agg_path}")
    print(f"[OK] Filtered view: {view_path}")
    print(view.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
