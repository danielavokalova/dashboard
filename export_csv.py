#!/usr/bin/env python3
"""Exportuje celou tabulku z PostgreSQL do air-reservations.csv (pouze lokálně)."""
import os, sys, csv
import psycopg2, psycopg2.extras
from dotenv import load_dotenv

load_dotenv(override=True)

TABLE = os.getenv("TABLE_NAME", "gol_reservations_sourcedata_3_20260311130217")
OUT   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "air-reservations.csv")

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )

def export():
    print("[export] Připojuji se k databázi…")
    conn = get_db()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f'SELECT COUNT(*) FROM "{TABLE}"')
    total = cur.fetchone()["count"]
    print(f"[export] Exportuji {total:,} záznamů…")

    cur.execute(f'SELECT * FROM "{TABLE}" ORDER BY ctid')
    rows = cur.fetchall()
    if not rows:
        print("[export] Tabulka je prázdná, přeskakuji.")
        cur.close(); conn.close()
        return

    cols = list(rows[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow({k: ("" if v is None else str(v)) for k, v in row.items()})

    cur.close(); conn.close()
    print(f"[export] Hotovo — uloženo do {OUT}")

if __name__ == "__main__":
    try:
        export()
    except Exception as e:
        print(f"[export] Chyba: {e}", file=sys.stderr)
        sys.exit(1)
