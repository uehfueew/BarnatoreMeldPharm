from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from models.db import mongo
from models.product import Product
from models.order import Order
from models.user import User
from models.categories import CATEGORIES
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    featured_products = Product.get_featured(limit=15)
    best_sellers = Product.get_best_sellers(limit=15)
    regular_products = Product.get_regular(limit=15)
    return render_template('index.html', 
                            featured_products=featured_products, 
                            best_sellers=best_sellers,
                            regular_products=regular_products,
                            categories=CATEGORIES)

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
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    subcategory = request.args.get('subcategory', 'all')
    search_query = request.args.get('q', '')
    per_page = 20
    
    products, total_pages = Product.get_paginated(page, per_page, category, search_query, subcategory)
    
    # If it's an AJAX request (from our new filter system)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results = []
        for p in products:
            results.append({
                'id': str(p['_id']),
                'name': p['name'],
                'brand': p.get('brand', ''),
                'price': p['price'],
                'discount_price': p.get('discount_price'),
                'image_url': p.get('image_url'),
                'images': p.get('images', []),
                'category': p.get('category'),
                'subcategory': p.get('subcategory'),
                'in_stock': p.get('in_stock', True),
                'size': p.get('size', ''),
                'is_favorite': (current_user.is_authenticated and p.get('favorites') and current_user.id in p.get('favorites')) or 
                               (not current_user.is_authenticated and str(p['_id']) in session.get('liked_products', []))
            })
        
        return jsonify({
            'products': results,
            'page': page,
            'total_pages': total_pages,
            'current_category': category,
            'current_subcategory': subcategory,
            'categories_config': CATEGORIES # To update subcategory choices
        })

    # Debug print
    print(f"Products found: {len(products)} on page {page} in category {category} subcategory {subcategory} search: {search_query}")
    return render_template('products.html', 
                         products=products, 
                         page=page, 
                         total_pages=total_pages,
                         current_category=category,
                         current_subcategory=subcategory,
                         search_query=search_query,
                         categories=CATEGORIES)

@main.route('/product/<product_id>')
def product_detail(product_id):
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
    return render_template('about.html')

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Duhet të jeni të kyçur për të kryer këtë veprim.', 'error')
            return redirect(url_for('auth.login'))
        
        profile_data = {
            'fullname': request.form.get('fullname'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'country': request.form.get('country'),
            'phone': request.form.get('phone')
        }
        User.update_profile(current_user.id, profile_data)
        flash('Profili u përditësua me sukses!', 'success')
        return redirect(url_for('main.profile'))

    favorites = []
    if current_user.is_authenticated:
        favorites = Product.get_favorites_by_user(current_user.id)
    else:
        # Check for guest favorites in session
        liked_ids = session.get('liked_products', [])
        if liked_ids:
            favorites = Product.get_by_ids(liked_ids)
            
    return render_template('profile.html', favorites=favorites)

@main.route('/orders')
def orders():
    if not current_user.is_authenticated:
        flash('Ju lutem kyçuni për të parë historinë e porosive.', 'info')
        return redirect(url_for('auth.login'))
        
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

@main.route('/api/search')
def search_api():
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)
    if not query or len(query) < 2:
        return jsonify([])
    
    # Search in name, category, or subcategory
    search_query = {
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}},
            {"subcategory": {"$regex": query, "$options": "i"}}
        ]
    }
    
    products = list(mongo.db.products.find(search_query).limit(limit))
    
    results = []
    for p in products:
        results.append({
            'id': str(p['_id']),
            'name': p['name'],
            'price': p['price'],
            'discount_price': p.get('discount_price'),
            'image_url': p.get('image_url'),
            'category': p.get('category'),
            'subcategory': p.get('subcategory')
        })
    
    return jsonify(results)
