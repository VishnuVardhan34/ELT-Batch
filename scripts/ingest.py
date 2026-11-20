import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import duckdb


def parse_date(value: str):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"unsupported date format: {value}")


def normalize_row(row: dict, ingested_at: datetime, batch_id: str) -> tuple:
    order_id = (row.get("order_id") or "").strip()
    if not order_id:
        raise ValueError("order_id is required")

    customer_id = (row.get("customer_id") or "").strip()
    product_id = (row.get("product_id") or "").strip()
    status = (row.get("status") or "").strip().lower() or "unknown"

    if not customer_id:
        customer_id = f"C-{int(order_id):03d}" if order_id.isdigit() else f"C-{order_id}"
    if not product_id:
        product_id = f"P-{int(order_id):03d}" if order_id.isdigit() else f"P-{order_id}"

    quantity = int(row["quantity"])
    unit_price = float(row["unit_price"])
    if quantity < 0:
        raise ValueError(f"quantity cannot be negative for order {order_id}")
    if unit_price < 0:
        raise ValueError(f"unit_price cannot be negative for order {order_id}")

    order_date = parse_date(row["order_date"])
    updated_at = parse_date(row["updated_at"])
    return (order_id, customer_id, product_id, order_date, updated_at,
            quantity, unit_price, status, ingested_at, batch_id)


def ingest(input_path: str, database: str, chunk_size: int = 500) -> int:
    if chunk_size < 1:
        raise ValueError("chunk_size must be greater than zero")

    batch_id = hashlib.sha256(
        f"{input_path}:{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:16]
    ingested_at = datetime.now(timezone.utc)
    con = duckdb.connect(database)
    con.execute("""create table if not exists raw_orders (
        order_id varchar, customer_id varchar, product_id varchar,
        order_date date, updated_at timestamptz, quantity integer,
        unit_price decimal(12,2), status varchar, ingested_at timestamptz,
        batch_id varchar)""")

    insert_sql = "insert into raw_orders values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    total = 0
    try:
        with Path(input_path).open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required = {"order_id", "customer_id", "product_id", "order_date",
                        "updated_at", "quantity", "unit_price", "status"}
            missing = required - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"missing required CSV columns: {sorted(missing)}")

            chunk = []
            for line_number, row in enumerate(reader, start=2):
                try:
                    chunk.append(normalize_row(row, ingested_at, batch_id))
                except (ValueError, KeyError) as error:
                    raise ValueError(f"invalid row at line {line_number}: {error}") from error

                if len(chunk) == chunk_size:
                    con.executemany(insert_sql, chunk)
                    con.commit()
                    total += len(chunk)
                    chunk.clear()

            if chunk:
                con.executemany(insert_sql, chunk)
                con.commit()
                total += len(chunk)
    finally:
        con.close()
    return total


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/orders.csv")
    p.add_argument("--database", default="warehouse/warehouse.duckdb")
    p.add_argument("--chunk-size", type=int, default=500)
    args = p.parse_args()
    print(f"ingested {ingest(args.input, args.database, args.chunk_size)} rows")
