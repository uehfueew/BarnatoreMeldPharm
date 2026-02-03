from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required
from models.user import User
from flask_bcrypt import Bcrypt

auth = Blueprint('auth', __name__)
# We will init bcrypt with app in app.py, but here we can just use the class for hashing if needed, 
# or better, pass the bcrypt instance from app. 
# For now, let's instantiate a local Bcrypt, but ideally it should be the same instance. 
# A common pattern is extensions.py. Let's stick to simple:
bcrypt = Bcrypt()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.get_by_email(email)
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            # Sync Cart
            db_cart = User.get_cart(user.id)
            session_cart = session.get('cart', {})
            
            for pid, qty in session_cart.items():
                if pid in db_cart:
                    db_cart[pid] = int(db_cart[pid]) + int(qty)
                else:
                    db_cart[pid] = int(qty)
            
            User.update_cart(user.id, db_cart)
            session['cart'] = db_cart

            flash('Kycja ishte e suksesshme!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Kycja dështoi. Kontrolloni emailin dhe fjalëkalimin.', 'danger')
            
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email është rregjistruar tashmë.', 'warning')
            return redirect(url_for('auth.register'))
            
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User.create(username, email, hashed_pw)
        login_user(user)

        # Sync Cart for new user if they added items before registering
        session_cart = session.get('cart', {})
        if session_cart:
            User.update_cart(user.id, session_cart)

        flash('Llogaria u krijua! Mirë se erdhet.', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('guest_mode', None)
    session.pop('cart', None)
    return redirect(url_for('main.index'))
