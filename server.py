#!/usr/bin/env python3
"""
Air Reservations – lokální dashboard server
--------------------------------------------
1. Zkopíruj .env.example do .env a vyplň přihlašovací údaje k PostgreSQL
   (stejné jako používá Metabase)
2. pip install -r requirements.txt
3. python server.py
4. Otevři http://localhost:8080/air-reservations.html
"""
import os
import json
import datetime
from decimal import Decimal

from flask import Flask, Response, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

TABLE = os.getenv("TABLE_NAME", "gol_reservations_sourcedata_3_20260311130217")
PORT  = int(os.getenv("PORT", 8080))
BASE  = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE)
CORS(app)


# ── DB connection ──────────────────────────────────────────────────────────────

def get_db():
    return psycopg2.connect(
        host     = os.getenv("DB_HOST",     "localhost"),
        port     = int(os.getenv("DB_PORT", "5432")),
        dbname   = os.getenv("DB_NAME",     "postgres"),
        user     = os.getenv("DB_USER",     "postgres"),
        password = os.getenv("DB_PASSWORD", ""),
    )


# ── JSON serializer (handles date / Decimal) ───────────────────────────────────

class Enc(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):           return float(o)
        if isinstance(o, datetime.datetime): return o.isoformat()
        if isinstance(o, datetime.date):     return o.isoformat()
        return super().default(o)


def jresp(data, status=200):
    return Response(
        json.dumps(data, cls=Enc, ensure_ascii=False),
        status=status,
        mimetype="application/json",
    )


# ── API endpoints ──────────────────────────────────────────────────────────────

@app.route("/api/reservations")
def reservations():
    """Vrátí všechny řádky z tabulky rezervací jako JSON."""
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f'SELECT * FROM "{TABLE}"')
        rows = [dict(r) for r in cur.fetchall()]
        cols = list(rows[0].keys()) if rows else []
        cur.close()
        conn.close()
        return jresp({"ok": True, "columns": cols, "rows": rows, "count": len(rows)})
    except Exception as e:
        return jresp({"ok": False, "error": str(e), "columns": [], "rows": [], "count": 0}, 500)


@app.route("/api/status")
def status():
    """Health-check – ověří připojení k DB a vrátí počet řádků."""
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(f'SELECT COUNT(*) FROM "{TABLE}"')
        n = cur.fetchone()[0]
        cur.close()
        conn.close()
        return jresp({"ok": True, "table": TABLE, "count": n})
    except Exception as e:
        return jresp({"ok": False, "error": str(e)}, 500)


# ── Static file serving ────────────────────────────────────────────────────────

@app.route("/")
def root():
    return send_from_directory(BASE, "index.html")


@app.route("/<path:path>")
def static_files(path):
    try:
        return send_from_directory(BASE, path)
    except Exception:
        return "404 Not Found", 404


# ── Startup ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cfg = {
        "host":   os.getenv("DB_HOST",     "localhost"),
        "port":   os.getenv("DB_PORT",     "5432"),
        "dbname": os.getenv("DB_NAME",     "postgres"),
        "user":   os.getenv("DB_USER",     "postgres"),
    }
    print()
    print("  ╔══════════════════════════════════════════════════╗")
    print("  ║         Air Reservations – lokální server        ║")
    print("  ╠══════════════════════════════════════════════════╣")
    print(f"  ║  DB:      {cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}")
    print(f"  ║  Tabulka: {TABLE}")
    print(f"  ║  URL:     http://localhost:{PORT}/air-reservations.html")
    print("  ╚══════════════════════════════════════════════════╝")
    print()
    app.run(host="0.0.0.0", port=PORT, debug=False)
