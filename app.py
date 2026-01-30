from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os

from models.db import init_db
from models.user import User
from routes.main import main
from routes.auth import auth
from routes.cart import cart_bp
from routes.admin import admin

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/meldpharm')

# Initialize Extensions
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
    cart = session.get('cart', {})
    count = sum(int(v) for v in cart.values())
    return dict(cart_count=count)

# Register Blueprints
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(cart_bp)
app.register_blueprint(admin)

if __name__ == '__main__':
    app.run(debug=True)
