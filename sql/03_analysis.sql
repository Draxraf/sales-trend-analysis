-- =====================================================================
-- 03_analysis.sql
-- Query analisis untuk project Sales Trend Analysis (MySQL 8 / DBeaver).
--
-- Berisi:
--   A. Eksplorasi (EDA) dasar
--   B. Produk paling laku (by unit vs by revenue)
--   C. Tren penjualan per tahun + growth YoY (CTE + window function LAG)
--   D. Tren per kategori + growth YoY (PARTITION BY)
--
-- Pertanyaan utama project:
--   "Kategori/produk apa yang menunjukkan tren pertumbuhan paling kuat
--    dari tahun ke tahun (era e-commerce)?"
-- =====================================================================

USE superstore;

-- =====================================================================
-- A. EKSPLORASI (EDA) DASAR
-- =====================================================================

-- A1. Rentang tanggal data
SELECT MIN(order_date) AS tanggal_awal,
       MAX(order_date) AS tanggal_akhir
FROM orders;

-- A2. Total sales & profit keseluruhan
SELECT SUM(sales)  AS total_sales,
       SUM(profit) AS total_profit
FROM order_items;

-- A3. Total sales per kategori
SELECT p.category,
       SUM(oi.sales) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_sales DESC;


-- =====================================================================
-- B. PRODUK PALING LAKU
--    Catatan penting: "paling laku by UNIT" (SUM quantity) BISA BEDA
--    dari "paling cuan by REVENUE" (SUM sales).
-- =====================================================================

-- B1. Top 10 produk by UNIT terjual (SUM quantity, bukan COUNT!)
SELECT oi.product_id,
       p.product_name,
       SUM(oi.quantity) AS total_unit_terjual,
       SUM(oi.sales)    AS total_sales,
       SUM(oi.profit)   AS total_profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.product_name
ORDER BY total_unit_terjual DESC
LIMIT 10;

-- B2. Top 10 produk by REVENUE (bandingkan dengan B1 -> insight!)
SELECT oi.product_id,
       p.product_name,
       SUM(oi.sales)    AS total_sales,
       SUM(oi.quantity) AS total_unit_terjual
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY oi.product_id, p.product_name
ORDER BY total_sales DESC
LIMIT 10;


-- =====================================================================
-- C. TREN PENJUALAN PER TAHUN + GROWTH YoY
--    Konsep: CTE (WITH) + window function LAG().
--    Growth % = (sekarang - tahun_lalu) / tahun_lalu * 100
--    (pembagi = TAHUN LALU, bukan tahun sekarang!)
-- =====================================================================
WITH sales_per_year AS (
    SELECT YEAR(o.order_date) AS tahun,
           SUM(oi.sales)      AS total_sales
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY YEAR(o.order_date)
)
SELECT
    tahun,
    total_sales,
    LAG(total_sales) OVER (ORDER BY tahun) AS sales_tahun_lalu,
    ROUND(
        (total_sales - LAG(total_sales) OVER (ORDER BY tahun))
        / LAG(total_sales) OVER (ORDER BY tahun) * 100
    , 2) AS growth_persen
FROM sales_per_year
ORDER BY tahun;


-- =====================================================================
-- D. TREN PER KATEGORI + GROWTH YoY  (jawaban pertanyaan utama!)
--    Konsep baru: PARTITION BY category -> LAG reset per kategori,
--    jadi growth dibandingkan dalam kategori yang sama.
-- =====================================================================
WITH sales_per_year_cat AS (
    SELECT p.category,
           YEAR(o.order_date) AS tahun,
           SUM(oi.sales)      AS total_sales
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON p.product_id = oi.product_id
    GROUP BY p.category, YEAR(o.order_date)
)
SELECT
    category,
    tahun,
    total_sales,
    LAG(total_sales) OVER (PARTITION BY category ORDER BY tahun) AS sales_tahun_lalu,
    ROUND(
        (total_sales - LAG(total_sales) OVER (PARTITION BY category ORDER BY tahun))
        / LAG(total_sales) OVER (PARTITION BY category ORDER BY tahun) * 100
    , 2) AS growth_persen
FROM sales_per_year_cat
ORDER BY category, tahun;


-- =====================================================================
-- E. POLA MUSIMAN (seasonality)
--    Melengkapi analisis tren: selain tumbuh tiap tahun, apakah ada
--    bulan tertentu yang selalu ramai?
-- =====================================================================

-- E1. Total sales per BULAN (gabung semua tahun) -> bulan apa paling ramai?
--     Hasil data ini: puncak di November, lalu Desember (musim akhir tahun);
--     terendah di Januari.
SELECT
    MONTH(o.order_date)     AS bulan,
    MONTHNAME(o.order_date) AS nama_bulan,
    SUM(oi.sales)           AS total_sales
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
GROUP BY MONTH(o.order_date), MONTHNAME(o.order_date)
ORDER BY bulan;

-- E2. Total sales per BULAN per TAHUN (4 tahun x 12 bulan = 48 baris)
--     -> untuk melihat apakah pola musiman konsisten tiap tahun.
--     Cocok dijadikan line chart di Tableau (sumbu X = waktu, 1 garis per tahun).
SELECT
    YEAR(o.order_date)      AS tahun,
    MONTH(o.order_date)     AS bulan,
    MONTHNAME(o.order_date) AS nama_bulan,
    SUM(oi.sales)           AS total_sales
FROM order_items oi
JOIN orders o ON o.order_id = oi.order_id
GROUP BY YEAR(o.order_date), MONTH(o.order_date), MONTHNAME(o.order_date)
ORDER BY tahun, bulan;
