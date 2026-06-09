#!/usr/bin/env python3
"""
Exportuje celou tabulku z PostgreSQL do air-reservations.csv
a pushne změnu na GitHub, aby byla data aktuální na GitHub Pages.
"""
import os, sys, csv, subprocess
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
        return False

    cols = list(rows[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in rows:
            w.writerow({k: ("" if v is None else str(v)) for k, v in row.items()})

    cur.close(); conn.close()
    print(f"[export] Uloženo do {OUT}")
    return True

def git_push():
    base = os.path.dirname(os.path.abspath(__file__))
    def run(cmd):
        r = subprocess.run(cmd, cwd=base, capture_output=True, text=True)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()

    ok, out, err = run(["git", "diff", "--quiet", "air-reservations.csv"])
    if ok:
        print("[git] CSV se nezměnilo, push přeskočen.")
        return

    print("[git] Commituju a pushuji aktualizaci CSV…")
    run(["git", "add", "air-reservations.csv"])
    run(["git", "commit", "-m", "Auto-update air-reservations.csv from PostgreSQL"])
    ok, out, err = run(["git", "push"])
    if ok:
        print("[git] Hotovo — GitHub Pages bude aktuální za ~1 minutu.")
    else:
        print(f"[git] Push selhal: {err}")
        print("[git] Tip: zkontroluj 'git remote -v' a přihlašovací údaje.")

if __name__ == "__main__":
    try:
        changed = export()
        if changed:
            git_push()
    except Exception as e:
        print(f"[export] Chyba: {e}", file=sys.stderr)
        sys.exit(1)
