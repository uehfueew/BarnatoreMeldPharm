from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.product import Product
from models.order import Order
from functools import wraps

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
    products = Product.get_all()
    return render_template('admin/dashboard.html', products=products)

@admin.route('/product/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    if request.method == 'POST':
        product_data = {
            "name": request.form.get('name'),
            "category": request.form.get('category'),
            "price": float(request.form.get('price')),
            "discount_price": float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
            "description": request.form.get('description'),
            "image_url": request.form.get('image_url'),
            "featured": request.form.get('featured') == 'on'
        }
        Product.create(product_data)
        flash('Produkti u krijua me sukses!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/product_form.html', product=None)

@admin.route('/product/edit/<product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.get_by_id(product_id)
    if not product:
        flash('Produkti nuk ekziston.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        product_data = {
            "name": request.form.get('name'),
            "category": request.form.get('category'),
            "price": float(request.form.get('price')),
            "discount_price": float(request.form.get('discount_price')) if request.form.get('discount_price') else None,
            "description": request.form.get('description'),
            "image_url": request.form.get('image_url'),
            "featured": request.form.get('featured') == 'on'
        }
        Product.update(product_id, product_data)
        flash('Produkti u përditësua me sukses!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/product_form.html', product=product)

@admin.route('/product/delete/<product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    Product.delete(product_id)
    flash('Produkti u fshi.', 'success')
    return redirect(url_for('admin.dashboard'))
