-- Core seed data for the platform
-- This file will be executed after schema.sql during database initialization

INSERT INTO inventory_items (sku, quantity_available, price) VALUES
    ('SKU-1001', 1000000, 29.99),
    ('SKU-1002', 1000000, 9.99),
    ('SKU-1003', 1000000, 99.99),
    ('SKU-1004', 1000000, 149.50),
    ('SKU-1005', 1000000, 49.99)
ON CONFLICT (sku) DO UPDATE SET quantity_available = EXCLUDED.quantity_available;
