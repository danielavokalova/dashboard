#!/usr/bin/env python3
"""Air Reservations – lokální dashboard server"""
import os, json, datetime, subprocess, time, csv, glob, re
from decimal import Decimal
from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(override=True)

PORT = int(os.getenv("PORT", 8080))
BASE = os.path.dirname(os.path.abspath(__file__))
SYNC_WAIT_SECONDS = int(os.getenv("SYNC_WAIT_SECONDS", "12"))

# ── CSV data source ────────────────────────────────────────────────────────────

def _find_csv():
    """Najde nejnovější GOL CSV soubor ve složce dashboardu."""
    explicit = os.getenv("DATA_CSV", "").strip()
    if explicit and os.path.exists(explicit):
        return explicit
    patterns = ["GOL_Reservations*.csv", "gol_reservations*.csv", "air-reservations-data.csv"]
    for pat in patterns:
        files = sorted(glob.glob(os.path.join(BASE, pat)), key=os.path.getmtime, reverse=True)
        if files:
            return files[0]
    return None

CSV_FILE = _find_csv()

_csv_cache = None  # (columns, rows)

def load_csv_data():
    global _csv_cache
    if _csv_cache is not None:
        return _csv_cache
    if not CSV_FILE:
        return None, None
    print(f"[server] Načítám CSV: {CSV_FILE}")
    with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    columns = list(rows[0].keys()) if rows else []
    # normalize column names to lowercase with underscores (matches dashboard expectations)
    def slug(s): return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")
    col_map = {c: slug(c) for c in columns}
    norm_rows = [{col_map[k]: v for k, v in r.items()} for r in rows]
    norm_cols = list(col_map.values())
    _csv_cache = (norm_cols, norm_rows)
    print(f"[server] CSV načteno: {len(norm_rows):,} záznamů")
    return _csv_cache

if CSV_FILE:
    print(f"[server] Datový zdroj: CSV → {CSV_FILE}")
    load_csv_data()
else:
    print(f"[server] CSV nenalezeno, zkouším PostgreSQL")



# ── JSON encoder ───────────────────────────────────────────────────────────────

class Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal): return float(o)
        if isinstance(o, (datetime.datetime, datetime.date)): return o.isoformat()
        return super().default(o)

def jresp(data, s=200):
    return Response(json.dumps(data, cls=Enc, ensure_ascii=False),
                    status=s, mimetype="application/json")

# ── CSV helpers ────────────────────────────────────────────────────────────────

def _parse_date(v):
    if not v: return None
    s = str(v).strip()
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', s):
        d,m,y = s.split('.'); return f"{y}-{m.zfill(2)}-{d.zfill(2)}"
    if re.match(r'^\d{4}-\d{2}-\d{2}', s):
        return s[:10]
    return None

def _is_issued(row):
    status = str(row.get('status','')).upper()
    if 'ISSUE' in status: return True
    idate = str(row.get('issuance_date','')).strip()
    return idate not in ('','null','None','')

def _filter_csv(rows, args):
    date_from = args.get('date_from','')
    date_to   = args.get('date_to','')
    search    = args.get('search','').lower()
    exact_cols = ('agency','dealer','agency_country','currency','connector','status','type')
    result = []
    for r in rows:
        d = _parse_date(r.get('reservation_date',''))
        if date_from and (not d or d < date_from): continue
        if date_to   and (not d or d > date_to):   continue
        skip = False
        for col in exact_cols:
            val = args.get(col,'')
            if val and r.get(col,'') != val: skip = True; break
        if skip: continue
        if search and search not in ' '.join(r.values()).lower(): continue
        result.append(r)
    return result

# ── /api/reservations ──────────────────────────────────────────────────────────

@app.route("/api/reservations")
def reservations():
    try:
        columns, all_rows = load_csv_data()
        if all_rows is None:
            raise RuntimeError("CSV soubor nenalezen. Umístěte GOL_Reservations*.csv do složky dashboardu.")
        limit = int(request.args.get("limit", 500))
        rows = _filter_csv(all_rows, request.args)
        rows.sort(key=lambda r: _parse_date(r.get('reservation_date','')) or '', reverse=True)
        total = len(rows)
        if limit > 0:
            rows = rows[:limit]
        return jresp({"ok":True,"columns":columns,"rows":rows,"count":len(rows),
                      "total":total,"limited":limit>0 and len(rows)<total})
    except Exception as e:
        return jresp({"ok":False,"error":str(e),"columns":[],"rows":[],"count":0,"total":0,"limited":False}, 500)

