# 📊 Sales Trend Analysis

Analisis tren penjualan ritel (gaya *Superstore*) secara **end-to-end** —
dari data mentah, diolah dengan **SQL (MySQL 8)**, dianalisis dengan **Python**,
dan divisualisasikan dengan **Tableau**.

> **Project portofolio Data Analyst.**
> Fokus utama: *produk & kategori apa yang menunjukkan tren pertumbuhan paling
> kuat dari tahun ke tahun, dan bagaimana pola musimannya?*

---

## ❓ Pertanyaan Bisnis

1. 📈 Kategori / sub-kategori mana yang tumbuh paling cepat tiap tahun? (growth rate)
2. 📅 Apakah ada pola musiman? (bulan apa paling ramai)
3. 🏆 Produk apa yang konsisten naik vs mulai ditinggalkan?
4. 🛒 *(bonus)* Produk apa yang sering dibeli bersamaan?

---

## 🗂️ Struktur Project

```
sales-trend-analysis/
├── data/
│   └── raw/
│       └── superstore_orders.csv   # dataset mentah (hasil generate)
├── scripts/
│   └── generate_dataset.py         # generator dataset (Python std lib)
├── sql/                            # schema + query analisis (MySQL 8)
├── notebooks/                      # analisis & visualisasi (Python)
├── tableau/                        # panduan + data untuk dashboard
├── reports/                        # insight & kesimpulan
└── README.md
```

---

## 🚀 Cara Memulai

### 1. Siapkan dataset
Dataset bisa dibuat ulang kapan saja (tidak perlu internet, hanya Python 3):

```bash
python scripts/generate_dataset.py
# -> menghasilkan data/raw/superstore_orders.csv
```

### 2. Import ke MySQL
Buka **DBeaver** (terhubung ke **MySQL 8**), lalu jalankan script di folder `sql/`
sesuai urutan (schema → load data → analisis). *(menyusul di tahap berikutnya)*

### 3. Analisis & Visualisasi
- Query analisis tren ada di `sql/`.
- Notebook Python untuk eksplorasi & grafik ada di `notebooks/`.
- Dashboard Tableau & panduannya ada di `tableau/`.

---

## 🧱 Desain Database

Dataset mentah (1 baris = 1 item order) dinormalisasi menjadi **4 tabel**:

```
customers ──┐
            ├──→ orders ──→ order_items ←── products
            │  (header)     (detail/item)
```

| Tabel         | Isi                                                        | 1 baris = |
|---------------|------------------------------------------------------------|-----------|
| `customers`   | customer_id, name, segment, region, state, city            | 1 pelanggan |
| `products`    | product_id, name, category, sub_category                   | 1 produk |
| `orders`      | order_id, order_date, ship_mode, customer_id (FK)          | 1 order |
| `order_items` | item_id, order_id (FK), product_id (FK), quantity, discount, sales, profit | 1 item dalam order |

> **Kenapa `sales`/`profit`/`quantity` ada di `order_items`, bukan `orders`?**
> Karena satu order bisa berisi **banyak item** (relasi *one-to-many*), jadi tiap
> item punya quantity/sales/profit sendiri.

---

## 🛠️ Tools

![SQL](https://img.shields.io/badge/MySQL_8-SQL-blue)
![Python](https://img.shields.io/badge/Python-pandas-green)
![Tableau](https://img.shields.io/badge/Tableau-dashboard-orange)

- **MySQL 8** (dikerjakan via DBeaver) — penyimpanan & query analisis
- **Python** (pandas, matplotlib) — eksplorasi & visualisasi
- **Tableau** — dashboard interaktif

---

## 📌 Catatan tentang Dataset

Dataset ini **di-generate secara sintetis** menyerupai *Superstore* (2014–2017),
dengan **tren pertumbuhan tahunan** dan **pola musiman** yang sengaja dirancang
agar cocok untuk latihan analisis tren. Lihat `scripts/generate_dataset.py`.

---

*Dibuat sebagai bagian dari pembelajaran menjadi Data Analyst.* 🎓
