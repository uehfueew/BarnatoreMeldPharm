from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models.product import Product

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

def calculate_cart_totals(cart):
    total_price = 0
    total_items = 0
    for product_id, quantity in cart.items():
        product = Product.get_by_id(product_id)
        if product:
            price = product.get('discount_price') if product.get('discount_price') else product.get('price')
            total_price += price * int(quantity)
            total_items += int(quantity)
    return total_price, total_items

@cart_bp.route('/')
def view_cart():
    # session['cart'] structure: {'product_id': quantity, ...}
    cart = session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        product = Product.get_by_id(product_id)
        if product:
            price = product.get('discount_price') if product.get('discount_price') else product.get('price')
            item_total = price * int(quantity)
            total_price += item_total
            product['quantity'] = quantity
            product['item_total'] = item_total
            cart_items.append(product)
            
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@cart_bp.route('/add/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    quantity = int(request.form.get('quantity', 1))
    
    if product_id in cart:
        cart[product_id] = int(cart[product_id]) + quantity
    else:
        cart[product_id] = quantity
        
    session['cart'] = cart
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_price, total_items = calculate_cart_totals(cart)
        return jsonify({
            'success': True,
            'message': 'Produkti u shtua në shportë.',
            'cart_count': total_items
        })
        
    flash('Produkti u shtua në shportë në mënyrë të sigurt.', 'success')
    return redirect(request.referrer or url_for('cart.view_cart'))

@cart_bp.route('/update/<product_id>/<action>', methods=['POST'])
def update_quantity(product_id, action):
    cart = session.get('cart', {})
    
    if product_id in cart:
        current_qty = int(cart[product_id])
        
        if action == 'increase':
            cart[product_id] = current_qty + 1
        elif action == 'decrease':
            if current_qty > 1:
                cart[product_id] = current_qty - 1
        
        session['cart'] = cart
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_price, total_items = calculate_cart_totals(cart)
        # Get specific item total
        product = Product.get_by_id(product_id)
        item_total = 0
        if product:
            price = product.get('discount_price') if product.get('discount_price') else product.get('price')
            item_total = price * cart[product_id]
            
        return jsonify({
            'success': True,
            'total_price': total_price,
            'cart_count': total_items,
            'item_total': item_total,
            'quantity': cart[product_id]
        })

    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            total_price, total_items = calculate_cart_totals(cart)
            return jsonify({
                'success': True,
                'message': 'Produkti u largua nga shporta.',
                'total_price': total_price,
                'cart_count': total_items,
                'removed': True
            })
            
        flash('Produkti u largua nga shporta.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/clear')
def clear_cart():
    session.pop('cart', None)
    flash('Shporta u pastrua.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout')
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Shporta juaj është e zbrazët.', 'warning')
        return redirect(url_for('main.products'))
        
    cart_items = []
    total_price = 0
    
    for product_id, quantity in cart.items():
        product = Product.get_by_id(product_id)
        if product:
            price = product.get('discount_price') if product.get('discount_price') else product.get('price')
            item_total = price * int(quantity)
            total_price += item_total
            product['quantity'] = quantity
            product['item_total'] = item_total
            cart_items.append(product)
            
    shipping_cost = 0 if total_price >= 50 else 3.00
    grand_total = total_price + shipping_cost
    
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, shipping_cost=shipping_cost, grand_total=grand_total)

@cart_bp.route('/place_order', methods=['POST'])
def place_order():
    # Here you would normally save the order to the database
    # For now, we will simulate it
    
    method = request.form.get('payment_method')
    fullname = request.form.get('fullname')
    
    if method == 'card':
        flash('Pagesat me kartë nuk janë ende aktive.', 'warning')
        return redirect(url_for('cart.checkout'))
        
    # Process Cash on Delivery
    session.pop('cart', None)
    flash(f'Faleminderit {fullname}, porosia u realizua me sukses!', 'success')
    return redirect(url_for('main.index'))
