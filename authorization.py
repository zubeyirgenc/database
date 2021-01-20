from functools import wraps
from flask import current_app, flash,redirect, url_for
from flask_login import login_required, current_user

def admin_required(func):
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash(u"Bu sayfaya giriş yetkiniz yok.", 'danger')
            return redirect(url_for("home_page"))
        return func(*args, **kwargs)
    return decorated_view

def member_required(func):
    @login_required
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_member:
            flash(u"Bu sayfaya giriş yetkiniz yok.", 'danger')
            return redirect(url_for("home_page"))
        return func(*args, **kwargs)
    return decorated_view