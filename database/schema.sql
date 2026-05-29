-- ============================================================
-- Restaurant AI System - Database Schema
-- Phase 1: Core Tables for Billing, Inventory, and ML Pipeline
-- ============================================================

CREATE DATABASE IF NOT EXISTS restaurant_ai_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE restaurant_ai_db;

-- ============================================================
-- 1. USERS & AUTHENTICATION
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100) NOT NULL,
    role            ENUM('ADMIN', 'MANAGER', 'CASHIER') NOT NULL DEFAULT 'CASHIER',
    email           VARCHAR(100) UNIQUE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 2. MENU ITEMS
-- ============================================================

CREATE TABLE IF NOT EXISTS menu_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    item_name       VARCHAR(100) NOT NULL,
    category        VARCHAR(50)  NOT NULL COMMENT 'e.g. Fastfood, Beverages, Burgers, Fries',
    subcategory     VARCHAR(50)  DEFAULT NULL COMMENT 'e.g. Veg, Non-Veg',
    item_type       VARCHAR(50)  DEFAULT NULL COMMENT 'e.g. Fastfood, Beverages',
    price           DECIMAL(10,2) NOT NULL,
    is_available    BOOLEAN NOT NULL DEFAULT TRUE,
    description     TEXT DEFAULT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_menu_item (item_name, category)
) ENGINE=InnoDB;

-- ============================================================
-- 3. ORDERS & ORDER ITEMS  (Smart Billing Core)
-- ============================================================

CREATE TABLE IF NOT EXISTS orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    order_date      DATE NOT NULL,
    order_time      TIME DEFAULT NULL,
    time_of_sale    VARCHAR(20) DEFAULT NULL COMMENT 'Morning, Afternoon, Evening, Night, Midnight',
    total_amount    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    payment_method  VARCHAR(30) DEFAULT NULL COMMENT 'Cash, Online, Credit Card, Gift Card',
    purchase_type   VARCHAR(30) DEFAULT NULL COMMENT 'In-store, Online, Drive-thru',
    cashier_id      INT DEFAULT NULL,
    manager_name    VARCHAR(100) DEFAULT NULL,
    city            VARCHAR(50)  DEFAULT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cashier_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    menu_item_id    INT NOT NULL,
    quantity        INT NOT NULL DEFAULT 1,
    unit_price      DECIMAL(10,2) NOT NULL,
    subtotal        DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (order_id)    REFERENCES orders(id)     ON DELETE CASCADE,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ============================================================
