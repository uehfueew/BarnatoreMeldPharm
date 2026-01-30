from flask import Blueprint, render_template, redirect, url_for, flash, request
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
        User.create(username, email, hashed_pw)
        flash('Llogaria u krijua! Tani mund të kyçeni.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Ju jeni çkyçur.', 'info')
    return redirect(url_for('main.index'))
