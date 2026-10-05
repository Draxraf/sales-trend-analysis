"""
export_for_tableau.py
---------------------
Membuat beberapa CSV hasil agregasi (sudah "matang") dari dataset mentah,
siap langsung dipakai di Tableau Public (yang hanya bisa baca file).

Isi query-nya SAMA dengan yang ada di sql/03_analysis.sql, tapi dihitung
dengan Python supaya menghasilkan file CSV. Jadi angka di Tableau akan
konsisten dengan hasil di MySQL/DBeaver.

Output (folder tableau/):
  - sales_per_year_category.csv  : tren sales + growth YoY per kategori
  - sales_per_month.csv          : pola musiman (per bulan, gabung semua tahun)
  - sales_per_month_year.csv     : sales per bulan per tahun (48 baris)
  - top_products.csv             : produk by unit terjual & revenue

Jalankan: python scripts/export_for_tableau.py
Hanya butuh Python standard library.
"""

import csv
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw", "superstore_orders.csv")
OUT_DIR = os.path.join(HERE, "..", "tableau")
os.makedirs(OUT_DIR, exist_ok=True)

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def load_rows():
    with open(RAW, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"OK -> {os.path.relpath(path)}  ({len(rows)} baris)")


def main():
    rows = load_rows()

    # ---- helper: ambil tahun & bulan dari order_date (YYYY-MM-DD) ----
    def year(r):
        return int(r["order_date"][:4])

    def month(r):
        return int(r["order_date"][5:7])

    # =================================================================
    # 1. sales_per_year_category.csv  (tren + growth YoY per kategori)
    # =================================================================
    agg = defaultdict(float)  # (category, year) -> sales
    for r in rows:
        agg[(r["category"], year(r))] += float(r["sales"])

    categories = sorted({c for (c, _) in agg})
    years = sorted({y for (_, y) in agg})

    out = []
    for cat in categories:
        prev = None
        for y in years:
            total = round(agg.get((cat, y), 0.0), 2)
            growth = ""
            if prev not in (None, 0):
                growth = round((total - prev) / prev * 100, 2)
            out.append({
                "category": cat,
                "year": y,
                "total_sales": total,
                "prev_year_sales": "" if prev is None else round(prev, 2),
                "growth_percent": growth,
            })
            prev = total
    write_csv(
        os.path.join(OUT_DIR, "sales_per_year_category.csv"),
        ["category", "year", "total_sales", "prev_year_sales", "growth_percent"],
        out,
    )

    # =================================================================
    # 2. sales_per_month.csv  (pola musiman, gabung semua tahun)
    # =================================================================
    by_month = defaultdict(float)
    for r in rows:
        by_month[month(r)] += float(r["sales"])
    out = [{
        "month_num": m,
        "month_name": MONTH_NAMES[m],
        "total_sales": round(by_month.get(m, 0.0), 2),
    } for m in range(1, 13)]
    write_csv(
        os.path.join(OUT_DIR, "sales_per_month.csv"),
        ["month_num", "month_name", "total_sales"],
        out,
    )

    # =================================================================
    # 3. sales_per_month_year.csv  (per bulan per tahun -> line chart)
    # =================================================================
    by_my = defaultdict(float)
    for r in rows:
        by_my[(year(r), month(r))] += float(r["sales"])
    out = []
    for y in years:
        for m in range(1, 13):
            out.append({
                "year": y,
                "month_num": m,
                "month_name": MONTH_NAMES[m],
                "total_sales": round(by_my.get((y, m), 0.0), 2),
            })
    write_csv(
        os.path.join(OUT_DIR, "sales_per_month_year.csv"),
        ["year", "month_num", "month_name", "total_sales"],
        out,
    )

    # =================================================================
    # 4. top_products.csv  (by unit & revenue)
    # =================================================================
    qty = defaultdict(float)
    sales = defaultdict(float)
    profit = defaultdict(float)
    meta = {}
    for r in rows:
        pid = r["product_id"]
        qty[pid] += float(r["quantity"])
        sales[pid] += float(r["sales"])
        profit[pid] += float(r["profit"])
        meta[pid] = (r["product_name"], r["category"])
    out = []
    for pid in meta:
        name, cat = meta[pid]
        out.append({
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "total_unit": int(qty[pid]),
            "total_sales": round(sales[pid], 2),
            "total_profit": round(profit[pid], 2),
        })
    out.sort(key=lambda x: x["total_sales"], reverse=True)
    write_csv(
        os.path.join(OUT_DIR, "top_products.csv"),
        ["product_id", "product_name", "category", "total_unit",
         "total_sales", "total_profit"],
        out,
    )

    print("\nSemua CSV untuk Tableau sudah dibuat di folder tableau/")


if __name__ == "__main__":
    main()
