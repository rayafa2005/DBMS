-- Insert Users
INSERT INTO Users (username, email, password_hash, phone, address)
VALUES 
  ('aa', 'alice@example.com', 'hashed_password_1', '1234567890', '123 Rose Street'),
  ('bb', 'bob@example.com', 'hashed_password_2', '0987654321', '456 Lily Avenue');

-- Insert Categories
INSERT INTO Categories (name)
VALUES 
  ('Dress'),
  ('Shirt'),
  ('Pant'),
  ('Skirt'),
  ('Jacket');

-- Insert Products
INSERT INTO Products (name, description, price, image_url, category_id, conditions, quantity, seller_id, created_at)
VALUES
  ('Dress', 'A stylish summer dress.', 499.99, 'dress.jpg', 1, 'Like New', 1000, 1, CURRENT_TIMESTAMP),
  ('Shirt', 'Casual blue cotton shirt.', 299.99, 'shirt.jpg', 2, 'New', 600, 2, CURRENT_TIMESTAMP),
  ('Pant', 'Black formal pants.', 399.00, 'pant.jpg', 3, 'Used', 798, 1, CURRENT_TIMESTAMP),
  ('Skirt', 'Floral mini skirt.', 249.50, 'skirt.jpg', 4, 'Like New', 499, 2, CURRENT_TIMESTAMP),
  ('Jacket', 'Vintage denim jacket.', 799.00, 'jacket.jpg', 5, 'Used', 1598, 1, CURRENT_TIMESTAMP);

SELECT * FROM raziyadb.products;
ALTER TABLE products ADD COLUMN approved BOOLEAN DEFAULT FALSE;

-- No Orders Yet
-- No Order_Items Yet
-- No Cart or Cart_Items Yet
-- No Wishlist Yet

