CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50),
  email VARCHAR(100),
  password_hash VARCHAR(255),
  phone VARCHAR(15),
  address TEXT,
  created_at DATETIME
);

CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  description TEXT,
  price DECIMAL(10, 2),
  image TEXT,
  category_id INT,
  conditions ENUM('New','Like New','Used'),
  og_price INT,
  seller_id INT,
  quantity INT,
  created_at DATETIME,
  FOREIGN KEY (category_id) REFERENCES categories(category_id),
  FOREIGN KEY (seller_id) REFERENCES users(user_id),
  approved tinyint(1) DEFAULT 0
);

CREATE TABLE categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50)
);

CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  order_date DATETIME,
  status ENUM('Pending', 'Shipped', 'Delivered', 'Cancelled'),
  total DECIMAL(10, 2),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE order_items (
  order_item_id INT AUTO_INCREMENT PRIMARY KEY,
  order_id INT,
  id INT,
  quantity INT,
  price DECIMAL(10, 2),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (id) REFERENCES products(id)
);

CREATE TABLE cart (
  cart_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  created_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE cart_items (
  cart_item_id INT AUTO_INCREMENT PRIMARY KEY,
  cart_id INT,
  id INT,
  quantity INT,
  FOREIGN KEY (cart_id) REFERENCES cart(cart_id),
  FOREIGN KEY (id) REFERENCES products(id)
);

CREATE TABLE wishlist (
  wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  id INT,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (id) REFERENCES products(id)
);


