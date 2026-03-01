const express = require('express');
const sanitizeHtml = require('sanitize-html');
const db = require('../data/db');

const router = express.Router();

function getProductWithImageClause() {
  return `
  SELECT p.*, c.name AS category_name,
         (SELECT image_path FROM product_images pi WHERE pi.product_id = p.id LIMIT 1) AS image
  FROM products p
  LEFT JOIN categories c ON p.category_id = c.id
  `;
}

router.get('/', (req, res) => {
  const featured = db.prepare(`${getProductWithImageClause()} WHERE p.is_featured = 1 AND p.is_active = 1 ORDER BY p.created_at DESC LIMIT 8`).all();
  const latest = db.prepare(`${getProductWithImageClause()} WHERE p.is_active = 1 ORDER BY p.created_at DESC LIMIT 8`).all();
  const categories = db.prepare('SELECT * FROM categories').all();

  res.render('home', { featured, latest, categories });
});

router.get('/products', (req, res) => {
  const { minPrice, maxPrice, category, size, color, sort = 'latest' } = req.query;
  const categories = db.prepare('SELECT * FROM categories').all();

  const conditions = ['p.is_active = 1'];
  const params = {};

  if (minPrice) {
    conditions.push('p.price >= @minPrice');
    params.minPrice = Number(minPrice);
  }
  if (maxPrice) {
    conditions.push('p.price <= @maxPrice');
    params.maxPrice = Number(maxPrice);
  }
  if (category) {
    conditions.push('p.category_id = @category');
    params.category = Number(category);
  }
  if (size) {
    conditions.push('p.sizes LIKE @size');
    params.size = `%${size}%`;
  }
  if (color) {
    conditions.push('p.colors LIKE @color');
    params.color = `%${color}%`;
  }

  const orderBy = {
    latest: 'p.created_at DESC',
    priceAsc: 'p.price ASC',
    priceDesc: 'p.price DESC'
  }[sort] || 'p.created_at DESC';

  const sql = `${getProductWithImageClause()} WHERE ${conditions.join(' AND ')} ORDER BY ${orderBy}`;
  const products = db.prepare(sql).all(params);

  res.render('products', { products, categories, filters: req.query });
});

router.get('/products/:id', (req, res) => {
  const product = db.prepare('SELECT p.*, c.name AS category_name FROM products p LEFT JOIN categories c ON c.id = p.category_id WHERE p.id = ? AND p.is_active = 1').get(req.params.id);
  if (!product) return res.status(404).send('المنتج غير موجود');

  const images = db.prepare('SELECT * FROM product_images WHERE product_id = ?').all(req.params.id);
  res.render('product-details', { product, images });
});

router.post('/order/:productId', (req, res) => {
  const product = db.prepare('SELECT id, sizes, colors FROM products WHERE id = ? AND is_active = 1').get(req.params.productId);
  if (!product) return res.status(404).send('المنتج غير متاح');

  const clean = {
    first_name: sanitizeHtml(req.body.first_name || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    last_name: sanitizeHtml(req.body.last_name || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    phone: sanitizeHtml(req.body.phone || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    state: sanitizeHtml(req.body.state || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    notes: sanitizeHtml(req.body.notes || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    size: sanitizeHtml(req.body.size || '', { allowedTags: [], allowedAttributes: {} }).trim(),
    color: sanitizeHtml(req.body.color || '', { allowedTags: [], allowedAttributes: {} }).trim()
  };

  if (!clean.first_name || !clean.last_name || !clean.phone || !clean.state) {
    return res.status(400).send('يرجى ملء البيانات المطلوبة.');
  }

  db.prepare(`INSERT INTO orders (product_id, first_name, last_name, phone, state, notes, size, color)
              VALUES (@product_id, @first_name, @last_name, @phone, @state, @notes, @size, @color)`)
    .run({ product_id: req.params.productId, ...clean });

  res.render('order-success');
});

module.exports = router;
