"""
generate_dataset.py
-------------------
Membuat dataset penjualan ber-gaya "Superstore" yang realistis untuk
project portofolio Sales Trend Analysis.

Output: data/raw/superstore_orders.csv
  - 1 baris = 1 item dalam sebuah order (order line)
  - Rentang waktu: 2014-01-01 s/d 2017-12-31 (4 tahun) -> cocok untuk analisis tren
  - Ada tren pertumbuhan tahunan + pola musiman (akhir tahun lebih ramai)

Dijalankan dengan: python scripts/generate_dataset.py
Tidak butuh koneksi internet, hanya Python standard library.
"""

import csv
import os
import random
from datetime import date, timedelta

random.seed(42)  # supaya hasilnya selalu sama (reproducible)

# ---------------------------------------------------------------------------
# 1. Master data: produk, kategori, customer, geografi
#    Struktur ini meniru Superstore asli.
# ---------------------------------------------------------------------------

# category -> sub_category -> daftar nama produk
CATALOG = {
    "Furniture": {
        "Chairs": ["Office Chair Ergo", "Dining Chair Oak", "Folding Chair"],
        "Tables": ["Conference Table", "Study Desk", "Coffee Table"],
        "Bookcases": ["Wooden Bookcase", "Metal Shelf Unit"],
        "Furnishings": ["Desk Lamp", "Wall Clock", "Picture Frame"],
    },
    "Office Supplies": {
        "Paper": ["A4 Paper Ream", "Sticky Notes", "Notebook A5"],
        "Binders": ["Lever Arch Binder", "Ring Binder"],
        "Storage": ["Storage Box", "File Cabinet"],
        "Art": ["Marker Set", "Colored Pencils"],
        "Fasteners": ["Stapler", "Paper Clips Box"],
    },
    "Technology": {
        "Phones": ["Smartphone X", "Office Desk Phone", "Headset Pro"],
        "Computers": ["Laptop Pro 14", "Desktop Tower", "Mini PC"],
        "Accessories": ["Wireless Mouse", "Mechanical Keyboard", "USB-C Hub"],
        "Machines": ["Laser Printer", "Document Scanner"],
    },
}

# region -> daftar (state, city)
GEOGRAPHY = {
    "West": [("California", "Los Angeles"), ("California", "San Francisco"),
             ("Washington", "Seattle"), ("Oregon", "Portland")],
    "East": [("New York", "New York City"), ("Pennsylvania", "Philadelphia"),
             ("Massachusetts", "Boston"), ("Florida", "Miami")],
    "Central": [("Texas", "Houston"), ("Illinois", "Chicago"),
                ("Michigan", "Detroit"), ("Ohio", "Columbus")],
    "South": [("Georgia", "Atlanta"), ("Tennessee", "Nashville"),
              ("Louisiana", "New Orleans"), ("Virginia", "Richmond")],
}

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]

FIRST_NAMES = ["Andi", "Budi", "Citra", "Dewi", "Eka", "Fajar", "Gita",
               "Hadi", "Indah", "Joko", "Kiki", "Lina", "Maya", "Nanda",
               "Oka", "Putri", "Rama", "Sari", "Tono", "Uli"]
LAST_NAMES = ["Santoso", "Wijaya", "Pratama", "Lestari", "Kusuma",
              "Halim", "Saputra", "Permata", "Nugraha", "Anggraini"]

# ---------------------------------------------------------------------------
# 2. Bikin daftar customer tetap (supaya 1 customer bisa order berkali-kali)
# ---------------------------------------------------------------------------

def build_customers(n=120):
    customers = []
    for i in range(1, n + 1):
        region = random.choice(list(GEOGRAPHY.keys()))
        state, city = random.choice(GEOGRAPHY[region])
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        customers.append({
            "customer_id": f"CUST-{i:04d}",
            "customer_name": name,
            "segment": random.choice(SEGMENTS),
            "region": region,
            "state": state,
            "city": city,
        })
    return customers


# flatten katalog jadi list produk dengan harga dasar
def build_products():
    products = []
    pid = 1
    for category, subs in CATALOG.items():
        for sub_category, names in subs.items():
            for name in names:
                # harga dasar beda-beda per kategori (Technology paling mahal)
                base = {"Furniture": 150, "Office Supplies": 20,
                        "Technology": 400}[category]
                price = round(base * random.uniform(0.6, 1.8), 2)
                products.append({
                    "product_id": f"PROD-{pid:04d}",
                    "product_name": name,
                    "category": category,
                    "sub_category": sub_category,
                    "unit_price": price,
                })
                pid += 1
    return products


