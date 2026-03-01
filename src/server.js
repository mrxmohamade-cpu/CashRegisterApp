const express = require('express');
const path = require('path');
const helmet = require('helmet');
const cookieParser = require('cookie-parser');
const methodOverride = require('method-override');
const rateLimit = require('express-rate-limit');
const csrf = require('csurf');

require('./setupDb');
const shopRoutes = require('./routes/shop');
const adminRoutes = require('./routes/admin');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(helmet({ contentSecurityPolicy: false }));
app.use('/uploads', express.static(path.join(__dirname, 'public/uploads')));
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(methodOverride('_method'));

const limiter = rateLimit({ windowMs: 15 * 60 * 1000, limit: 120 });
app.use(limiter);

const csrfProtection = csrf({ cookie: true });
app.use(csrfProtection);
app.use((req, res, next) => {
  res.locals.csrfToken = req.csrfToken();
  res.locals.currentPath = req.path;
  next();
});

app.use(shopRoutes);
app.use('/admin', adminRoutes);

app.use((err, req, res, next) => {
  if (err.code === 'EBADCSRFTOKEN') {
    return res.status(403).send('رمز أمان غير صالح، حاول تحديث الصفحة.');
  }
  console.error(err);
  res.status(500).send('حدث خطأ داخلي في الخادم.');
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
