#!/usr/bin/env python3
"""Air Reservations – lokální dashboard server"""
import os, json, datetime, subprocess, time
from decimal import Decimal
from flask import Flask, Response, send_from_directory, request
from flask_cors import CORS
import psycopg2, psycopg2.extras
from dotenv import load_dotenv

# Prefer values from local .env over inherited shell variables.
load_dotenv(override=True)

PORT  = int(os.getenv("PORT", 8080))
BASE  = os.path.dirname(os.path.abspath(__file__))
SYNC_WAIT_SECONDS = int(os.getenv("SYNC_WAIT_SECONDS", "12"))

def _find_latest_table():
    """Vrátí TABLE_NAME z .env, nebo najde tabulku s nejnovějšími daty (max datum) mezi gol_reservations_*."""
    explicit = os.getenv("TABLE_NAME", "").strip()
    if explicit:
        return explicit
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST","localhost"), port=int(os.getenv("DB_PORT","5432")),
            dbname=os.getenv("DB_NAME","postgres"), user=os.getenv("DB_USER","postgres"),
            password=os.getenv("DB_PASSWORD",""),
        )
        cur = conn.cursor()
        # Najdi všechny kandidátní tabulky
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name LIKE 'gol_reservations%'
            ORDER BY table_name DESC
            LIMIT 10
        """)
        candidates = [r[0] for r in cur.fetchall()]

        best_table, best_date = None, None
        date_expr = """CASE
            WHEN reservation_date ~ '^\\d{2}\\.\\d{2}\\.\\d{4}$' THEN to_date(reservation_date,'DD.MM.YYYY')
            WHEN reservation_date ~ '^\\d{4}-\\d{2}-\\d{2}' THEN reservation_date::date
            ELSE NULL END"""
        for t in candidates:
            try:
                cur.execute(f'SELECT MAX({date_expr}) FROM "{t}"')
                row = cur.fetchone()
                d = row[0] if row else None
                if d and (best_date is None or d > best_date):
                    best_date, best_table = d, t
            except Exception:
                pass

        cur.close(); conn.close()
        if best_table:
            print(f"[server] Vybrána tabulka s nejnovějšími daty: {best_table} (max datum: {best_date})")
            return best_table
    except Exception as e:
        print(f"[server] Nelze detekovat tabulku: {e}")
    return "gol_reservations_sourcedata_3_20260311130217"

TABLE = _find_latest_table()

app = Flask(__name__, static_folder=BASE)
CORS(app)

# ── SQL výrazy ─────────────────────────────────────────────────────────────────

_DATE = r"""CASE
    WHEN reservation_date ~ '^\d{2}\.\d{2}\.\d{4}$' THEN to_date(reservation_date,'DD.MM.YYYY')
    WHEN reservation_date ~ '^\d{4}-\d{2}-\d{2}' THEN reservation_date::date
    ELSE NULL END"""

_ISSUED = """CASE
    WHEN UPPER(COALESCE(status::text,'')) LIKE '%%ISSUE%%' THEN 1
    WHEN issuance_date IS NOT NULL AND issuance_date::text NOT IN ('','null','None') THEN 1
    ELSE 0 END"""

# ── DB ─────────────────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST","localhost"), port=int(os.getenv("DB_PORT","5432")),
        dbname=os.getenv("DB_NAME","postgres"), user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD",""),
    )

# ── JSON encoder ───────────────────────────────────────────────────────────────

class Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal): return float(o)
        if isinstance(o, (datetime.datetime, datetime.date)): return o.isoformat()
        return super().default(o)

def jresp(data, s=200):
    return Response(json.dumps(data, cls=Enc, ensure_ascii=False),
                    status=s, mimetype="application/json")

# ── Filtry ─────────────────────────────────────────────────────────────────────

def build_filter(args):
    """Sestaví WHERE klauzuli z parametrů requestu."""
    conds, params = [], []
    if args.get('date_from'):
        conds.append(f"({_DATE}) >= %s::date"); params.append(args['date_from'])
    if args.get('date_to'):
        conds.append(f"({_DATE}) <= %s::date"); params.append(args['date_to'])
    for col in ('agency','dealer','agency_country','currency','connector','status','type'):
        if args.get(col):
            conds.append(f'"{col}" = %s'); params.append(args[col])
    if args.get('search'):
        conds.append(f"row_to_json(\"{TABLE}\")::text ILIKE %s")
        params.append(f"%{args['search']}%")
    return ("WHERE " + " AND ".join(conds)) if conds else "", params

def wand(where, extra):
    """Přidá podmínku k WHERE klauzuli."""
    return f"{where} AND ({extra})" if where else f"WHERE ({extra})"

# ── /api/reservations ──────────────────────────────────────────────────────────

@app.route("/api/reservations")
def reservations():
    try:
        limit = int(request.args.get("limit", 500))
        where, params = build_filter(request.args)
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f'SELECT COUNT(*) FROM "{TABLE}" {where}', params)
        total = cur.fetchone()["count"]
        lim   = f"LIMIT {limit}" if limit > 0 else ""
        cur.execute(f'SELECT * FROM "{TABLE}" {where} ORDER BY ({_DATE}) DESC NULLS LAST {lim}', params)
        rows = [dict(r) for r in cur.fetchall()]
        cols = list(rows[0].keys()) if rows else []
        cur.close(); conn.close()
        return jresp({"ok":True,"columns":cols,"rows":rows,"count":len(rows),
                      "total":total,"limited":limit>0 and len(rows)<total})
    except Exception as e:
        return jresp({"ok":False,"error":str(e),"columns":[],"rows":[],"count":0,"total":0,"limited":False}, 500)

# ── /api/stats ─────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def stats():
    try:
        where, params = build_filter(request.args)
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        T = f'"{TABLE}"'

        def q(sql):
            cur.execute(sql, params); return [dict(r) for r in cur.fetchall()]
        def q1(sql):
            cur.execute(sql, params); r = cur.fetchone(); return dict(r) if r else {}

        # Celkové součty
        totals = q1(f"""SELECT COUNT(*) as total, SUM({_ISSUED}) as issued,
                        COUNT(DISTINCT agency) as agencies,
                        COUNT(DISTINCT agency_country) as countries
                        FROM {T} {where}""")

        # Měsíční trend
        w_d = wand(where, f"({_DATE}) IS NOT NULL")
        monthly = q(f"""SELECT TO_CHAR(({_DATE}),'YYYY-MM') as month,
                        COUNT(*) as total, SUM({_ISSUED}) as issued
                        FROM {T} {w_d} GROUP BY month ORDER BY month""")

        # Status
        by_status = q(f"""SELECT COALESCE(status::text,'(prázdné)') as label,
                          COUNT(*) as cnt FROM {T} {where}
                          GROUP BY label ORDER BY cnt DESC""")

        # Last status
        by_last_status = q(f"""SELECT COALESCE(last_status::text,'(prázdné)') as label,
                               COUNT(*) as cnt FROM {T} {where}
                               GROUP BY label ORDER BY cnt DESC LIMIT 10""")

        # Agentury top 15
        w_ag = wand(where, "agency IS NOT NULL AND agency::text != ''")
        by_agency = q(f"""SELECT agency as label, COUNT(*) as cnt, SUM({_ISSUED}) as issued
                          FROM {T} {w_ag} GROUP BY agency ORDER BY cnt DESC LIMIT 15""")

        # Země top 15
        w_co = wand(where, "agency_country IS NOT NULL AND agency_country::text != ''")
        by_country = q(f"""SELECT agency_country as label, COUNT(*) as cnt
                           FROM {T} {w_co} GROUP BY agency_country ORDER BY cnt DESC LIMIT 15""")

        # Měna + revenue
        w_cu = wand(where, "currency IS NOT NULL AND currency::text != ''")
        by_currency = q(f"""SELECT currency as label, COUNT(*) as cnt,
                            ROUND(SUM(CASE WHEN total_price IS NOT NULL AND total_price::text NOT IN ('','null')
                                     THEN total_price::numeric ELSE 0 END), 0) as revenue
                            FROM {T} {w_cu} GROUP BY currency ORDER BY cnt DESC""")

        # Connector
        by_connector = q(f"""SELECT COALESCE(connector::text,'(prázdné)') as label,
                             COUNT(*) as cnt FROM {T} {where}
                             GROUP BY label ORDER BY cnt DESC""")

        # Typ letu
        by_type = q(f"""SELECT COALESCE(type::text,'(prázdné)') as label,
                        COUNT(*) as cnt FROM {T} {where}
                        GROUP BY label ORDER BY cnt DESC""")

        cur.close(); conn.close()
        return jresp({"ok":True,"totals":totals,"monthly":monthly,
                      "by_status":by_status,"by_last_status":by_last_status,
                      "by_agency":by_agency,"by_country":by_country,
                      "by_currency":by_currency,"by_connector":by_connector,
                      "by_type":by_type})
    except Exception as e:
        return jresp({"ok":False,"error":str(e)}, 500)

# ── /api/health + refresh ──────────────────────────────────────────────────────

def db_total():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f'SELECT COUNT(*) FROM "{TABLE}"')
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return total

@app.route("/api/health")
def health():
    try:
        total = db_total()
        return jresp({"ok": True, "db": True, "total": total, "table": TABLE})
    except Exception as exc:
        return jresp({"ok": False, "db": False, "error": str(exc)}, 503)

@app.route("/api/refresh-data", methods=["POST"])
def refresh_data():
    """Spustí sync do Postgres a počká na doplnění dat."""
    notes = []
    try:
        before = db_total()
    except Exception as exc:
        return jresp({"ok": False, "error": f"PostgreSQL: {exc}", "notes": notes}, 500)

    try:
        proc = subprocess.run(
            ["docker", "start", "google-sync"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if proc.returncode == 0:
            notes.append("google-sync spuštěn")
        else:
            notes.append("google-sync není dostupný (pokračuji z Postgres)")
    except Exception as exc:
        notes.append(f"docker sync: {exc}")

    after = before
    for second in range(max(SYNC_WAIT_SECONDS, 1)):
        time.sleep(1)
        try:
            after = db_total()
            if after != before:
                notes.append(f"postgres aktualizován ({before} → {after})")
                break
        except Exception as exc:
            return jresp({"ok": False, "error": f"PostgreSQL: {exc}", "notes": notes}, 500)
    else:
        notes.append(f"postgres načten ({after} záznamů)")

    return jresp({"ok": True, "total": after, "before": before, "notes": notes})

# ── /api/filter-options ────────────────────────────────────────────────────────

@app.route("/api/filter-options")
def filter_options():
    try:
        conn = get_db(); cur = conn.cursor()
        opts = {}
        for col in ('status','agency','dealer','agency_country','currency','connector','type'):
            cur.execute(f"""SELECT DISTINCT "{col}"::text FROM "{TABLE}"
                           WHERE "{col}" IS NOT NULL AND "{col}"::text != '' ORDER BY 1""")
            opts[col] = [r[0] for r in cur.fetchall()]
        cur.close(); conn.close()
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
