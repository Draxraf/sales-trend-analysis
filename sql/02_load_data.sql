-- =====================================================================
-- 02_load_data.sql
-- Mengisi 4 tabel dari CSV mentah menggunakan pola "staging table".
--
-- Alur:
--   1. Buat tabel staging (cerminan CSV, 1 baris = 1 item)
--   2. Import CSV ke staging  <-- lewat DBeaver: klik kanan staging > Import Data
--      (Delimiter = koma ','  |  Header position = Top  |  Encoding = UTF-8)
--   3. Sebar staging -> customers, products, orders, order_items
--   4. (opsional) hapus staging
--
-- Urutan INSERT penting karena FK:
--   customers & products dulu -> orders -> order_items
-- =====================================================================

USE superstore;

-- ---------------------------------------------------------------------
-- Langkah 1: tabel staging (penampung mentah, tanpa PK/FK/constraint)
-- ---------------------------------------------------------------------
DROP TABLE IF EXISTS staging;
CREATE TABLE staging (
    order_id       VARCHAR(20),
    order_date     DATE,
    ship_mode      VARCHAR(20),
    customer_id    VARCHAR(11),
    customer_name  VARCHAR(50),
    segment        VARCHAR(20),
    region         VARCHAR(20),
    state          VARCHAR(50),
    city           VARCHAR(50),
    product_id     VARCHAR(11),
    product_name   VARCHAR(70),
    category       VARCHAR(20),
    sub_category   VARCHAR(20),
    quantity       INT,
    discount       DECIMAL(3,2),
    sales          DECIMAL(10,2),
    profit         DECIMAL(10,2)
);

-- Langkah 2: IMPORT CSV ke tabel staging via DBeaver (lihat catatan di atas).
-- Verifikasi setelah import:
--   SELECT COUNT(*) FROM staging;   -- target: 6253

-- ---------------------------------------------------------------------
-- Langkah 3: sebar staging -> 4 tabel
-- ---------------------------------------------------------------------

-- 3a. customers (DISTINCT -> 1 baris per customer unik, hindari PK dobel)
INSERT INTO customers (customer_id, customer_name, segment, region, state, city)
SELECT DISTINCT
    customer_id, customer_name, segment, region, state, city
FROM staging;
-- cek: SELECT COUNT(*) FROM customers;  -- target 120

-- 3b. products (DISTINCT -> 1 baris per produk unik)
INSERT INTO products (product_id, product_name, category, sub_category)
SELECT DISTINCT
    product_id, product_name, category, sub_category
FROM staging;
-- cek: SELECT COUNT(*) FROM products;  -- target 33

-- 3c. orders (DISTINCT -> 1 baris per order unik; TANPA sales/profit/quantity)
INSERT INTO orders (order_id, order_date, ship_mode, customer_id)
SELECT DISTINCT
    order_id, order_date, ship_mode, customer_id
FROM staging;
-- cek: SELECT COUNT(*) FROM orders;  -- target 2480

-- 3d. order_items (TANPA DISTINCT -> SEMUA baris item; id auto-increment)
INSERT INTO order_items (order_id, product_id, quantity, discount, sales, profit)
SELECT
    order_id, product_id, quantity, discount, sales, profit
FROM staging;
-- cek: SELECT COUNT(*) FROM order_items;  -- target 6253

-- ---------------------------------------------------------------------
-- Langkah 4 (opsional): buang staging setelah data tersebar
-- ---------------------------------------------------------------------
-- DROP TABLE IF EXISTS staging;
