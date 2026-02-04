import os
from dotenv import load_dotenv
from flask import Flask, render_template, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from models.db import init_db
from models.user import User
from routes.main import main
from routes.auth import auth
from routes.cart import cart_bp
from routes.admin import admin

csrf = CSRFProtect()

load_dotenv(override=True)

app = Flask(__name__)

# Trust headers from Render's proxy (Crucial for HTTPS)
if os.getenv('RENDER'):
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Security Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/meldpharm')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Secure cookies only if explicit or safely on Render (HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('RENDER') is not None 

# Initialize Extensions
csrf.init_app(app)
init_db(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.context_processor
def inject_cart_count():
    from flask import session
    from flask_login import current_user
    
    # Only show cart count if user is logged in
    if not current_user.is_authenticated:
        return dict(cart_count=0)

    cart = session.get('cart', {})
    count = sum(int(v) for v in cart.values())
    return dict(cart_count=count)

# Register Blueprints
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(cart_bp)
app.register_blueprint(admin)

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
