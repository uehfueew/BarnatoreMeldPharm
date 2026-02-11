import os
import logging
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, session, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

from models.db import init_db, mongo
from bson import ObjectId
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
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31) # Keep cart for 31 days
# Secure cookies only if explicit or safely on Render (HTTPS)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('RENDER') is not None 

@app.before_request
def make_session_permanent():
    session.permanent = True 

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
    from models.categories import CATEGORIES
    from flask_login import current_user
    import logging
    
    try:
        cart = session.get('cart', {})
        cart_count = sum(int(v) for v in cart.values()) if cart else 0
        
        cart_items = []
        total_price = 0
        total_savings = 0
        
        if cart:
            # Ensure mongo.db is available
            if mongo and mongo.db:
                product_ids = []
                for pid in cart.keys():
                    if pid and ObjectId.is_valid(str(pid)):
                        product_ids.append(ObjectId(str(pid)))
                        
                if product_ids:
                    # Using a list to ensure we can iterate multiple times or just to be safe with the cursor
                    products_cursor = list(mongo.db.products.find({"_id": {"$in": product_ids}}))
                    products_db = {str(p['_id']): p for p in products_cursor}
                    
                    for pid, qty in cart.items():
                        product = products_db.get(str(pid))
                        if product:
                            try:
                                # Ensure _id is a string for Jinja
                                product['_id'] = str(product['_id'])
                                p_price = product.get('discount_price') or product.get('price') or 0
                                original_price = product.get('price') or 0
                                qty_int = int(qty)
                                
                                item_total = float(p_price) * qty_int
                                item_savings = (float(original_price) - float(p_price)) * qty_int if product.get('discount_price') else 0
                                
                                total_price += item_total
                                total_savings += item_savings
                                
                                product['quantity'] = qty_int
                                product['item_total'] = item_total
                                product['item_savings'] = item_savings
                                cart_items.append(product)
                            except (ValueError, TypeError):
                                continue

        # Calculate Delivery Fee (Global context processor version)
        from routes.cart import calculate_shipping
        country = current_user.country if current_user.is_authenticated and current_user.country else 'Kosova'
        delivery_fee = calculate_shipping(total_price, country)
        grand_total = total_price + delivery_fee

        # Calculate Wishlist Count
        wish_count = 0
        try:
            if current_user.is_authenticated:
                # Count products where user_id is in favorites list
                wish_count = mongo.db.products.count_documents({"favorites": str(current_user.id)})
            else:
                wish_count = len(session.get('liked_products', []))
        except:
            pass

        return dict(
            cart_count=int(cart_count), 
            cart_items=cart_items,
            cart_total=float(total_price),
            cart_savings=float(total_savings),
            delivery_fee=float(delivery_fee),
            grand_total=float(grand_total),
            wishlist_count=int(wish_count), 
            global_categories=CATEGORIES
        )
    except Exception as e:
        import traceback
        logging.error(f"Error in inject_cart_count: {e}")
        logging.error(traceback.format_exc())
        return dict(
            cart_count=0, 
            cart_items=[],
            cart_total=0,
            cart_savings=0,
            delivery_fee=0,
            grand_total=0,
            wishlist_count=0,
            global_categories=CATEGORIES
        )

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
    app.run(debug=True, port=5001)
