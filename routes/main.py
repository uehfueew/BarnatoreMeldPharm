from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from models.db import mongo
from models.product import Product
from models.order import Order
from models.user import User
from models.categories import CATEGORIES
from models.banner import Banner
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    import math
    featured_products = Product.get_featured(limit=20)
    best_sellers = Product.get_best_sellers(limit=20)
    
    # Get regular products with count and total pages for pagination
    # Changed from get_regular to get_paginated(page=1) to include all products and match store logic
    regular_products, total_pages_regular, total_regular = Product.get_paginated(page=1, per_page=20)
    
    # Get active offer banners
    offer_banners = Banner.get_active()
    
    return render_template('index.html', 
                            featured_products=featured_products, 
                            best_sellers=best_sellers,
                            regular_products=regular_products,
                            total_pages_regular=total_pages_regular,
                            categories=CATEGORIES,
                            offer_banners=offer_banners)

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
    # Automatically revert expired offers
    Product.revert_expired_offers()
    
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    subcategory = request.args.get('subcategory', 'all')
    search_query = request.args.get('search') or request.args.get('q', '')
    
    # Custom products comma separated support
    comma_searches = [s.strip() for s in search_query.split(',')] if ',' in search_query else None
    sort = request.args.get('sort', 'newest')
    brand = request.args.get('brand', 'all')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    discount_only = request.args.get('discount_only') == 'true'
    no_discount = request.args.get('no_discount') == 'true'
    best_sellers = request.args.get('best_sellers') == 'true'
    per_page = 20
    if request.args.get('all') == 'true':
        per_page = 1000 # Show all products
    
    pharmacist_choice = request.args.get('pharmacist_choice') == 'true'
    
    products, total_pages, total_count = Product.get_paginated(
        page, per_page, category, search_query, subcategory, 
        sort=sort, brand=brand, min_price=min_price, max_price=max_price,
        discount_only=discount_only, best_seller_only=best_sellers,
        no_discount=no_discount, pharmacist_choice=pharmacist_choice
    )
    
    # Get all unique brands for the filter sidebar
    filter_query = {"is_deleted": {"$ne": True}}
    if category != 'all':
        filter_query["category"] = category
    if subcategory != 'all':
        import re
        escaped_sub = re.escape(subcategory.strip())
        filter_query["subcategory"] = {"$regex": f"^\\s*{escaped_sub}\\s*$", "$options": "i"}
    raw_brands = mongo.db.products.distinct("brand", filter_query)
    brand_map = {}
    for rb in raw_brands:
        if rb:
            normalized = rb.strip().lower()
            # If we see multiple versions, prefer the one with most capital letters or just the first one
            if normalized not in brand_map:
                brand_map[normalized] = rb.strip()
    available_brands = sorted(brand_map.values(), key=lambda x: x.lower())
    
    # If it's an AJAX request (from our new filter system)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == '1':
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
                'is_best_seller': p.get('is_best_seller', False),
                'is_favorite': (current_user.is_authenticated and p.get('favorites') and current_user.id in p.get('favorites')) or 
                               (not current_user.is_authenticated and str(p['_id']) in session.get('liked_products', []))
            })
        
        return jsonify({
            'products': results,
            'page': page,
            'total_pages': total_pages,
            'total_count': total_count,
            'current_category': category,
            'current_subcategory': subcategory,
            'current_brand': brand,
            'sort': sort,
            'best_sellers': best_sellers,
            'available_brands': available_brands
        })

    return render_template('products.html', 
                         products=products, 
                         page=page, 
                         total_pages=total_pages,
                         total_count=total_count,
                         current_category=category,
                         current_subcategory=subcategory,
                         current_brand=brand,
                         search_query=search_query,
                         categories=CATEGORIES,
                         brands=available_brands,
                         discount_only=discount_only,
                         best_sellers=best_sellers)

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
    
    # Increment view count
    try:
        from bson import ObjectId
        from models.db import mongo
        mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$inc": {"views": 1}})
    except Exception as e:
        print(f"Error incrementing views: {e}")
    
    
    favorite_usernames = []
    if product.get('favorites'):
        for uid in product.get('favorites'):
            u = User.get_by_id(uid)
            if u:
                favorite_usernames.append(u.username)

    related_products = Product.get_related(product.get('category'), product.get('_id'), limit=12)
    # The limit is set to 12 directly inside get_related

    # Fetch variants if they exist (By Group ID or Name fallback)
    variants = []
    variant_group = product.get('variant_group')
    product_name = product.get('name')
    
    all_variants = Product.get_variants(variant_group, product_name)
    if all_variants and len(all_variants) > 1:
        variants = all_variants

    return render_template('product_detail.html', 
                            product=product, 
                            related_products=related_products, 
                            favorite_usernames=favorite_usernames,
                            variants=variants)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        profile_data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone': request.form.get('phone')
        }
        User.update_profile(current_user.id, profile_data)
        flash('Të dhënat personale u përditësuan!', 'success')
        return redirect(url_for('main.profile'))
    return render_template('profile.html')

