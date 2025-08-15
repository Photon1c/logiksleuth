from copy import deepcopy

def drop_fields(rec, fields):
    r = deepcopy(rec)
    for f in fields:
        r.pop(f, None)
    return r

def dob_to_year(rec):
    r = deepcopy(rec)
    dob = r.pop("exact_dob", None)
    if dob and len(dob) >= 4:
        r["birth_year"] = dob[:4]
    return r

def address_to_city(rec):
    r = deepcopy(rec)
    if "address" in r:
        r.pop("address", None)
    # assume city/county already present; keep centroid external
    return r

def gps_to_hex(rec, precision="hex7"):
    r = deepcopy(rec)
    if "gps_exact" in r:
        r.pop("gps_exact", None)
    r["geo_precision"] = precision
    return r

def date_to_band(rec, band="week_band"):
    r = deepcopy(rec)
    date = r.get("date")
    if date and len(date) >= 10:
        # simple “YYYY-WW” band stub
        import datetime as dt
        y, m, d = map(int, date.split("-"))
        ww = dt.date(y, m, d).isocalendar().week
        r[band] = f"{y}-W{ww:02d}"
    return r

def minimal_active(rec):
    # compose minimal pipeline for active cases
    r = rec
    r = dob_to_year(r)
    r = address_to_city(r)
    r = gps_to_hex(r, "hex7")
    r = date_to_band(r, "week_band")
    # final hard drop of sensitive fields if still present
    return drop_fields(r, ["name", "exact_dob", "address", "gps_exact", "phone", "email", "handles", "plate"])
