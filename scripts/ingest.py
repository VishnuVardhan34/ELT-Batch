import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import duckdb


def ingest(input_path: str, database: str) -> int:
    batch_id = hashlib.sha256(
        f"{input_path}:{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:16]
    con = duckdb.connect(database)
    con.execute("""create table if not exists raw_orders (
        order_id varchar, customer_id varchar, product_id varchar,
        order_date date, updated_at timestamptz, quantity integer,
        unit_price decimal(12,2), status varchar, ingested_at timestamptz,
        batch_id varchar)""")
    with Path(input_path).open(newline="", encoding="utf-8") as file:
        rows = [
            (r["order_id"], r["customer_id"], r["product_id"], r["order_date"],
             r["updated_at"], int(r["quantity"]), float(r["unit_price"]),
             r["status"], datetime.now(timezone.utc), batch_id)
            for r in csv.DictReader(file)
        ]
    con.executemany("insert into raw_orders values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    con.close()
    return len(rows)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/orders.csv")
    p.add_argument("--database", default="warehouse/warehouse.duckdb")
    args = p.parse_args()
    print(f"ingested {ingest(args.input, args.database)} rows")