@main.route('/profile/address', methods=['GET', 'POST'])
@login_required
def address():
    if request.method == 'POST':
        address_data = {
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'country': request.form.get('country'),
            'specifikat': request.form.get('specifikat') # Optional field
        }
        User.update_profile(current_user.id, address_data)
        flash('Adresa u përditësua me sukses!', 'success')
        return redirect(url_for('main.address'))
    return render_template('address.html')

@main.route('/wishlist')
def wishlist():
    favorites = []
    if current_user.is_authenticated:
        favorites = Product.get_favorites_by_user(current_user.id)
    else:
        liked_ids = session.get('liked_products', [])
        if liked_ids:
            favorites = Product.get_by_ids(liked_ids)
    return render_template('wishlist.html', favorites=favorites)

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
        # Get new count
        if current_user.is_authenticated:
            # Count products where user_id is in favorites list
            new_count = mongo.db.products.count_documents({"favorites": str(current_user.id)})
        else:
            new_count = len(session.get('liked_products', []))
            
        return jsonify({'success': True, 'action': action, 'count': new_count})
    return jsonify({'success': False}), 400

@main.route('/api/search')
def search_api():
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 20, type=int)
    if not query or len(query) < 2:
        return jsonify([])
    
    # Fuzzy search: require all terms in the query to be present
    import re
    terms = [t for t in query.split() if t]
    search_query = {}
    if terms:
        and_parts = []
        for t in terms:
            escaped_term = re.escape(t)
            and_parts.append({
                "$or": [
                    {"name": {"$regex": escaped_term, "$options": "i"}},
                    {"brand": {"$regex": escaped_term, "$options": "i"}},
                    {"category": {"$regex": escaped_term, "$options": "i"}},
                    {"subcategory": {"$regex": escaped_term, "$options": "i"}}
                ]
            })
        search_query = {"$and": and_parts, "is_deleted": {"$ne": True}}
    else:
        return jsonify([])
    
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
            'subcategory': p.get('subcategory'),
            'brand': p.get('brand', ''),
            'size': p.get('size', '')
        })
    
    return jsonify(results)

@main.route('/quiz')
def quiz():
    return render_template('quiz.html')

@main.route('/quiz/results')
def quiz_results():
    skin_type = request.args.get('skin_type', '')
    concern = request.args.get('concern', '')
    
    # Advanced logic: Map concerns to specific subcategories
    mapping = {
        'Akne': 'Kundër Akneve',
        'Anti-aging': 'Anti-aging & Rrudhat',
        'Hidratim': 'Hidratues',
        'Shkëlqim': 'Serume & Trajtime'
    }
    
    subcategory = mapping.get(concern)
    
    if subcategory:
        return redirect(url_for('main.products', category='Dermokozmetikë', subcategory=subcategory))
    
    # Fallback to general search if no direct subcategory match
    query = f"{skin_type} {concern}".strip()
    return redirect(url_for('main.products', category='Dermokozmetikë', q=query))

@main.route('/banner/<banner_id>')
def click_banner(banner_id):
    from bson.objectid import ObjectId
    banner = Banner.get_by_id(banner_id)
    if not banner:
        return redirect(url_for('main.index'))
    
    link_type = banner.get('link_type')
    link_value = banner.get('link_value')
    
    if link_type == 'category':
        return redirect(url_for('main.products', category=link_value))
    elif link_type == 'brand':
        return redirect(url_for('main.products', brand=link_value))
    elif link_type == 'custom_products':
        # we can use the search query parameter for multiple products by passing link_value as a search query
        return redirect(url_for('main.products', q=link_value))
    else:
        # all_offers
        return redirect(url_for('main.products', on_offer='1'))