CUSTOMERS = build_customers()
PRODUCTS = build_products()

# ---------------------------------------------------------------------------
# 3. Model tren: tiap tahun jumlah order naik; akhir tahun (Q4) lebih ramai
# ---------------------------------------------------------------------------

# jumlah order per tahun -> tren naik (pertumbuhan ~25%/tahun)
ORDERS_PER_YEAR = {2014: 400, 2015: 520, 2016: 680, 2017: 880}

# bobot bulan (musiman): Nov & Des paling tinggi
MONTH_WEIGHT = [0.6, 0.6, 0.8, 0.9, 1.0, 1.0,
                1.0, 1.0, 1.1, 1.2, 1.6, 1.8]

# Technology makin lama makin populer (porsinya naik tiap tahun)
# -> ini "cerita" utama analisis tren kita
CATEGORY_WEIGHT_BY_YEAR = {
    2014: {"Furniture": 0.40, "Office Supplies": 0.40, "Technology": 0.20},
    2015: {"Furniture": 0.37, "Office Supplies": 0.38, "Technology": 0.25},
    2016: {"Furniture": 0.33, "Office Supplies": 0.35, "Technology": 0.32},
    2017: {"Furniture": 0.28, "Office Supplies": 0.32, "Technology": 0.40},
}


def pick_product(year):
    """Pilih produk dengan bias kategori sesuai tahun (biar ada tren)."""
    weights = CATEGORY_WEIGHT_BY_YEAR[year]
    category = random.choices(list(weights.keys()),
                              weights=list(weights.values()))[0]
    candidates = [p for p in PRODUCTS if p["category"] == category]
    return random.choice(candidates)


def random_date_in_month(year, month):
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    days = (nxt - date(year, month, 1)).days
    return date(year, month, 1) + timedelta(days=random.randint(0, days - 1))


# ---------------------------------------------------------------------------
# 4. Generate baris-baris order
# ---------------------------------------------------------------------------

def generate_rows():
    rows = []
    order_counter = 1
    for year, n_orders in ORDERS_PER_YEAR.items():
        for _ in range(n_orders):
            # tentukan bulan berdasarkan bobot musiman
            month = random.choices(range(1, 13), weights=MONTH_WEIGHT)[0]
            order_date = random_date_in_month(year, month)
            customer = random.choice(CUSTOMERS)
            ship_mode = random.choice(SHIP_MODES)
            order_id = f"ORD-{year}-{order_counter:05d}"
            order_counter += 1

            # tiap order punya 1-4 item (produk berbeda)
            n_items = random.randint(1, 4)
            chosen = random.sample(PRODUCTS, k=n_items) if False else None
            for item_no in range(n_items):
                product = pick_product(year)
                quantity = random.randint(1, 8)
                discount = random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.3])
                gross = product["unit_price"] * quantity
                sales = round(gross * (1 - discount), 2)
                # margin profit: Technology lebih tipis saat diskon besar
                margin = random.uniform(0.08, 0.28) - discount * 0.3
                profit = round(sales * margin, 2)
                rows.append({
                    "order_id": order_id,
                    "order_date": order_date.isoformat(),
                    "ship_mode": ship_mode,
                    "customer_id": customer["customer_id"],
                    "customer_name": customer["customer_name"],
                    "segment": customer["segment"],
                    "region": customer["region"],
                    "state": customer["state"],
                    "city": customer["city"],
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": product["category"],
                    "sub_category": product["sub_category"],
                    "quantity": quantity,
                    "discount": discount,
                    "sales": sales,
                    "profit": profit,
                })
    return rows


def main():
    rows = generate_rows()
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "superstore_orders.csv")

    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"OK -> {out_path}")
    print(f"Total baris (order lines): {len(rows)}")
    uniq_orders = len({r['order_id'] for r in rows})
    print(f"Total order unik          : {uniq_orders}")
    print(f"Total customer            : {len(CUSTOMERS)}")
    print(f"Total produk              : {len(PRODUCTS)}")


if __name__ == "__main__":
    main()