-- 4. INVENTORY MANAGEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS inventory (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    item_id         INT DEFAULT NULL COMMENT 'FK to a raw material / ingredient lookup',
    item_name       VARCHAR(100) NOT NULL,
    category        VARCHAR(50)  NOT NULL COMMENT 'Veg, Non-Veg',
    subcategory     VARCHAR(50)  DEFAULT NULL COMMENT 'Dairy, Vegetable, Meat, Fish, Poultry, Grain, Grocery',
    unit            VARCHAR(20)  NOT NULL COMMENT 'kg, liter, pieces',
    current_stock   DECIMAL(10,2) NOT NULL DEFAULT 0,
    reorder_level   DECIMAL(10,2) NOT NULL DEFAULT 0,
    daily_usage     DECIMAL(10,2) DEFAULT 0,
    lead_time_days  INT DEFAULT 1,
    price_per_unit  DECIMAL(10,2) DEFAULT 0,
    supplier_name   VARCHAR(100) DEFAULT NULL,
    seasonal_factor DECIMAL(4,2) DEFAULT 1.00,
    waste_pct       DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Waste percentage 0-100',
    record_date     DATE NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 5. RECIPE MASTER  (Bill of Materials / BOM Mapping)
-- ============================================================

CREATE TABLE IF NOT EXISTS recipe_master (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id    INT NOT NULL,
    ingredient_name VARCHAR(100) NOT NULL,
    quantity_needed DECIMAL(10,3) NOT NULL COMMENT 'Amount of ingredient needed per 1 unit of dish',
    unit            VARCHAR(20)  NOT NULL COMMENT 'kg, liter, pieces, grams, ml',
    ingredient_category VARCHAR(50) DEFAULT NULL,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 6. FESTIVALS & HOLIDAYS  (Special Demand Intelligence)
-- ============================================================

CREATE TABLE IF NOT EXISTS festivals (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    festival_name   VARCHAR(100) NOT NULL,
    festival_date   DATE NOT NULL,
    is_holiday      BOOLEAN NOT NULL DEFAULT TRUE,
    expected_impact ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM' COMMENT 'Expected demand impact',
    notes           TEXT DEFAULT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_festival_date (festival_name, festival_date)
) ENGINE=InnoDB;

-- ============================================================
-- 7. ML PREDICTIONS  (Demand Forecasting Output)
-- ============================================================

CREATE TABLE IF NOT EXISTS predictions (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id        INT NOT NULL,
    prediction_date     DATE NOT NULL,
    predicted_quantity  DECIMAL(10,2) NOT NULL,
    confidence_lower    DECIMAL(10,2) DEFAULT NULL,
    confidence_upper    DECIMAL(10,2) DEFAULT NULL,
    model_name          VARCHAR(50) DEFAULT NULL COMMENT 'e.g. RandomForest, XGBoost, LSTM',
    model_version       VARCHAR(20) DEFAULT NULL,
    is_festival_day     BOOLEAN DEFAULT FALSE,
    actual_quantity      DECIMAL(10,2) DEFAULT NULL COMMENT 'Filled in after the day passes',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE,
    UNIQUE KEY uq_prediction (menu_item_id, prediction_date, model_name)
) ENGINE=InnoDB;

-- ============================================================
-- 8. ML TRAINING FEATURES  (Preprocessed Feature Store)
-- ============================================================

CREATE TABLE IF NOT EXISTS ml_features (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    menu_item_id    INT NOT NULL,
    sale_date       DATE NOT NULL,
    day_of_week     TINYINT NOT NULL COMMENT '0=Monday, 6=Sunday',
    is_weekend      BOOLEAN NOT NULL DEFAULT FALSE,
    month           TINYINT NOT NULL,
    quantity_sold   INT NOT NULL DEFAULT 0,
    revenue         DECIMAL(12,2) DEFAULT 0,
    lag_1_day       INT DEFAULT NULL COMMENT 'Sales quantity 1 day ago',
    lag_7_day       INT DEFAULT NULL COMMENT 'Sales quantity 7 days ago',
    rolling_avg_7   DECIMAL(10,2) DEFAULT NULL COMMENT '7-day rolling average',
    is_festival     BOOLEAN DEFAULT FALSE,
    price           DECIMAL(10,2) DEFAULT NULL,
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 9. INVENTORY PREDICTIONS  (Waste Optimization Output)
-- ============================================================

CREATE TABLE IF NOT EXISTS inventory_predictions (
    id                          INT AUTO_INCREMENT PRIMARY KEY,
    inventory_item_name         VARCHAR(100) NOT NULL COMMENT 'Name of the inventory ingredient',
    prediction_date             DATE NOT NULL,
    current_stock               DECIMAL(10,2) DEFAULT NULL,
    daily_usage                 DECIMAL(10,2) DEFAULT NULL,
    predicted_waste_percentage  DECIMAL(5,2) NOT NULL,
    action_recommended          VARCHAR(100) DEFAULT NULL COMMENT 'e.g. Reduce Reorder Level, Stock is Optimal',
    model_name                  VARCHAR(50) DEFAULT 'RandomForest',
    model_version               VARCHAR(20) DEFAULT NULL,
    actual_waste_percentage     DECIMAL(5,2) DEFAULT NULL COMMENT 'Filled in after actual data is available',
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_inv_prediction (inventory_item_name, prediction_date, model_name)
) ENGINE=InnoDB;

-- ============================================================
-- 10. INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_payment ON orders(payment_method);
CREATE INDEX idx_inventory_date ON inventory(record_date);
CREATE INDEX idx_inventory_item ON inventory(item_name);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_ml_features_date ON ml_features(sale_date);
CREATE INDEX idx_ml_features_item ON ml_features(menu_item_id);
CREATE INDEX idx_inv_predictions_date ON inventory_predictions(prediction_date);
CREATE INDEX idx_inv_predictions_item ON inventory_predictions(inventory_item_name);
