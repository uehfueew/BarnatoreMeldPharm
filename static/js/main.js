document.addEventListener('DOMContentLoaded', () => {
    // Mobile Menu Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    const menuBackdrop = document.querySelector('.menu-backdrop');
    const menuCloseBtn = document.querySelector('.menu-close-btn');

    const closeMenu = () => {
        menuToggle.classList.remove('active');
        navLinks.classList.remove('active');
        if (menuBackdrop) menuBackdrop.classList.remove('active');
        document.body.style.overflow = '';
    };

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            menuToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
            if (menuBackdrop) menuBackdrop.classList.toggle('active');
            document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : '';
        });

        // Close when clicking backdrop
        if (menuBackdrop) {
            menuBackdrop.addEventListener('click', closeMenu);
        }

        // Close when clicking 'X' button
        if (menuCloseBtn) {
            menuCloseBtn.addEventListener('click', closeMenu);
        }

        // Close menu when clicking links
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });
    }

    // 1. Sticky Navbar Effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // 3. Product Search Filter (Front-end only for demo/smoothness)
    const searchInput = document.getElementById('productSearch');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            filterProducts(term, getActiveCategory());
        });
    }

    if (filterBtns) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class from all
                filterBtns.forEach(b => b.classList.remove('active'));
                // Add to clicked
                btn.classList.add('active');
                
                const category = btn.getAttribute('data-filter');
                filterProducts(searchInput ? searchInput.value.toLowerCase() : '', category);
            });
        });
    }

    function getActiveCategory() {
        const activeBtn = document.querySelector('.filter-btn.active');
        return activeBtn ? activeBtn.getAttribute('data-filter') : 'all';
    }

    function filterProducts(searchTerm, category) {
        productCards.forEach(card => {
            const name = card.querySelector('h3').textContent.toLowerCase();
            const cardCategory = card.getAttribute('data-category'); // Needs to be added to HTML
            
            const matchesSearch = name.includes(searchTerm);
            const matchesCategory = category === 'all' || cardCategory === category;

            if (matchesSearch && matchesCategory) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
                card.classList.remove('is-visible');
            }
        });
    }

    // 4. Toast Notification System
    window.showToast = function(message, type = 'success') {
        const container = document.getElementById('toast-container');
        if (!container) return; // Should be in base.html

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        container.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };

    // 5. Add to Cart Buttons logic removed to prevent double toasts (handled by AJAX form submit below)

    // 6. Favorite Button Logic
    window.toggleFavorite = async function(btn, productId) {
        if (!productId) return;
        
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        try {
            const response = await fetch(`/product/favorite/${productId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                const icon = btn.querySelector('i');
                if (data.action === 'added') {
                    btn.classList.add('active');
                    if (icon) {
                        icon.classList.remove('far'); // Outline
                        icon.classList.add('fas');    // Solid
                    }
                    showToast('Produkti u shtua në të preferuarat!', 'success');
                } else {
                    btn.classList.remove('active');
                    if (icon) {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                    }
                    showToast('Produkti u largua nga të preferuarat', 'info');
                }
                
                // Reload to update the list of users who liked it (optional, but requested to show "who")
                // if (window.location.pathname.includes('/product/')) {
                //    setTimeout(() => window.location.reload(), 1000);
                // }
            } else {
                showToast('Duhet të jeni të kyçur për të ruajtur produktet.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast('Ndodhi një gabim.', 'error');
        }
    }
});

// Quantity Selector Logic
document.addEventListener('DOMContentLoaded', () => {
    const qtyInputs = document.querySelectorAll('.quantity-selector');
    
    qtyInputs.forEach(selector => {
        const input = selector.querySelector('.qty-input');
        const minusBtn = selector.querySelector('.minus');
        const plusBtn = selector.querySelector('.plus');
        
        minusBtn.addEventListener('click', () => {
            let val = parseInt(input.value);
            if (val > 1) {
                input.value = val - 1;
            }
        });
        
        plusBtn.addEventListener('click', () => {
            let val = parseInt(input.value);
            input.value = val + 1;
        });
    });
});

// AJAX Cart Actions & Confirmations
document.addEventListener('DOMContentLoaded', () => {
    
    // Helper to update cart badge
    const updateCartBadge = (count) => {
        const badge = document.querySelector('.cart-badge');
        if (badge) {
            badge.textContent = count;
            if (count > 0) badge.style.display = 'flex';
            else badge.style.display = 'none';
        } else if (count > 0) {
            const icon = document.querySelector('.cart-icon');
            if (icon) {
                const newBadge = document.createElement('span');
                newBadge.className = 'cart-badge';
                newBadge.textContent = count;
                icon.appendChild(newBadge);
            }
        }
    };

    // Generic form submit handler for Add to Cart forms
    document.body.addEventListener('submit', async (e) => {
        // Handle Checkout Form
        if (e.target.id === 'checkout-form') {
            e.preventDefault();
            const result = await Swal.fire({
                title: 'Konfirmo Porosinë',
                text: "A jeni të sigurt që të dhënat janë të sakta?",
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Po, Dërgo',
                cancelButtonText: 'Anulo',
                confirmButtonColor: '#10b981'
            });
            if (result.isConfirmed) e.target.submit();
            return;
        }

        const isAdd = e.target.matches('form[action*="/cart/add/"]');
        const isUpdate = e.target.matches('form[action*="/cart/update/"]');
        const isRemove = e.target.matches('form[action*="/cart/remove/"]');
        
        if (!isAdd && !isUpdate && !isRemove) return;
        
        e.preventDefault();
        const form = e.target;

        // Confirmation for remove
        if (isRemove) {
            const result = await Swal.fire({
                title: 'A jeni i sigurt?',
                text: "Dëshironi ta largoni këtë produkt nga shporta?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#ef4444',
                cancelButtonColor: '#3b82f6',
                confirmButtonText: 'Po, largoje!',
                cancelButtonText: 'Anulo'
            });
            if (!result.isConfirmed) return;
        }

        // Setup UI for loading
        let btn = form.querySelector('button[type="submit"]');
        let originalContent = btn ? btn.innerHTML : '';
        if (btn && isAdd) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (isAdd) {
                    showToast(data.message, 'success');
                    updateCartBadge(data.cart_count);
                } else if (isRemove && data.removed) {
                    const row = form.closest('tr');
                    row.style.opacity = '0';
                    setTimeout(() => {
                        row.remove();
                        if (document.querySelectorAll('tbody tr').length === 0) {
                            location.reload(); 
                        }
                    }, 300);
                    showToast(data.message, 'info');
                    // Update totals
                    const totalEl = document.querySelector('.cart-summary h3');
                    if (totalEl) totalEl.textContent = 'Totali: €' + data.total_price.toFixed(2);
                    updateCartBadge(data.cart_count);

                } else if (isUpdate) {
                     // Update quantity input and item total
                    const row = form.closest('tr');
                    if (row) {
                        const qtyInput = row.querySelector('.qty-input');
                        if (qtyInput) qtyInput.value = data.quantity;
                        
                        const itemTotal = row.querySelector('td:nth-child(4)'); // 4th column is subtotal
                        if (itemTotal) itemTotal.textContent = '€' + data.item_total.toFixed(2);
                        
                        const minusBtn = row.querySelector('.minus');
                        if (minusBtn) minusBtn.disabled = data.quantity <= 1;
                    }
                    // Update global totals
                    const totalEl = document.querySelector('.cart-summary h3');
                    if (totalEl) totalEl.textContent = 'Totali: €' + data.total_price.toFixed(2);
                    updateCartBadge(data.cart_count);
                }
            } else {
                // Handle error (e.g., login required)
                if (response.status === 401 || !data.success) {
                    Swal.fire({
                        title: 'Kërkohet Kyçja!',
                        text: data.message || 'Ju duhet të kyçeni për ta kryer këtë veprim.',
                        icon: 'info',
                        showCancelButton: true,
                        confirmButtonText: 'Kyçu',
                        cancelButtonText: 'Anulo',
                        confirmButtonColor: '#059669'
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.href = '/login';
                        }
                    });
                } else {
                     showToast(data.message || 'Ndodhi një gabim.', 'danger');
                }
            }
        } catch (error) {
            console.error('Error:', error);
            if (!isRemove) showToast('Ndodhi një gabim.', 'danger');
        } finally {
            if (btn && isAdd) {
                btn.disabled = false;
                btn.innerHTML = originalContent;
            }
        }
    });

    // Handle Link Confirmations (Logout, Clear Cart)
    document.body.addEventListener('click', async (e) => {
        const trigger = e.target.closest('[data-confirm]');
        if (!trigger) return;

        e.preventDefault();
        const message = trigger.dataset.confirm || "A jeni i sigurt?";
        const href = trigger.getAttribute('href');

        const result = await Swal.fire({
            title: 'Konfirmim',
            text: message,
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Po',
            cancelButtonText: 'Jo'
        });

        if (result.isConfirmed) {
            window.location.href = href;
        }
    });

    // 6. Checkout Login Check
    const checkoutBtn = document.querySelector('.checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', (e) => {
            const isLoggedIn = document.body.dataset.userLoggedIn === 'true';
            
            if (!isLoggedIn) {
                e.preventDefault();
                Swal.fire({
                    title: 'Kërkohet Hyrja',
                    text: 'Ju lutemi kyçuni ose regjistrohuni për të vazhduar me pagesën.',
                    icon: 'info',
                    showCancelButton: true,
                    showDenyButton: true,
                    confirmButtonText: 'Kyçu',
                    denyButtonText: 'Regjistrohu',
                    cancelButtonText: 'Anulo',
                    confirmButtonColor: 'var(--primary)',
                    denyButtonColor: 'var(--primary-dark)',
                    reverseButtons: true
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
                    } else if (result.isDenied) {
                        window.location.href = '/register';
                    }
                });
            }
        });
    }

});

// Make entire product card clickable
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.product-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', (e) => {
            // Do nothing if clicked on button, link, or form
            if (e.target.closest('button') || e.target.closest('a') || e.target.closest('form')) {
                return;
            }
            
            // Find the detail link
            const detailLink = card.querySelector('a[href*="/product/"]');
            if (detailLink) {
                window.location.href = detailLink.href;
            }
        });
    });

    // Initialize Swipe for Carousels
    initCarouselSwipe();
});

function initCarouselSwipe() {
    const containers = document.querySelectorAll('.carousel-container');
    
    containers.forEach(container => {
        let touchstartX = 0;
        let touchendX = 0;
        let touchstartY = 0;
        let touchendY = 0;
        
        container.addEventListener('touchstart', e => {
            touchstartX = e.changedTouches[0].clientX;
            touchstartY = e.changedTouches[0].clientY;
        }, {passive: true});

        container.addEventListener('touchend', e => {
            touchendX = e.changedTouches[0].clientX;
            touchendY = e.changedTouches[0].clientY;
            handleGesture();
        }, {passive: true});

        function handleGesture() {
            const deltaX = touchendX - touchstartX;
            const deltaY = touchendY - touchstartY;
            
            // Reduced threshold to 30px for easier swiping on small cards
            // Only trigger if horizontal movement is clearly dominant
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 30) {
                if (deltaX < -30) {
                    // Swiped Left -> Move Next
                    moveCarousel(null, container, 1);
                } else if (deltaX > 30) {
                    // Swiped Right -> Move Prev
                    moveCarousel(null, container, -1);
                }
            }
        }
    });
}

function moveCarousel(event, btnOrTrack, direction) {
    if (event && event.preventDefault) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Find container from button OR from track (if swipe)
    const container = btnOrTrack.closest('.carousel-container');
    const track = container.querySelector('.carousel-track');
    const images = track.querySelectorAll('img');
    
    let currentIndex = parseInt(container.getAttribute('data-index') || '0');
    currentIndex += direction;
    
    if (currentIndex < 0) currentIndex = images.length - 1;
    if (currentIndex >= images.length) currentIndex = 0;
    
    goToSlide(container, currentIndex);
}

function goToSlide(container, index) {
    const track = container.querySelector('.carousel-track');
    const dots = container.querySelectorAll('.indicator-dot');
    const thumbs = container.parentElement.querySelectorAll('.thumbnail');
    
    container.setAttribute('data-index', index);
    track.style.transform = `translateX(-${index * 100}%)`;
    
    // Update indicators
    if (dots) {
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
    }

    // Update thumbnails if they exist
    if (thumbs) {
        thumbs.forEach((thumb, i) => {
            thumb.style.borderColor = i === index ? 'var(--primary)' : 'transparent';
            thumb.style.opacity = i === index ? '1' : '0.7';
        });
    }
}
