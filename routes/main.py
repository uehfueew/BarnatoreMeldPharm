from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from models.product import Product
from models.order import Order
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # If user is logged in OR has chosen to continue as guest, show the main page (now called index template)
    if current_user.is_authenticated or session.get('guest_mode'):
        featured_products = Product.get_featured()
        return render_template('index.html', featured_products=featured_products)
    
    # Otherwise, show the welcome screen
    return render_template('welcome.html')

@main.route('/guest_login')
def guest_login():
    session['guest_mode'] = True
    return redirect(url_for('main.index'))

@main.route('/exit_guest')
def exit_guest():
    session.pop('guest_mode', None)
    return redirect(url_for('main.index'))

@main.route('/products')
def products():
    # Ensure user is allowed to see this page
    if not (current_user.is_authenticated or session.get('guest_mode')):
         return redirect(url_for('main.index'))
         
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    products, total_pages = Product.get_paginated(page, per_page)
    
    # Debug print
    print(f"Products found: {len(products)} on page {page}")
    return render_template('products.html', products=products, page=page, total_pages=total_pages)

from models.user import User

@main.route('/product/<product_id>')
def product_detail(product_id):
    if not (current_user.is_authenticated or session.get('guest_mode')):
         return redirect(url_for('main.index'))

    product = Product.get_by_id(product_id)
    if not product:
        return render_template('index.html') # Should be 404
    
    favorite_usernames = []
    if product.get('favorites'):
        for uid in product.get('favorites'):
            u = User.get_by_id(uid)
            if u:
                favorite_usernames.append(u.username)

    related_products = Product.get_related(product.get('category'), product.get('_id'))
    return render_template('product_detail.html', product=product, related_products=related_products, favorite_usernames=favorite_usernames)

@main.route('/about')
def about():
    if not (current_user.is_authenticated or session.get('guest_mode')):
         return redirect(url_for('main.index'))
    return render_template('about.html')

@main.route('/profile')
def profile():
    # Access profile even if guest, but it will show login/register forms basically
    # Or strict logic: if guest, show login/register. If logged in, show user info.
    return render_template('profile.html')

@main.route('/cart')
def cart():
    if not (current_user.is_authenticated or session.get('guest_mode')):
         return redirect(url_for('main.index'))
    return render_template('cart.html')

@main.route('/orders')
def orders():
    if not current_user.is_authenticated:
        # If guest mode, show page but with "Login needed" message inside.
        # Or redirect if not guest either.
        if not session.get('guest_mode'):
             return redirect(url_for('main.index'))
        return render_template('orders.html', orders=[], guest_access=True)
        
    user_orders = Order.get_by_user(current_user.id)
    return render_template('orders.html', orders=user_orders)

@main.route('/product/favorite/<product_id>', methods=['POST'])
def toggle_favorite(product_id):
    if current_user.is_authenticated:
        action = Product.toggle_favorite(product_id, current_user.id)
    else:
        # Guest User Logic
        liked_products = session.get('liked_products', [])
        
        if product_id in liked_products:
            liked_products.remove(product_id)
            action = 'removed'
        else:
            liked_products.append(product_id)
            action = 'added'
        
        session['liked_products'] = liked_products
        session.modified = True
    
    if action:
        return jsonify({'success': True, 'action': action})
    return jsonify({'success': False}), 400
