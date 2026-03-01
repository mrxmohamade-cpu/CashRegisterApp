function requireAdmin(req, res, next) {
  if (!req.cookies.admin_session) {
    return res.redirect('/admin/login');
  }
  next();
}

module.exports = { requireAdmin };
