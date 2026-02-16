from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.product import Product
from models.order import Order
from models.categories import CATEGORIES
from functools import wraps
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Ju nuk keni akses në këtë faqe.", "danger")
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.get_all()
    return render_template('admin/orders.html', orders=orders)

@admin.route('/order/update_status/<order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    new_status = request.form.get('status')
    if new_status:
        Order.update_status(order_id, new_status)
        flash(f'Statusi i porosisë u ndryshua në {new_status}.', 'success')
    return redirect(url_for('admin.orders'))

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Automatically revert expired offers
    Product.revert_expired_offers()
    
    filter_on_offer = request.args.get('on_offer') == '1'
    all_products = Product.get_all()
    
    if filter_on_offer:
        products = [p for p in all_products if p.get('discount_price')]
    else:
        products = all_products

    # --- Analytics: Sales at a Glance ---
    orders = Order.get_all()
    
    def safe_float(val):
        try:
            return float(val or 0)
        except (ValueError, TypeError):
            return 0.0

    analytics = {
        'total_products': len(all_products),
        'total_offers': len([p for p in all_products if p.get('discount_price')]),
        'category_sales': {},
        'brand_distribution': {},
        'most_ordered': [],
        'out_of_stock': [p for p in all_products if not p.get('in_stock')][:5],
        'most_liked': []
    }

    # Helper for normalization
    brand_counts = {}
    category_counts = {}
    for p in all_products:
        # Category normalization
        raw_cat = str(p.get('category') or 'Tjera').strip()
        cat_key = raw_cat.title()
        category_counts[cat_key] = category_counts.get(cat_key, 0) + 1
        
        # Brand normalization
        raw_brand = str(p.get('brand') or 'Pa Brand').strip()
        brand_key = raw_brand.title()
        brand_counts[brand_key] = brand_counts.get(brand_key, 0) + 1

    analytics['brand_distribution'] = dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:6])
    analytics['category_sales'] = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:6])

    # Dynamic metrics
    # 1. Most liked (top 5) - based on length of favorites list
    analytics['most_liked'] = sorted(all_products, key=lambda x: len(x.get('favorites', [])), reverse=True)[:5]
    
    # 2. Most ordered (top 5 from actual orders)
    product_order_counts = {}
    for o in orders:
        items = o.get('items', [])
        if not isinstance(items, list): continue
        for item in items:
            if not isinstance(item, dict): continue
            try:
                pid = str(item.get('product_id') or item.get('_id') or 'unknown')
                product_order_counts[pid] = product_order_counts.get(pid, 0) + int(item.get('quantity', 1))
            except (ValueError, TypeError):
                continue
    
    # Map IDs back to product names
    product_map = {str(p['_id']): p for p in all_products}
    sorted_order_ids = sorted(product_order_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for pid, count in sorted_order_ids:
        if pid in product_map:
            p_info = product_map[pid].copy()
            p_info['order_count'] = count
            analytics['most_ordered'].append(p_info)
        
    return render_template('admin/dashboard.html', 
                           products=products, 
                           filter_on_offer=filter_on_offer,
                           analytics=analytics)

@admin.route('/product/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    if request.method == 'POST':
        # Process images
        main_img = request.form.get('image_url')
        additional_str = request.form.get('additional_images', '')
        images = [main_img]
        if additional_str:
            extras = [x.strip() for x in additional_str.replace(',', '\n').split('\n') if x.strip()]
            for img in extras:
                if img != main_img:
                    images.append(img)

        product_data = {
            "name": request.form.get('name'),
            "brand": request.form.get('brand'),
            "category": request.form.get('category'),
            "subcategory": request.form.get('subcategory'),
            "size": request.form.get('size'),
            "price": float(request.form.get('price')),
            "discount_price": float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
            "discount_until": datetime.strptime(request.form.get('discount_until'), '%Y-%m-%d') if request.form.get('discount_until') else None,
            "description": request.form.get('description'),
            "image_url": main_img,
            "images": images,
            "featured": request.form.get('featured') == 'on',
            "is_best_seller": request.form.get('is_best_seller') == 'on',
            "is_pharmacist_choice": request.form.get('is_pharmacist_choice') == 'on',
            "in_stock": request.form.get('in_stock') == 'on',
            "how_to_use": request.form.get('how_to_use'),
            "key_ingredients": request.form.get('key_ingredients')
        }
        Product.create(product_data)
        flash('Produkti u krijua me sukses!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/product_form.html', product=None, categories=CATEGORIES)

@admin.route('/product/edit/<product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('Produkti nuk ekziston.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        # Process images
        main_img = request.form.get('image_url')
        additional_str = request.form.get('additional_images', '')
        images = [main_img]
        if additional_str:
            extras = [x.strip() for x in additional_str.replace(',', '\n').split('\n') if x.strip()]
            for img in extras:
                if img != main_img:
                    images.append(img)

        product_data = {
            "name": request.form.get('name'),
            "brand": request.form.get('brand'),
            "category": request.form.get('category'),
            "subcategory": request.form.get('subcategory'),
            "size": request.form.get('size'),
            "price": float(request.form.get('price')),
            "discount_price": float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
            "discount_until": datetime.strptime(request.form.get('discount_until'), '%Y-%m-%d') if request.form.get('discount_until') else None,
            "description": request.form.get('description'),
            "image_url": main_img,
            "images": images,
            "featured": request.form.get('featured') == 'on',
            "is_best_seller": request.form.get('is_best_seller') == 'on',
            "is_pharmacist_choice": request.form.get('is_pharmacist_choice') == 'on',
            "in_stock": request.form.get('in_stock') == 'on',
            "how_to_use": request.form.get('how_to_use'),
            "key_ingredients": request.form.get('key_ingredients')
        }
        Product.update(product_id, product_data)
        flash('Produkti u përditësua me sukses!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/product_form.html', product=product, categories=CATEGORIES)

@admin.route('/product/delete/<product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    Product.delete(product_id)
    flash('Produkti u fshi.', 'success')
    return redirect(url_for('admin.dashboard'))
@admin.route('/bulk-offers', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_offers():
    from models.db import mongo
    from bson import ObjectId
    
    if request.method == 'POST':
        try:
            action = request.form.get('action', 'apply')
            discount_percent = float(request.form.get('discount_percent', 0)) if action == 'apply' else 0
            discount_until = request.form.get('discount_until')
            selected_ids = request.form.getlist('selected_products')
            
            # If specific products are selected, use them. Otherwise use filters.
            if selected_ids:
                query = {"_id": {"$in": [ObjectId(pid) for pid in selected_ids]}}
            else:
                target_brand = request.form.get('brand')
                target_category = request.form.get('category')
                target_subcategory = request.form.get('subcategory')
                
                query = {"is_deleted": {"$ne": True}}
                if target_brand and target_brand != 'all':
                    query["brand"] = target_brand
                if target_category and target_category != 'all':
                    query["category"] = target_category
                if target_subcategory and target_subcategory != 'all':
                    query["subcategory"] = target_subcategory
                
            products = list(mongo.db.products.find(query))
            count = 0
            expiry_date = datetime.strptime(discount_until, '%Y-%m-%d') if discount_until else None
            
            for p in products:
                if action == 'apply':
                    price = float(p.get('price', 0))
                    if price > 0:
                        discount_price = price * (1 - (discount_percent / 100))
                        update_data = {
                            "discount_price": round(discount_price, 2),
                            "discount_until": expiry_date,
                            "updated_at": datetime.now()
                        }
                        mongo.db.products.update_one({"_id": p["_id"]}, {"$set": update_data})
                        count += 1
                else: # remove action
                    mongo.db.products.update_one(
                        {"_id": p["_id"]}, 
                        {"$set": {"discount_price": None, "discount_until": None, "updated_at": datetime.now()}}
                    )
                    count += 1
            
            msg = f'Sukses! Oferta u aplikua për {count} produkte.' if action == 'apply' else f'Sukses! Ofertat u hoqën nga {count} produkte.'
            flash(msg, 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Gabim gjatë aplikimit të ofertës: {str(e)}', 'danger')
            return redirect(url_for('admin.bulk_offers'))
        
    all_products = Product.get_all()
    brands = sorted(list(set(p.get('brand') for p in all_products if p.get('brand'))))
    return render_template('admin/bulk_offers.html', 
                         all_products=all_products,
                         brands=brands, 
                         categories=CATEGORIES)
