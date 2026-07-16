-- Core seed data for the platform
-- This file will be executed after schema.sql during database initialization

INSERT INTO inventory_items (sku, quantity_available, price) VALUES
    ('SKU-1001', 50, 29.99),
    ('SKU-1002', 200, 9.99),
    ('SKU-1003', 0, 99.99),
    ('SKU-1004', 15, 149.50)
ON CONFLICT (sku) DO NOTHING;