# ── /api/stats ─────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def stats():
    try:
        from collections import defaultdict
        columns, all_rows = load_csv_data()
        if all_rows is None:
            raise RuntimeError("CSV soubor nenalezen.")
        rows = _filter_csv(all_rows, request.args)

        issued_count = sum(1 for r in rows if _is_issued(r))
        agencies  = len({r.get('agency','') for r in rows if r.get('agency','')})
        countries = len({r.get('agency_country','') for r in rows if r.get('agency_country','')})
        totals = {"total": len(rows), "issued": issued_count, "agencies": agencies, "countries": countries}

        # Měsíční trend
        mon = defaultdict(lambda: {"total":0,"issued":0})
        for r in rows:
            d = _parse_date(r.get('reservation_date',''))
            if d:
                m = d[:7]
                mon[m]["total"] += 1
                if _is_issued(r): mon[m]["issued"] += 1
        monthly = [{"month":k,"total":v["total"],"issued":v["issued"]} for k,v in sorted(mon.items())]

        def group_by(key, rows, limit=None):
            cnt = defaultdict(int)
            for r in rows: cnt[r.get(key,'') or '(prázdné)'] += 1
            result = sorted(cnt.items(), key=lambda x:-x[1])
            if limit: result = result[:limit]
            return [{"label":k,"cnt":v} for k,v in result]

        def group_agency(rows):
            cnt = defaultdict(lambda:{"cnt":0,"issued":0})
            for r in rows:
                a = r.get('agency','') or '(prázdné)'
                cnt[a]["cnt"] += 1
                if _is_issued(r): cnt[a]["issued"] += 1
            result = sorted(cnt.items(), key=lambda x:-x[1]["cnt"])[:15]
            return [{"label":k,"cnt":v["cnt"],"issued":v["issued"]} for k,v in result]

        def group_currency(rows):
            cnt = defaultdict(lambda:{"cnt":0,"revenue":0})
            for r in rows:
                c = r.get('currency','') or '(prázdné)'
                cnt[c]["cnt"] += 1
                try: cnt[c]["revenue"] += float(r.get('total_price','') or 0)
                except: pass
            return [{"label":k,"cnt":v["cnt"],"revenue":round(v["revenue"],0)} for k,v in sorted(cnt.items(),key=lambda x:-x[1]["cnt"])]

        return jresp({"ok":True,"totals":totals,"monthly":monthly,
                      "by_status":     group_by('status', rows),
                      "by_last_status":group_by('last_status', rows, 10),
                      "by_agency":     group_agency(rows),
                      "by_country":    group_by('agency_country', rows, 15),
                      "by_currency":   group_currency(rows),
                      "by_connector":  group_by('connector', rows),
                      "by_type":       group_by('type', rows)})
    except Exception as e:
        return jresp({"ok":False,"error":str(e)}, 500)

# ── /api/health ────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    try:
        columns, rows = load_csv_data()
        total = len(rows) if rows else 0
        return jresp({"ok": True, "db": True, "total": total, "table": CSV_FILE or "csv"})
    except Exception as exc:
        return jresp({"ok": False, "db": False, "error": str(exc)}, 503)

@app.route("/api/refresh-data", methods=["POST"])
def refresh_data():
    """Znovu načte CSV ze souboru."""
    global _csv_cache
    _csv_cache = None
    columns, rows = load_csv_data()
    total = len(rows) if rows else 0
    return jresp({"ok": True, "total": total, "before": total, "notes": [f"CSV znovu načteno ({total:,} záznamů)"]})

# ── /api/filter-options ────────────────────────────────────────────────────────

@app.route("/api/filter-options")
def filter_options():
    try:
        columns, rows = load_csv_data()
        if rows is None: raise RuntimeError("CSV nenalezeno")
        opts = {}
        for col in ('status','agency','dealer','agency_country','currency','connector','type'):
            vals = sorted({r.get(col,'') for r in rows if r.get(col,'')})
            opts[col] = vals
        return jresp({"ok":True, **opts})
    except Exception as e:
        return jresp({"ok":False,"error":str(e)}, 500)

# ── /api/gsheet-stream  ────────────────────────────────────────────────────────

GSHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1PnxOaenFjIPbmEnySChbE6h13HehIsFM9VNnwytsY4k"
    "/export?format=csv&gid=413463191"
)
DATE_FROM = "2026-01-01"

def _fetch_gsheet_rows():
    """Stáhne Google Sheets CSV a vrátí (columns, rows) jako list of dicts."""
    import urllib.request, csv, io
    req = urllib.request.urlopen(GSHEET_CSV, timeout=30)
    raw = req.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    rows = [dict(r) for r in reader]
    columns = list(rows[0].keys()) if rows else []
    return columns, rows

@app.route("/api/gsheet-reservations")
def gsheet_reservations():
    """Vrátí všechna data z Google Sheets ve stejném formátu jako /api/reservations."""
    try:
        columns, rows = _fetch_gsheet_rows()
        return jresp({"ok": True, "columns": columns, "rows": rows,
                      "count": len(rows), "total": len(rows), "limited": False})
    except Exception as e:
        return jresp({"ok": False, "error": str(e), "columns": [], "rows": [],
                      "count": 0, "total": 0, "limited": False}, 500)

@app.route("/api/gsheet-stream")
def gsheet_stream():
    """Streamuje záznamy z Google Sheets od DATE_FROM jako NDJSON s progress."""
    import urllib.request, csv, io

    def generate():
        try:
            req = urllib.request.urlopen(GSHEET_CSV, timeout=30)
            raw = req.read().decode("utf-8-sig")
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
            return

        reader = csv.DictReader(io.StringIO(raw))
        rows = list(reader)
        total = len(rows)
        sent = 0
        yield json.dumps({"total": total}) + "\n"

        for row in rows:
            date_val = (row.get("Reservation date") or row.get("reservation_date") or "").strip()
            # support DD.MM.YYYY and YYYY-MM-DD
            try:
                if "." in date_val:
                    parts = date_val.split(".")
                    date_iso = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
                else:
                    date_iso = date_val[:10]
            except Exception:
                date_iso = ""

            if date_iso >= DATE_FROM:
                yield json.dumps(row) + "\n"
            sent += 1
            if sent % 500 == 0:
                yield json.dumps({"progress": sent, "total": total}) + "\n"

        yield json.dumps({"done": True, "total": total}) + "\n"

    return Response(generate(), mimetype="application/x-ndjson",
                    headers={"Cache-Control": "no-store"})

# ── Static files ───────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/<path:path>")
def static_files(path="index.html"):
    try: return send_from_directory(BASE, path)
    except: return "404", 404

# ── Start ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f'\n  Air Reservations → http://localhost:{PORT}/air-reservations.html\n')
    app.run(host="127.0.0.1", port=PORT, debug=False)
