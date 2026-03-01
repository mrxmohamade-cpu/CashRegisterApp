const express = require('express');
const bcrypt = require('bcryptjs');
const multer = require('multer');
const path = require('path');
const sanitizeHtml = require('sanitize-html');
const dayjs = require('dayjs');
const db = require('../data/db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

const storage = multer.diskStorage({
  destination: (_, __, cb) => cb(null, path.join(__dirname, '../public/uploads')),
  filename: (_, file, cb) => cb(null, `${Date.now()}-${file.originalname.replace(/\s+/g, '-')}`)
});

const upload = multer({ storage });

router.get('/login', (req, res) => {
  res.render('admin/login', { error: null });
});

router.post('/login', (req, res) => {
  const username = (req.body.username || '').trim();
  const password = req.body.password || '';
  const admin = db.prepare('SELECT * FROM admins WHERE username = ?').get(username);

  if (!admin || !bcrypt.compareSync(password, admin.password_hash)) {
    return res.status(401).render('admin/login', { error: 'بيانات الدخول غير صحيحة' });
  }

  res.cookie('admin_session', admin.id, { httpOnly: true, sameSite: 'strict' });
  res.redirect('/admin');
});

router.post('/logout', (req, res) => {
  res.clearCookie('admin_session');
  res.redirect('/admin/login');
});

router.get('/', requireAdmin, (req, res) => {
  const stats = {
    totalOrders: db.prepare('SELECT COUNT(*) AS count FROM orders').get().count,
    confirmedOrders: db.prepare("SELECT COUNT(*) AS count FROM orders WHERE status = 'تم تأكيد الطلب'").get().count,
    canceledOrders: db.prepare("SELECT COUNT(*) AS count FROM orders WHERE status = 'ملغي'").get().count,
    products: db.prepare('SELECT COUNT(*) AS count FROM products').get().count
  };

  const recentOrders = db.prepare(`SELECT o.*, p.title AS product_title FROM orders o
    LEFT JOIN products p ON p.id = o.product_id ORDER BY o.created_at DESC LIMIT 10`).all();

  res.render('admin/dashboard', { stats, recentOrders, dayjs });
});

router.get('/products', requireAdmin, (req, res) => {
  const products = db.prepare(`SELECT p.*, c.name AS category_name,
    (SELECT image_path FROM product_images pi WHERE pi.product_id = p.id LIMIT 1) AS image
    FROM products p LEFT JOIN categories c ON c.id = p.category_id ORDER BY p.created_at DESC`).all();
  const categories = db.prepare('SELECT * FROM categories').all();
  res.render('admin/products', { products, categories });
});

router.post('/products', requireAdmin, upload.array('images', 5), (req, res) => {
  const body = req.body;
  const data = {
    title: sanitizeHtml(body.title || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    description: sanitizeHtml(body.description || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    price: Number(body.price || 0),
    old_price: Number(body.old_price || 0) || null,
    category_id: Number(body.category_id),
    sizes: (body.sizes || '').trim(),
    colors: (body.colors || '').trim(),
    is_featured: body.is_featured ? 1 : 0,
    is_active: body.is_active ? 1 : 0,
    stock: Number(body.stock || 0)
  };

  const productId = db.prepare(`INSERT INTO products
    (title, description, price, old_price, category_id, sizes, colors, is_featured, is_active, stock)
    VALUES (@title, @description, @price, @old_price, @category_id, @sizes, @colors, @is_featured, @is_active, @stock)`).run(data).lastInsertRowid;

  const addImage = db.prepare('INSERT INTO product_images (product_id, image_path) VALUES (?, ?)');
  (req.files || []).forEach((file) => addImage.run(productId, `/uploads/${file.filename}`));

  res.redirect('/admin/products');
});

router.post('/products/:id/toggle', requireAdmin, (req, res) => {
  db.prepare('UPDATE products SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?').run(req.params.id);
  res.redirect('/admin/products');
});

router.post('/products/:id/delete', requireAdmin, (req, res) => {
  db.prepare('DELETE FROM product_images WHERE product_id = ?').run(req.params.id);
  db.prepare('DELETE FROM products WHERE id = ?').run(req.params.id);
  res.redirect('/admin/products');
});

router.get('/categories', requireAdmin, (req, res) => {
  const categories = db.prepare('SELECT * FROM categories ORDER BY id DESC').all();
  res.render('admin/categories', { categories });
});

router.post('/categories', requireAdmin, (req, res) => {
  const name = sanitizeHtml(req.body.name || '', { allowedTags: [], allowedAttributes: {} }).trim();
  const slug = name.toLowerCase().replace(/\s+/g, '-');
  if (name) {
    db.prepare('INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)').run(name, slug);
  }
  res.redirect('/admin/categories');
});

router.post('/categories/:id/delete', requireAdmin, (req, res) => {
  db.prepare('DELETE FROM categories WHERE id = ?').run(req.params.id);
  res.redirect('/admin/categories');
});

router.get('/orders', requireAdmin, (req, res) => {
  const q = (req.query.phone || '').trim();
  let orders;
  if (q) {
    orders = db.prepare(`SELECT o.*, p.title AS product_title FROM orders o
      LEFT JOIN products p ON p.id = o.product_id WHERE o.phone LIKE ? ORDER BY o.created_at DESC`).all(`%${q}%`);
  } else {
    orders = db.prepare(`SELECT o.*, p.title AS product_title FROM orders o
      LEFT JOIN products p ON p.id = o.product_id ORDER BY o.created_at DESC`).all();
  }
  res.render('admin/orders', { orders, phone: q, dayjs });
});

router.post('/orders/:id/status', requireAdmin, (req, res) => {
  const allowed = ['طلب جديد', 'تم الاتصال بالزبون', 'تم تأكيد الطلب', 'تم الشحن', 'تم التسليم', 'ملغي'];
  const status = req.body.status;
  if (allowed.includes(status)) {
    db.prepare('UPDATE orders SET status = ? WHERE id = ?').run(status, req.params.id);
  }
  res.redirect('/admin/orders');
});

module.exports = router;
