const bcrypt = require('bcryptjs');
const db = require('./data/db');

const schema = `
CREATE TABLE IF NOT EXISTS admins (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  price REAL NOT NULL,
  old_price REAL,
  category_id INTEGER,
  sizes TEXT,
  colors TEXT,
  is_featured INTEGER DEFAULT 0,
  is_active INTEGER DEFAULT 1,
  stock INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS product_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  image_path TEXT NOT NULL,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  state TEXT NOT NULL,
  notes TEXT,
  size TEXT,
  color TEXT,
  status TEXT DEFAULT 'طلب جديد',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
`;

db.exec(schema);

const adminExists = db.prepare('SELECT id FROM admins WHERE username = ?').get('admin');
if (!adminExists) {
  const hash = bcrypt.hashSync('Admin@123', 10);
  db.prepare('INSERT INTO admins (username, password_hash) VALUES (?, ?)').run('admin', hash);
}

const categoriesCount = db.prepare('SELECT COUNT(*) as count FROM categories').get().count;
if (!categoriesCount) {
  const categories = [
    ['ملابس رجالية', 'menswear'],
    ['ملابس نسائية', 'womenswear'],
    ['أحذية', 'shoes'],
    ['إكسسوارات', 'accessories']
  ];

  const insertCategory = db.prepare('INSERT INTO categories (name, slug) VALUES (?, ?)');
  categories.forEach((category) => insertCategory.run(...category));
}

const productsCount = db.prepare('SELECT COUNT(*) as count FROM products').get().count;
if (!productsCount) {
  const insertProduct = db.prepare(
    `INSERT INTO products (title, description, price, old_price, category_id, sizes, colors, is_featured, stock)
    VALUES (@title, @description, @price, @old_price, @category_id, @sizes, @colors, @is_featured, @stock)`
  );

  const p1 = insertProduct.run({
    title: 'قميص كاجوال فاخر',
    description: 'قميص قطني مريح مناسب للخروج والعمل.',
    price: 4500,
    old_price: 5200,
    category_id: 1,
    sizes: 'S,M,L,XL',
    colors: 'أسود,أبيض,أزرق',
    is_featured: 1,
    stock: 12
  }).lastInsertRowid;

  const p2 = insertProduct.run({
    title: 'فستان أنيق',
    description: 'فستان عصري بخامة ممتازة للمناسبات.',
    price: 7900,
    old_price: 8900,
    category_id: 2,
    sizes: 'M,L,XL',
    colors: 'أحمر,بيج,أسود',
    is_featured: 1,
    stock: 7
  }).lastInsertRowid;

  const addImage = db.prepare('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)');
  addImage.run(p1, '/uploads/sample-shirt.svg');
  addImage.run(p2, '/uploads/sample-dress.svg');
}

console.log('Database initialized successfully.');
console.log('Admin credentials => username: admin | password: Admin@123');
