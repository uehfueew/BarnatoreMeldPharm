import os

path = '/Users/drenbuqa/Library/CloudStorage/OneDrive-Personal/MeldPharm/BarnatoreMeldPharm-1/static/js/main.js'
with open(path, 'r') as f:
    lines = f.readlines()

# Target range for updateGlobalBadges (roughly 1167-1215)
# We'll search for the function start
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'window.updateGlobalBadges = function (data) {' in line:
        start_idx = i
        # Find the matching closing brace (very simplistic but should work for this file)
        # We know it ends with }; and a newline or end of block
        for j in range(i, len(lines)):
            if lines[j].strip() == '};' and (j == len(lines)-1 or lines[j+1].strip() == ''):
                end_idx = j
                break
        break

if start_idx != -1 and end_idx != -1:
    new_func = """window.updateGlobalBadges = function (data) {
    if (!data) return;

    // 1. Update Cart Badges
    const cartCount = data.cart_count !== undefined ? data.cart_count : (data.count !== undefined ? data.count : null);
    
    if (cartCount !== null) {
        const cartBadges = document.querySelectorAll(
            '.cart-badge, .mobile-cart-badge, .cart-count-badge, .items-count-badge-mobile, ' +
            '.cart-count, .shopping-cart-count, .total-cart-items, .badge-cart-count'
        );
        
        cartBadges.forEach(badge => {
            if (badge.classList.contains('items-count-badge-mobile')) {
                badge.textContent = `${cartCount} produkt(e)`;
            } else {
                badge.textContent = cartCount;
            }
            
            if (cartCount > 0) {
                badge.classList.remove('d-none');
                badge.style.display = 'flex';
            } else {
                badge.classList.add('d-none');
                badge.style.display = 'none';
            }
        });
        
        const countTexts = document.querySelectorAll('.items-count-text, .total-items-count, .cart-total-items-text');
        countTexts.forEach(el => {
            el.textContent = `${cartCount} produkt(e)`;
        });

        // Update Page Title with Cart Count
        const currentTitle = document.title.replace(/^\(\d+\)\s*/, '');
        if (cartCount > 0) {
            document.title = `(${cartCount}) ${currentTitle}`;
        } else {
            document.title = currentTitle;
        }
    }

    // 2. Update Wishlist Badges
    const wishCount = data.wishlist_count !== undefined ? data.wishlist_count : (data.count !== undefined && data.wishlist_count === undefined ? data.count : null);
    
    if (wishCount !== null) {
        const wishBadges = document.querySelectorAll('.wishlist-count, .cart-badge-wish, .mobile-wishlist-count');
        wishBadges.forEach(badge => {
            badge.textContent = wishCount;
            if (wishCount > 0) {
                badge.classList.remove('d-none');
                badge.style.display = 'flex';
            } else {
                badge.classList.add('d-none');
                badge.style.display = 'none';
            }
        });
    }

    // 3. Update Mini Cart Footer Total
    if (data.total_price !== undefined || data.cart_total !== undefined) {
        const total = data.total_price !== undefined ? data.total_price : data.cart_total;
        const footerBtn = document.querySelector('.btn-go-to-cart');
        if (footerBtn) {
            footerBtn.innerHTML = `SHKO NË SHPORTË (${parseFloat(total).toFixed(2)} €)`;
        }
    }
};
"""
    lines[start_idx:end_idx+1] = [new_func + '\n']
    
    with open(path, 'w') as f:
        f.writelines(lines)
    print(f"Successfully updated updateGlobalBadges in main.js (lines {start_idx+1}-{end_idx+1})")
else:
    print(f"Could not find updateGlobalBadges function. Start: {start_idx}, End: {end_idx}")
