from flask import Blueprint, render_template, session, redirect, url_for
from models.product import Product
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

@main.route('/products')
def products():
    # Ensure user is allowed to see this page
    if not (current_user.is_authenticated or session.get('guest_mode')):
         return redirect(url_for('main.index'))
         
    products = Product.get_all()
    # Debug print
    print(f"Products found: {len(products)}")
    return render_template('products.html', products=products)

@main.route('/product/<product_id>')
def product_detail(product_id):
    if not (current_user.is_authenticated or session.get('guest_mode')):
         return redirect(url_for('main.index'))

    product = Product.get_by_id(product_id)
    if not product:
        return render_template('index.html') # Should be 404
    
    related_products = Product.get_related(product.get('category'), product.get('_id'))
    return render_template('product_detail.html', product=product, related_products=related_products)

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
