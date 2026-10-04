-- =====================================================================
-- 01_schema.sql
-- Membuat database + 4 tabel ternormalisasi untuk project
-- Sales Trend Analysis (MySQL 8 / dikerjakan via DBeaver).
--
-- Desain:
--   customers ──┐
--               ├──> orders ──> order_items <── products
--               │  (header)     (detail/item)
--
-- Urutan CREATE penting karena foreign key:
--   customers & products dulu -> orders -> order_items
-- =====================================================================

CREATE DATABASE IF NOT EXISTS superstore;
USE superstore;

-- Jika dijalankan ulang: hapus dulu (urutan DIBALIK karena FK)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ---------------------------------------------------------------------
-- 1. customers : 1 baris = 1 pelanggan
-- ---------------------------------------------------------------------
CREATE TABLE customers (
    customer_id    VARCHAR(11) NOT NULL PRIMARY KEY
                   CHECK (customer_id REGEXP '^CUST-[0-9]{4}$'),
    customer_name  VARCHAR(50) NOT NULL,
    segment        VARCHAR(20) NOT NULL,
    region         VARCHAR(20) NOT NULL,
    state          VARCHAR(50) NOT NULL,
    city           VARCHAR(50) NOT NULL
);

-- ---------------------------------------------------------------------
-- 2. products : 1 baris = 1 produk
-- ---------------------------------------------------------------------
CREATE TABLE products (
    product_id    VARCHAR(11) NOT NULL PRIMARY KEY
                  CHECK (product_id REGEXP '^PROD-[0-9]{4}$'),
    product_name  VARCHAR(70) NOT NULL,
    category      VARCHAR(20) NOT NULL,
    sub_category  VARCHAR(20) NOT NULL
);

-- ---------------------------------------------------------------------
-- 3. orders : 1 baris = 1 order (header). FK -> customers
-- ---------------------------------------------------------------------
CREATE TABLE orders (
    order_id     VARCHAR(20) NOT NULL PRIMARY KEY,
    order_date   DATE NOT NULL,
    ship_mode    VARCHAR(20) NOT NULL,
    customer_id  VARCHAR(11) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ---------------------------------------------------------------------
-- 4. order_items : 1 baris = 1 item dalam sebuah order.
--    FK -> orders dan products. PK auto-increment.
--    sales/profit DECIMAL(10,2) (profit bisa minus = jual rugi).
-- ---------------------------------------------------------------------
CREATE TABLE order_items (
    order_items_id  INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    order_id        VARCHAR(20) NOT NULL,
    product_id      VARCHAR(11) NOT NULL,
    quantity        INT NOT NULL,
    discount        DECIMAL(3,2) NOT NULL,
    sales           DECIMAL(10,2) NOT NULL,
    profit          DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
