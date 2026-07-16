#!/usr/bin/env python3
"""
Import GOL Reservations CSV do PostgreSQL.
Použití: python import_csv.py cesta_k_souboru.csv
"""
import sys, os, csv, re, datetime
import psycopg2, psycopg2.extras
from dotenv import load_dotenv

load_dotenv(override=True)

CSV_FILE = sys.argv[1] if len(sys.argv) > 1 else "GOL_Reservations__SourceData_1.csv"

def slugify(name):
    """Převede název sloupce na bezpečný identifikátor PostgreSQL."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")

def detect_type(values):
    """Heuristika pro datový typ sloupce."""
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return "TEXT"
    # integer?
    if all(re.match(r"^-?\d+$", v) for v in non_empty[:50]):
        return "BIGINT"
    # decimal?
    if all(re.match(r"^-?\d+[\.,]\d+$", v) for v in non_empty[:50]):
        return "NUMERIC"
    return "TEXT"

def make_table_name():
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"gol_reservations_sourcedata_1_{ts}"

def main():
    if not os.path.exists(CSV_FILE):
        print(f"[CHYBA] Soubor nenalezen: {CSV_FILE}")
        sys.exit(1)

    print(f"Načítám: {CSV_FILE}")
    with open(CSV_FILE, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        orig_cols = reader.fieldnames

    print(f"  Načteno {len(rows):,} řádků, {len(orig_cols)} sloupců")

    # Mapování původní název → slug pro DB
    col_map = {}
    for c in orig_cols:
        slug = slugify(c)
        # zajisti unikátnost
        base, n = slug, 1
        while slug in col_map.values():
            slug = f"{base}_{n}"; n += 1
        col_map[c] = slug

    # Detekuj typy z prvních 200 řádků
    sample = rows[:200]
    col_types = {}
    for orig, slug in col_map.items():
        vals = [r.get(orig, "") for r in sample]
        col_types[slug] = detect_type(vals)

    # Připoj se k PostgreSQL
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    cur = conn.cursor()

    table = make_table_name()
    print(f"  Vytvářím tabulku: {table}")

    col_defs = ", ".join(f'"{slug}" {col_types[slug]}' for slug in col_map.values())
    cur.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')

    # Hromadný import
    slugs = list(col_map.values())
    cols_sql = ", ".join(f'"{s}"' for s in slugs)
    placeholders = ", ".join(["%s"] * len(slugs))
    insert_sql = f'INSERT INTO "{table}" ({cols_sql}) VALUES ({placeholders})'

    batch = []
    for r in rows:
        vals = []
        for orig, slug in col_map.items():
            v = r.get(orig, "").strip()
            vals.append(v if v else None)
        batch.append(vals)
        if len(batch) >= 1000:
            psycopg2.extras.execute_batch(cur, insert_sql, batch)
            batch = []
    if batch:
        psycopg2.extras.execute_batch(cur, insert_sql, batch)

    conn.commit()
    cur.close()
    conn.close()
    print(f"  Hotovo! Tabulka '{table}' obsahuje {len(rows):,} záznamů.")
    print(f"  Server ji detekuje automaticky při příštím spuštění.")

if __name__ == "__main__":
    main()
