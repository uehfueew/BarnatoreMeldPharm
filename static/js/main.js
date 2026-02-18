// --- GLOBAL HELPERS ---
window.updateResultsCount = function(count) {
    const countEl = document.getElementById('current-count');
    if (countEl) countEl.textContent = count;
};

window.createProductCardHtml = function(p) {
    const discountPercentage = p.discount_price ? Math.round(((p.price - p.discount_price) / p.price) * 100) : 0;
    const isFav = p.is_favorite ? 'active' : '';
    const heartIconClass = p.is_favorite ? 'fas' : 'far';
    return `
        <div class="product-card fade-in-section" data-id="${p.id}" data-category="${p.category}" data-name="${p.name}">
            <div class="product-image">
                ${p.discount_price ? `<div class="special-offer-badge red-badge">Oferta Speciale</div>` : ''}
                ${p.is_best_seller ? `<div class="best-seller-badge">Më i Shituri</div>` : ''}
                <img src="${p.image_url}" alt="${p.name}">
                <button class="btn-favorite ${isFav}" onclick="toggleFavorite(this, '${p.id}')">
                    <i class="${heartIconClass} fa-heart"></i>
                </button>
                <a href="/product/${p.id}" class="product-card-link-overlay"></a>
            </div>
            <div class="product-info">
                <span class="product-category" style="color: var(--primary); font-weight: 700;">${p.brand || p.category}</span>
                <h3 class="product-title">${p.name}</h3>
                ${p.size ? `<span class="product-size">${p.size}</span>` : ''}
                <div class="price-container">
                    ${p.discount_price ? `
                        <span class="price discounted">€${p.discount_price}</span>
                        <span class="price original">€${p.price}</span>
                        <span class="discount-badge">-${discountPercentage}%</span>
                    ` : `<span class="price">€${p.price}</span>`}
                </div>
            </div>
        </div>
    `;
};

window.renderProducts = function(products, grid) {
    if (!grid) return;
    grid.innerHTML = products.map(p => window.createProductCardHtml(p)).join('');
    
    // Trigger visibility for fade-in animations
    const cards = grid.querySelectorAll('.product-card');
    if (cards.length > 0) {
        setTimeout(() => {
            cards.forEach(card => card.classList.add('visible'));
        }, 50);
    }
};

window.appendProducts = function(products, grid) {
    if (!grid) return;
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = products.map(p => window.createProductCardHtml(p)).join('');
    
    while (tempDiv.firstChild) {
        const child = tempDiv.firstChild;
        grid.appendChild(child);
        // Trigger visibility if intersection observer is not used for These new items
        setTimeout(() => child.classList.add('visible'), 50);
    }
};

window.loadMoreHome = function() {
    const btn = document.getElementById('load-more-btn');
    const grid = document.getElementById('recommended-grid');
    if (!btn || !grid) return;
    
    // Set all=true to load everything
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = 'Duke u ngarkuar... <i class="fas fa-spinner fa-spin ml-2"></i>';

    const category = btn.getAttribute('data-category') || 'all';
    let url = `/products?ajax=1&all=true`;
    if (category !== 'all') {
        url += `&category=${encodeURIComponent(category)}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.products && data.products.length > 0) {
                // Clear and re-render to avoid duplicates if some are already there
                // or just append only the new ones. 
                // But the user said "show all", so replacing is safer if we want to ensure we don't have first 20 twice
                grid.innerHTML = ''; 
                window.appendProducts(data.products, grid);
                btn.parentElement.classList.add('d-none');
            } else {
                btn.parentElement.classList.add('d-none');
            }
        })
        .catch(err => console.error('Error loading more home:', err))
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
        });
};

// --- GLOBAL UI HANDLERS (Available immediately) ---
window.openShopSidebar = function() {
    const sidebar = document.getElementById('shopSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const mobileHeader = document.querySelector('.mobile-header');
    const mobileBottomNav = document.querySelector('.mobile-bottom-nav');

    if (sidebar) sidebar.classList.add('active');
    if (overlay) overlay.classList.add('active');
    
    // Disable scrolling but don't hide menus yet to avoid jitter
    document.body.classList.add('sidebar-open');
};

window.closeShopSidebar = function() {
    const sidebar = document.getElementById('shopSidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (sidebar) sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    
    document.body.classList.remove('sidebar-open');
};

// Toggle Filter Sections (Collapsible)
window.toggleFilterSection = function(btn) {
    const parent = btn.closest('.collapsible-sidebar-block');
    const icon = btn.querySelector('i');
    
    if (parent.classList.contains('active')) {
        parent.classList.remove('active');
        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
    } else {
        parent.classList.add('active');
        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
    }
};

window.toggleSubcats = function(event, btn) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const group = btn.closest('.sidebar-cat-group');
    const list = group.querySelector('.sidebar-subcat-list');
    const icon = btn.querySelector('.toggle-icon');
    
    if (list) {
        list.classList.toggle('show');
    }
    if (icon) {
        icon.classList.toggle('rotated');
    }
};

window.resetFilters = function(e) {
    if (e) e.preventDefault();
    
    // Clear inputs
    const minPrice = document.getElementById('min-price');
    const maxPrice = document.getElementById('max-price');
    if (minPrice) minPrice.value = '';
    if (maxPrice) maxPrice.value = '';
    
    const discountOnly = document.getElementById('discount-only-filter');
    if (discountOnly) discountOnly.checked = false;
    
    const bestSellers = document.getElementById('best-seller-filter');
    if (bestSellers) bestSellers.checked = false;

    const productSearch = document.getElementById('productSearch') || document.getElementById('productSearchMobile');
    if (productSearch) productSearch.value = '';

    // Reset URL and call update
    const url = new URL(window.location.href);
    url.search = '';
    window.history.pushState({}, '', url.pathname);
    
    // Update UI active states
    document.querySelectorAll('.sidebar-cat-link, .sidebar-subcat-link, .brand-link-item').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.sidebar-cat-link[onclick*="\'all\'"], .brand-link-item[onclick*="\'all\'"]').forEach(el => el.classList.add('active'));
    
    window.updateShop();
};

window.filterByCategory = function(e, cat) {
    if (e) e.preventDefault();
    const urlParams = new URLSearchParams(window.location.search);
    if (cat === 'all') {
        urlParams.delete('category');
    } else {
        urlParams.set('category', cat);
    }
    urlParams.delete('subcategory');
    urlParams.delete('page');
    
    window.history.pushState({}, '', `${window.location.pathname}?${urlParams.toString()}`);
    
    // Update active classes
    document.querySelectorAll('.sidebar-cat-link').forEach(link => {
        const onclick = link.getAttribute('onclick');
        if (onclick) {
            link.classList.toggle('active', onclick.includes(`'${cat}'`));
        }
    });
    document.querySelectorAll('.sidebar-subcat-list').forEach(list => {
        list.classList.remove('show');
    });
    document.querySelectorAll('.toggle-icon').forEach(ico => {
        ico.classList.remove('rotated');
    });
    
    const activeLink = document.querySelector(`.sidebar-cat-link.active`);
    if (activeLink) {
        const activeGroup = activeLink.closest('.sidebar-cat-group');
        if (activeGroup) {
            const activeList = activeGroup.querySelector('.sidebar-subcat-list');
            const activeIcon = activeGroup.querySelector('.toggle-icon');
            if (activeList) activeList.classList.add('show');
            if (activeIcon) activeIcon.classList.add('rotated');
        }
    }

    document.querySelectorAll('.sidebar-subcat-link').forEach(link => link.classList.remove('active'));
    
    window.updateShop();
};

window.filterBySubcategory = function(e, cat, sub) {
    if (e) e.preventDefault();
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('category', cat);
    urlParams.set('subcategory', sub);
    urlParams.delete('page');
    
    window.history.pushState({}, '', `${window.location.pathname}?${urlParams.toString()}`);
    
    // Update active classes
    document.querySelectorAll('.sidebar-cat-link').forEach(link => {
        const onclick = link.getAttribute('onclick');
        if (onclick) {
            link.classList.toggle('active', onclick.includes(`'${cat}'`));
        }
    });
    document.querySelectorAll('.sidebar-subcat-link').forEach(link => {
        const onclick = link.getAttribute('onclick');
        if (onclick) {
            link.classList.toggle('active', onclick.includes(`'${sub}'`));
        }
    });
    
    window.updateShop();
};

window.filterByBrand = function(e, brand) {
    if (e) e.preventDefault();
    const urlParams = new URLSearchParams(window.location.search);
    if (brand === 'all') {
        urlParams.delete('brand');
    } else {
        urlParams.set('brand', brand);
    }
    urlParams.delete('page');
    
    window.history.pushState({}, '', `${window.location.pathname}?${urlParams.toString()}`);
    
    // Update active classes
    document.querySelectorAll('.brand-link-item').forEach(link => {
        const onclick = link.getAttribute('onclick');
        if (onclick) {
            link.classList.toggle('active', onclick.includes(`'${brand}'`));
        }
    });
    
    window.updateShop();
};

window.toggleSortMenu = function(e) {
    if (e) {
        if (typeof e.preventDefault === 'function') e.preventDefault();
        if (typeof e.stopPropagation === 'function') e.stopPropagation();
    }
    const sortMenu = document.getElementById('sortMenu');
    const sortTrigger = document.getElementById('sortTrigger');
    if (sortMenu && sortTrigger) {
        const isVisible = sortMenu.style.display === 'block' || sortMenu.classList.contains('show');
        if (isVisible) {
            sortMenu.style.display = 'none';
            sortMenu.classList.remove('show');
            sortTrigger.classList.remove('active');
        } else {
            sortMenu.style.display = 'block';
            sortMenu.classList.add('show');
            sortTrigger.classList.add('active');
        }
    }
};

window.updateShop = function(isLoadMore = false, loadAll = false) {
    const productGrid = document.getElementById('productGrid');
    if (!productGrid) return;
    
    const loadMoreBtn = document.getElementById('load-more-products');
    let page = 1;
    if (isLoadMore && loadMoreBtn && !loadAll) {
        page = (parseInt(loadMoreBtn.getAttribute('data-page')) || 1) + 1;
    }

    const urlParams = new URLSearchParams(window.location.search);
    if (loadAll) {
        urlParams.set('all', 'true');
    }
    
    // Set search if exists in input
    const searchInput = document.getElementById('adminOrderSearch') || document.getElementById('productSearch');
    if (searchInput && searchInput.value) urlParams.set('search', searchInput.value);

    const minPrice = document.getElementById('min-price'), maxPrice = document.getElementById('max-price');
    if (minPrice && minPrice.value) {
        urlParams.set('min_price', minPrice.value);
    } else {
        urlParams.delete('min_price');
    }
    
    if (maxPrice && maxPrice.value) {
        urlParams.set('max_price', maxPrice.value);
    } else {
        urlParams.delete('max_price');
    }
    
    const discountOnly = document.getElementById('discount-only-filter');
    if (discountOnly && discountOnly.checked) urlParams.set('discount_only', 'true');
    
    const bestSellers = document.getElementById('best-seller-filter');
    if (bestSellers && bestSellers.checked) urlParams.set('best_sellers', 'true');

    urlParams.set('ajax', '1');
    urlParams.set('page', page);
    
    if (!isLoadMore && !loadAll) {
        productGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 5rem;"><i class="fas fa-spinner fa-spin fa-2x"></i></div>';
        productGrid.style.opacity = '1';
    }

    // Show loading state on button
    let originalBtnText = '';
    if ((isLoadMore || loadAll) && loadMoreBtn) {
        originalBtnText = loadMoreBtn.innerHTML;
        loadMoreBtn.disabled = true;
        loadMoreBtn.innerHTML = 'Duke u ngarkuar... <i class="fas fa-spinner fa-spin ml-2"></i>';
    }

    const currentPath = window.location.pathname.includes('/products') ? window.location.pathname : '/products';

    fetch(`${currentPath}?${urlParams.toString()}`)
        .then(res => res.json())
        .then(data => {
            if (isLoadMore || loadAll) {
                if (data.products && data.products.length > 0) {
                    if (loadAll) productGrid.innerHTML = '';
                    appendProducts(data.products, productGrid);
                    if (loadMoreBtn) loadMoreBtn.setAttribute('data-page', page);
                }
            } else {
                renderProducts(data.products, productGrid);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
            
            updateResultsCount(data.total_count);
            
            if (loadMoreBtn) {
                const totalPages = data.total_pages || 1;
                const currentPage = isLoadMore ? page : 1;
                if (currentPage >= totalPages || loadAll) {
                    loadMoreBtn.parentElement.classList.add('d-none');
                } else {
                    loadMoreBtn.parentElement.classList.remove('d-none');
                    loadMoreBtn.setAttribute('data-page', currentPage);
                }
            }
            
            if (!isLoadMore && !loadAll) {
                urlParams.delete('ajax');
                window.history.pushState({}, '', `${currentPath}?${urlParams.toString()}`);
            }
        })
        .catch(err => console.error('Error updating shop:', err))
        .finally(() => {
            productGrid.style.opacity = '1';
            const sortMenu = document.getElementById('sortMenu');
            if (sortMenu) sortMenu.classList.remove('show');
            if ((isLoadMore || loadAll) && loadMoreBtn) {
                loadMoreBtn.disabled = false;
                loadMoreBtn.innerHTML = originalBtnText;
            }
        });
};

window.filterHomeCategory = function(category, btnElement) {
    // UI update for chips
    document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');
    
    const grid = document.getElementById('recommended-grid');
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (!grid) return;
    
    grid.style.opacity = '0.5';
    grid.style.pointerEvents = 'none';
    
    let url = `/products?page=1&ajax=1`;
    if (category !== 'all') {
        url += `&category=${encodeURIComponent(category)}`;
    }
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = '';
            if (data.products && data.products.length > 0) {
                appendProducts(data.products, grid);
                if (loadMoreBtn) {
                    loadMoreBtn.setAttribute('data-page', '1');
                    loadMoreBtn.setAttribute('data-category', category);
                    if (1 >= data.total_pages) {
                        loadMoreBtn.parentElement.classList.add('d-none');
                    } else {
                        loadMoreBtn.parentElement.classList.remove('d-none');
                    }
                }
            } else {
                grid.innerHTML = '<div class="no-products-found" style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #64748b;">Nuk u gjet asnjë produkt në këtë kategori.</div>';
                if (loadMoreBtn) loadMoreBtn.parentElement.classList.add('d-none');
            }
        })
        .catch(err => console.error('Error filtering home products:', err))
        .finally(() => {
            grid.style.opacity = '1';
            grid.style.pointerEvents = 'auto';
        });
};

document.addEventListener('DOMContentLoaded', () => {
    // Clickable rows handler (e.g. in cart)
    const sidebar = document.getElementById('shopSidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const closeBtn = document.getElementById('closeSidebar');
    const closeBtnAlt = document.getElementById('closeSidebarAlt');

    if (closeBtn) closeBtn.onclick = function() { window.closeShopSidebar(); };
    if (closeBtnAlt) closeBtnAlt.onclick = function() { window.closeShopSidebar(); };
    if (overlay) overlay.onclick = function() { window.closeShopSidebar(); };

    // Clickable rows handler (e.g. in cart)
    const hasIntersectionObserver = 'IntersectionObserver' in window;
    
    // --- FADE-IN ANIMATION OBSERVER ---
    if (hasIntersectionObserver) {
        const fadeObserverOptions = {
            threshold: 0.1,
            rootMargin: "0px 0px -50px 0px"
        };

        const fadeObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, fadeObserverOptions);

        // Function to observe all current fade-in sections
        const observeSections = () => {
            document.querySelectorAll('.fade-in-section:not(.visible)').forEach(section => {
                fadeObserver.observe(section);
            });
        };

        observeSections();
    } else {
        // Fallback for older browsers
        document.querySelectorAll('.fade-in-section').forEach(s => s.classList.add('visible'));
    }

    // --- SEARCH FOCUS HANDLER ---
    document.querySelectorAll('input[type="text"][id*="Search"]').forEach(input => {
        input.addEventListener('focus', function(e) {
            if (window.innerWidth <= 768) {
                setTimeout(() => {
                    const elementPosition = this.getBoundingClientRect().top + window.scrollY;
                    const offsetPosition = elementPosition - 80;
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }, 300);
            }
        });
    });

    // --- NAVIGATION LOGIC ---
    // Close desktop dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        // Profile Dropdown
        const profileDropdown = document.getElementById('desktopProfileDropdown');
        const profileBtn = document.querySelector('.profile-dropdown-btn');
        if (profileDropdown && profileDropdown.classList.contains('active')) {
            if (!profileDropdown.contains(event.target) && (!profileBtn || !profileBtn.contains(event.target))) {
                profileDropdown.classList.remove('active');
                if(profileBtn) profileBtn.classList.remove('active');
            }
        }

        // Mini Cart Dropdown
        const miniCart = document.getElementById('miniCart');
        const cartBtn = document.getElementById('cartBadgeBtn');
        if (miniCart && miniCart.classList.contains('active')) {
            // Check if click is outside the cart container
            if (!miniCart.contains(event.target) && (!cartBtn || !cartBtn.contains(event.target))) {
                miniCart.classList.remove('active');
            }
        }
    });

    // Mobile Header Scroll Effect
    const mobileHeader = document.querySelector('.mobile-header');
    if (mobileHeader) {
        const handleScroll = () => {
            if (window.scrollY > 50) {
                mobileHeader.classList.add('scrolled');
            } else {
                mobileHeader.classList.remove('scrolled');
            }
        };
        handleScroll();
        window.addEventListener('scroll', handleScroll);
    }

    // Sticky Navbar (Desktop)
    const navbar = document.querySelector('.desktop-header');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // --- SEARCH & FILTER LOGIC ---
    const searchInputs = [document.getElementById('productSearch'), document.getElementById('productSearchMobile')];
    const searchPreviews = [document.getElementById('searchPreview'), document.getElementById('searchPreviewMobile')];
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    searchInputs.forEach((searchInput, index) => {
        if (!searchInput) return;
        const searchPreview = searchPreviews[index];
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            
            // REMOVED: Front-end filter for current page (only filter when clicking enter or view all)
            // if (typeof filterHomeProducts === 'function') {
            //     filterHomeProducts(term, getActiveCategory());
            // }

            // Live search preview
            clearTimeout(searchTimeout);
            if (term.length >= 2) {
                searchTimeout = setTimeout(async () => {
                    try {
                        const limit = searchInput.dataset.limit || 20;
                        const response = await fetch(`/api/search?q=${encodeURIComponent(term)}&limit=${limit}`);
                        const products = await response.json();
                        
                        if (searchPreview && products.length > 0) {
                            searchPreview.innerHTML = products.map(p => {
                                const hasDiscount = p.discount_price && p.discount_price < p.price;
                                const priceDisplay = hasDiscount ? 
                                    `<span class="preview-price-old" style="text-decoration: line-through; color: #94a3b8; font-size: 0.7rem; margin-right: 5px;">€${p.price}</span><span class="preview-price" style="color: #10b981;">€${p.discount_price}</span>` :
                                    `<span class="preview-price">€${p.price}</span>`;
                                
                                return `
                                    <a href="/product/${p.id}" class="preview-item">
                                        <div class="preview-image" style="width: 40px; height: 40px; flex-shrink: 0; background: #fff; border-radius: 6px; overflow: hidden; border: 1px solid #f1f5f9;">
                                            <img src="${p.image_url}" alt="${p.name}" style="width: 100%; height: 100%; object-fit: contain; padding: 2px;">
                                        </div>
                                        <div class="preview-info">
                                            <span class="preview-name">${p.name}</span>
                                            ${p.size ? `<span class="preview-size" style="font-size: 0.7rem; color: #64748b; display: block;">${p.size}</span>` : ''}
                                            <div class="preview-price-wrapper" style="font-size: 0.75rem; color: var(--primary); font-weight: 600;">
                                                ${priceDisplay}
                                            </div>
                                        </div>
                                    </a>
                                `;
                            }).join('') + `
                                <a href="/products?q=${encodeURIComponent(term)}" class="preview-item view-all-search">
                                    <span style="width: 100%; text-align: center; color: var(--primary); font-weight: 600; font-size: 0.85rem; padding: 5px 0;">Shiko të gjitha</span>
                                </a>
                            `;
                            searchPreview.classList.add('active');
                        } else if (searchPreview) {
                            searchPreview.classList.remove('active');
                        }
                    } catch (err) {
                        console.error('Search error:', err);
                    }
                }, 300);
            } else if (searchPreview) {
                searchPreview.classList.remove('active');
            }
        });

        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const term = searchInput.value;
                if (term.length >= 2) {
                    window.location.href = `/products?q=${encodeURIComponent(term)}`;
                }
            }
        });

        document.addEventListener('click', (e) => {
            if (searchPreview && !searchInput.contains(e.target) && !searchPreview.contains(e.target)) {
                searchPreview.classList.remove('active');
            }
        });
    });

    if (filterBtns) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const category = btn.getAttribute('data-filter');
                filterHomeProducts(searchInput ? searchInput.value.toLowerCase() : '', category);
            });
        });
    }

    function getActiveCategory() {
        const activeBtn = document.querySelector('.filter-btn.active');
        return activeBtn ? activeBtn.getAttribute('data-filter') : 'all';
    }

    function filterHomeProducts(searchTerm, category) {
        productCards.forEach(card => {
            const h3 = card.querySelector('h3');
            if (!h3) return;
            const name = h3.textContent.toLowerCase();
            const cardCategory = card.getAttribute('data-category');
            const matchesSearch = name.includes(searchTerm);
            const matchesCategory = category === 'all' || cardCategory === category;

            if (matchesSearch && matchesCategory) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // --- QUANTITY SELECTOR LOGIC ---
    const qtyInputs = document.querySelectorAll('.quantity-selector');
    qtyInputs.forEach(selector => {
        const input = selector.querySelector('.qty-input');
        const minusBtn = selector.querySelector('.minus');
        const plusBtn = selector.querySelector('.plus');
        
        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                let val = parseInt(input.value);
                input.value = val + 1;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            });
        }

        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                let val = parseInt(input.value);
                if (val > 1) {
                    input.value = val - 1;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }

        if (input) {
            input.addEventListener('focus', () => {
                if (!input.disabled) input.select();
            });

            input.addEventListener('keydown', (e) => {
                if (['.', ',', 'e', 'E', '-'].includes(e.key)) {
                    e.preventDefault();
                    return false;
                }
            });

            input.addEventListener('input', function() {
                // Allow empty input while typing
                if (this.value === '') return;
                
                let val = parseInt(this.value);
                if (isNaN(val) || val < 1) val = 1;
                
                // For cart page, we might want to submit automatically after delay
                const form = this.closest('form');
                if (form && (form.matches('[action*="/cart/set/"]') || form.classList.contains('qty-set-form'))) {
                    clearTimeout(this.timeout);
                    this.timeout = setTimeout(() => {
                        this.value = val;
                        form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                    }, 800);
                }
            });

            input.addEventListener('blur', function() {
                if (this.value === '' || parseInt(this.value) < 1) {
                    this.value = 1;
                    const form = this.closest('form');
                    if (form) form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            });
        }
    });

    // --- AJAX CART & FORM HANDLERS ---
    document.body.addEventListener('submit', async (e) => {
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
        const isSet = e.target.matches('form[action*="/cart/set/"]');
        const isRemove = e.target.matches('form[action*="/cart/remove/"]');
        
        if (!isAdd && !isUpdate && !isRemove && !isSet) return;
        
        e.preventDefault();
        const form = e.target;

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

        let btn = form.querySelector('button[type="submit"]');
        let originalContent = btn ? btn.innerHTML : '';
        let pQtyInput = null;
        let previousQty = null;

        if (btn) {
            btn.disabled = true;
            if (isAdd) btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
        
        if (isUpdate) {
            pQtyInput = form.querySelector('.qty-input');
            if (pQtyInput) previousQty = pQtyInput.value;
            // Removed disabling logic to prevent multi-click lockup
        }

        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (isAdd) {
                    showToast(data.message, 'success');
                    window.updateGlobalBadges(data);
                } else if (isRemove && data.removed) {
                    const row = form.closest('tr');
                    if (row) {
                        row.style.opacity = '0';
                        setTimeout(() => {
                            row.remove();
                            if (document.querySelectorAll('tbody tr').length === 0) location.reload(); 
                        }, 300);
                    }
                    showToast(data.message, 'info');
                    
                    // Update Summary Sidebar on Remove
                    const summaryTotal = document.querySelector('.summary-total-price');
                    if (summaryTotal) summaryTotal.textContent = '€' + data.total_price.toFixed(2);
                    
                    const summarySavings = document.querySelector('.summary-total-savings');
                    if (summarySavings && data.total_savings !== undefined) {
                        summarySavings.textContent = '-€' + data.total_savings.toFixed(2);
                        const sRow = summarySavings.closest('.savings-row');
                        if (sRow) sRow.style.display = data.total_savings > 0 ? 'flex' : 'none';
                    }

                    const summaryDelivery = document.querySelector('.summary-delivery-fee');
                    if (summaryDelivery && data.delivery_fee !== undefined) {
                        summaryDelivery.textContent = data.delivery_fee > 0 ? '€' + data.delivery_fee.toFixed(2) : 'Falas';
                    }

                    const grandTotalEls = document.querySelectorAll('.grand-total, .grand-total-amount');
                    grandTotalEls.forEach(el => {
                        const amount = data.grand_total || data.total_price;
                        el.textContent = '€' + amount.toFixed(2);
                    });

                    const oldTotalEl = document.querySelector('.cart-summary h3');
                    if (oldTotalEl) oldTotalEl.textContent = 'Totali: €' + data.total_price.toFixed(2);
                    window.updateGlobalBadges(data);

                } else if (isUpdate || isSet) {
                    const row = form.closest('tr') || form.closest('.cart-item-card');
                    if (row) {
                        const qtyInput = row.querySelector('.qty-input');
                        if (qtyInput) qtyInput.value = data.quantity;
                        
                        // Desktop subtotal
                        const itemTotal = row.querySelector('td:nth-child(4)');
                        if (itemTotal) itemTotal.textContent = '€' + data.item_total.toFixed(2);
                        
                        // Mobile subtotal
                        const mobileItemTotal = row.querySelector('.item-total-mobile');
                        if (mobileItemTotal) mobileItemTotal.textContent = '€' + data.item_total.toFixed(2);

                        // Individual Item Savings update
                        const itemSavingsEl = row.querySelector('.savings-amount');
                        if (itemSavingsEl && data.item_savings !== undefined) {
                            itemSavingsEl.textContent = '€' + data.item_savings.toFixed(2);
                            const label = itemSavingsEl.closest('.item-savings-label');
                            if (label) label.style.display = data.item_savings > 0 ? 'block' : 'none';
                        }

                        const container = row.querySelector('.quantity-selector') || row.querySelector('.quantity-control');
                        if (container) {
                            container.querySelectorAll('.qty-btn').forEach(b => {
                                // Check if it's a minus button
                                const isMinus = b.matches('.minus') || b.querySelector('.fa-minus');
                                b.disabled = isMinus ? data.quantity <= 1 : false;
                            });
                        }
                    }
                    
                    // Update Summary Sidebar
                    const summaryTotal = document.querySelector('.summary-total-price');
                    if (summaryTotal) summaryTotal.textContent = '€' + data.total_price.toFixed(2);
                    
                    const summarySavings = document.querySelector('.summary-total-savings');
                    if (summarySavings && data.total_savings !== undefined) {
                        summarySavings.textContent = '-€' + data.total_savings.toFixed(2);
                        const row = summarySavings.closest('.savings-row');
                        if (row) row.style.display = data.total_savings > 0 ? 'flex' : 'none';
                    }

                    const summaryDelivery = document.querySelector('.summary-delivery-fee');
                    if (summaryDelivery && data.delivery_fee !== undefined) {
                        summaryDelivery.textContent = data.delivery_fee > 0 ? '€' + data.delivery_fee.toFixed(2) : 'Falas';
                    }

                    const totalEl = document.querySelector('.cart-summary h3');
                    if (totalEl) totalEl.textContent = 'Totali: €' + data.total_price.toFixed(2);
                    
                    const grandTotalEls = document.querySelectorAll('.grand-total');
                    grandTotalEls.forEach(el => {
                        const amount = data.grand_total || data.total_price;
                        el.textContent = '€' + amount.toFixed(2);
                    });
                    
                    const sidebarGrandTotal = document.querySelector('.grand-total-amount');
                    if (sidebarGrandTotal) {
                        const amount = data.grand_total || data.total_price;
                        sidebarGrandTotal.textContent = '€' + amount.toFixed(2);
                    }
                    grandTotalEls.forEach(el => {
                        el.textContent = '€' + data.total_price.toFixed(2);
                    });

                    window.updateGlobalBadges(data);
                }
            } else {
                if (isUpdate && pQtyInput) pQtyInput.value = previousQty;
                if (isUpdate) {
                    const row = form.closest('tr');
                    if (row) {
                        const container = row.querySelector('.quantity-selector');
                        if (container) {
                            container.querySelectorAll('button').forEach(b => b.disabled = false);
                            const input = container.querySelector('input');
                            if (input) input.disabled = false;
                        }
                        const minusBtn = row.querySelector('.minus');
                        if (minusBtn && previousQty <= 1) minusBtn.disabled = true;
                    }
                }

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
                        if (result.isConfirmed) window.location.href = '/login';
                    });
                } else {
                    showToast(data.message || 'Ndodhi një gabim.', 'danger');
                }
            }
        } catch (error) {
            if (isUpdate && pQtyInput && previousQty !== null) pQtyInput.value = previousQty;
            console.error('Error:', error);
            if (!isRemove) showToast('Ndodhi një gabim.', 'danger');
        } finally {
            if (btn && isAdd) {
                btn.disabled = false;
                btn.innerHTML = originalContent;
            }
        }
    });

    // --- LINK CONFIRMATIONS ---
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

        if (result.isConfirmed && href) {
            window.location.href = href;
        }
    });

    // --- CHECKOUT LOGIN CHECK ---
    const checkoutBtn = document.querySelector('.checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', (e) => {
            const isLoggedIn = document.body.dataset.userLoggedIn === 'true';
            if (!isLoggedIn) {
                e.preventDefault();
                Swal.fire({
                    title: 'Kërkohet Hyrja',
                    text: 'Ju lutemi kyçuni ose regjistrohuni për të vazhuduar me pagesën.',
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

    // --- PRODUCT CARD CLICKABLE ---
    document.querySelectorAll('.product-card').forEach(card => {
        card.style.cursor = 'pointer';
        card.addEventListener('click', (e) => {
            if (e.target.closest('button') || e.target.closest('a') || e.target.closest('form')) return;
            const detailLink = card.querySelector('a[href*="/product/"]');
            if (detailLink) window.location.href = detailLink.href;
        });
    });

    // --- CAROUSEL SWIPE ---
    initCarouselSwipe();

    // --- HERO CAROUSEL AUTO PLAY ---
    if (document.querySelector('.hero-carousel')) {
        showSlides(slideIndex);
        startSlideTimer();
        const container = document.querySelector('.hero-carousel-container');
        if (container) {
            container.addEventListener('mouseenter', () => clearInterval(slideInterval));
            container.addEventListener('mouseleave', () => startSlideTimer());
        }
    }

    // --- SORT DROPDOWN ---
    const sortTrigger = document.getElementById('sortTrigger');
    const sortMenu = document.getElementById('sortMenu');

    if (sortTrigger && sortMenu) {
        sortTrigger.addEventListener('click', window.toggleSortMenu);

        // Handle Item Click
        sortMenu.addEventListener('click', function(e) {
            const item = e.target.closest('.sort-trigger');
            if (item && !item.id) {
                e.preventDefault();
                const sortVal = item.dataset.sort;
                const labelText = item.innerText.trim();
                
                const labelSpan = document.getElementById('current-sort-label');
                if (labelSpan) labelSpan.textContent = labelText;
                
                sortMenu.querySelectorAll('.sort-trigger').forEach(el => el.classList.remove('active'));
                item.classList.add('active');

                const urlParams = new URLSearchParams(window.location.search);
                urlParams.set('sort', sortVal);
                urlParams.set('page', 1);
                
                window.history.pushState({}, '', `${window.location.pathname}?${urlParams.toString()}`);
                
                if (typeof updateShop === 'function') {
                    updateShop();
                }

                sortMenu.classList.remove('show');
                sortTrigger.classList.remove('active');
            }
        });

        // Close when clicking outside
        document.addEventListener('click', function(e) {
            if (!sortTrigger.contains(e.target) && !sortMenu.contains(e.target)) {
                sortMenu.classList.remove('show');
                sortTrigger.classList.remove('active');
            }
        });
    }

    // --- SHOP FILTERS ---
    const brandSelect = document.getElementById('brand-select');
    if (brandSelect) brandSelect.addEventListener('change', updateShop);

    const applyPriceBtn = document.getElementById('apply-price-filter');
    if (applyPriceBtn) applyPriceBtn.addEventListener('click', () => {
        updateShop();
    });

    // Mobile Sidebar Toggle
    const openSidebarBtn = document.getElementById('openSidebar');
    const closeSidebarBtn = document.getElementById('closeSidebar');
    const closeSidebarBtnAlt = document.getElementById('closeSidebarAlt');
    // Using existing sidebar and overlay variables from outer scope if they exist, 
    // but they are already declared at the top of this DOMContentLoaded block.
    
    if (openSidebarBtn && sidebar && overlay) {
        openSidebarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.openShopSidebar();
        });
    }

    if (closeSidebarBtn && sidebar && overlay) {
        closeSidebarBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.closeShopSidebar();
        });
    }

    if (closeSidebarBtnAlt && sidebar && overlay) {
        closeSidebarBtnAlt.addEventListener('click', (e) => {
            e.preventDefault();
            window.closeShopSidebar();
        });
    }

    if (overlay) {
        overlay.addEventListener('click', window.closeShopSidebar);
    }

    if (sidebar) {
        sidebar.addEventListener('click', (e) => {
            // Prevent clicks inside the sidebar from closing it (if bubbling to overlay)
            e.stopPropagation();
        });
    }

    // Refresh cart & wishlist badges on load
    // Disabled to prevent flickering since server renders correct initial counts
    /*
    if (typeof refreshMiniCart === 'function') {
        refreshMiniCart();
    }
    */
});

// --- GLOBAL FUNCTIONS ---

window.toggleProfileDropdown = function() {
    const dropdown = document.getElementById('desktopProfileDropdown');
    const btn = document.querySelector('.profile-dropdown-btn');
    if(dropdown) {
        dropdown.classList.toggle('active');
        if(btn) btn.classList.toggle('active');
    }
};

// --- CART AJAX & MINI-CART FUNCTIONS ---

window.addToCartAJAX = function(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrf_token', document.querySelector('meta[name="csrf-token"]').content);

    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            refreshMiniCart();
            showMiniCart();
        }
    })
    .catch(err => console.error('Error adding to cart:', err));
};

window.buyNow = function(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrf_token', document.querySelector('meta[name="csrf-token"]').content);

    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/cart/checkout';
        }
    })
    .catch(err => console.error('Error in Buy Now:', err));
};

window.toggleMiniCart = function(e) {
    if (e) e.preventDefault();
    const miniCart = document.getElementById('miniCart');
    if (miniCart) {
        miniCart.classList.toggle('active');
        if (miniCart.classList.contains('active')) {
            refreshMiniCart();
        }
    }
};

window.showMiniCart = function() {
    const miniCart = document.getElementById('miniCart');
    if (miniCart) {
        miniCart.classList.add('active');
        // If it was auto-opened (after adding to cart), auto-close it
        setTimeout(() => {
            // Only auto-hide if it's still active (might have been toggled off manually)
            if (miniCart.classList.contains('active')) {
                miniCart.classList.remove('active');
            }
        }, 2500); 
    }
};

window.updateGlobalBadges = function(data) {
    if (!data) return;

    // 1. Update Cart Badges
    if (data.cart_count !== undefined) {
        const cartBadges = document.querySelectorAll('.cart-badge, .mobile-cart-badge, .cart-count-badge, .items-count-badge-mobile');
        cartBadges.forEach(badge => {
            if (badge.classList.contains('items-count-badge-mobile')) {
                badge.textContent = `${data.cart_count} produkt(e)`;
            } else {
                badge.textContent = data.cart_count;
            }
            if (data.cart_count > 0) {
                badge.classList.remove('d-none');
                badge.style.setProperty('display', 'flex', 'important');
            } else {
                badge.classList.add('d-none');
                badge.style.setProperty('display', 'none', 'important');
            }
        });
        
        const countText = document.querySelector('.items-count-text');
        if (countText) countText.textContent = `${data.cart_count} produkt(e)`;
    }

    // 2. Update Wishlist Badges
    if (data.wishlist_count !== undefined) {
        const wishBadges = document.querySelectorAll('.wishlist-count, .cart-badge-wish');
        wishBadges.forEach(badge => {
            badge.textContent = data.wishlist_count;
            if (data.wishlist_count > 0) {
                badge.classList.remove('d-none');
                badge.style.setProperty('display', 'flex', 'important');
            } else {
                badge.classList.add('d-none');
                badge.style.setProperty('display', 'none', 'important');
            }
        });
    }

    // 3. Update Mini Cart Footer Button Total
    if (data.total_price !== undefined) {
        const footerBtn = document.querySelector('.btn-go-to-cart');
        if (footerBtn) {
            footerBtn.innerHTML = `SHKO NË SHPORTË (${parseFloat(data.total_price).toFixed(2)} €)`;
        }
    }
};

window.refreshMiniCart = function() {
    fetch('/cart/mini-cart-data')
    .then(res => res.json())
    .then(data => {
        // Use the unified update function
        window.updateGlobalBadges(data);

        // Update Desktop Mini Cart
        const desktopContainer = document.querySelector('.mini-cart-items');
        if (desktopContainer) {
            if (data.cart_items.length === 0) {
                desktopContainer.innerHTML = `
                    <div class="empty-mini-cart">
                        <i class="fas fa-shopping-basket fa-3x mb-3"></i>
                        <p>Shporta juaj është boshe.</p>
                    </div>`;
            } else {
                let html = '';
                data.cart_items.forEach(item => {
                    const price = item.discount_price || item.price;
                    const productUrl = `/product/${item._id}`;
                    html += `
                    <div class="mini-cart-item" data-id="${item._id}" onclick="window.location.href='${productUrl}';">
                        <a href="${productUrl}" class="mini-cart-img-wrapper" onclick="event.stopPropagation()">
                            <img src="${item.image_url}" alt="${item.name}" class="mini-cart-img">
                        </a>
                        <div class="mini-cart-info">
                            <a href="${productUrl}" class="mini-item-name" onclick="event.stopPropagation()">${item.name}</a>
                            <div class="mini-item-meta">
                                <span class="mini-item-price">€${parseFloat(price).toFixed(2)}</span>
                                <div class="mini-qty-control" onclick="event.stopPropagation()">
                                    <button class="qty-control-btn minus" onclick="updateMiniQty(event, '${item._id}', 'decrease')">
                                        <i class="fas fa-minus"></i>
                                    </button>
                                    <span class="qty-val">${item.quantity}</span>
                                    <button class="qty-control-btn plus" onclick="updateMiniQty(event, '${item._id}', 'increase')">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <button class="remove-item-btn" onclick="updateMiniQty(event, '${item._id}', 'remove')" title="Hiqe">
                            <i class="far fa-trash-alt"></i>
                        </button>
                    </div>`;
                });
                desktopContainer.innerHTML = html;
            }
        }

        // Update Mobile Modal Cart
        const mobileContainer = document.querySelector('.mobile-cart-items-list');
        const mobileHeader = document.querySelector('.mobile-mini-cart-header');
        
        if (mobileContainer) {
            if (data.cart_items.length === 0) {
                // Update header (hide clear cart link)
                if (mobileHeader) mobileHeader.innerHTML = '';
                
                mobileContainer.innerHTML = `
                    <div class="empty-cart-state-mobile">
                        <div class="icon-circle">
                            <i class="fas fa-shopping-basket"></i>
                        </div>
                        <h4>Shporta juaj është boshe</h4>
                        <p>Ju nuk keni shtuar asnjë produkt në shportë akoma.</p>
                        <button class="btn-primary-mobile" onclick="closeCartModal()">Fillo Blerjen</button>
                    </div>`;
            } else {
                // Update header
                if (mobileHeader) {
                    mobileHeader.innerHTML = `
                        <a href="#" class="clear-cart-link-mobile" onclick="clearCart(event)">
                            <i class="fas fa-trash-alt"></i> Pastro Shportën
                        </a>`;
                }

                let html = '';
                data.cart_items.forEach(item => {
                    const price = item.discount_price || item.price;
                    const productUrl = `/product/${item._id}`;
                    html += `
                    <div class="mobile-mini-cart-item" data-id="${item._id}" onclick="window.location.href='${productUrl}';">
                        <div class="mobile-mini-cart-img">
                            <img src="${item.image_url}" alt="${item.name}">
                        </div>
                        <div class="mobile-mini-cart-info">
                            <p class="name">${item.name}</p>
                            <p class="price">€${parseFloat(price).toFixed(2)}</p>
                            <div class="qty-control-mobile" onclick="event.stopPropagation()">
                                <button class="qty-btn" onclick="updateMiniQty(event, '${item._id}', 'decrease')">-</button>
                                <span class="qty-val">${item.quantity}</span>
                                <button class="qty-btn" onclick="updateMiniQty(event, '${item._id}', 'increase')">+</button>
                            </div>
                        </div>
                        <button class="remove-btn" onclick="updateMiniQty(event, '${item._id}', 'remove')">
                            <i class="far fa-trash-alt"></i>
                        </button>
                    </div>`;
                });
                mobileContainer.innerHTML = html;
            }
        }
    });
};

window.updateMiniQty = function(event, productId, action) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    // Support both desktop mini-cart and mobile modal cart
    const itemRows = document.querySelectorAll(`.mini-cart-item[data-id="${productId}"], .mobile-mini-cart-item[data-id="${productId}"]`);
    
    itemRows.forEach(row => {
        const qtySpan = row.querySelector('.qty-val');
        const currentQty = qtySpan ? parseInt(qtySpan.textContent) : 1;

        if (action === 'remove') {
            row.style.opacity = '0.5';
            row.style.pointerEvents = 'none';
        } else if (qtySpan) {
            if (action === 'increase') qtySpan.textContent = currentQty + 1;
            else if (action === 'decrease' && currentQty > 1) qtySpan.textContent = currentQty - 1;
        }
    });

    const formData = new FormData();
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    formData.append('csrf_token', csrfToken);

    fetch(`/cart/update/${productId}/${action}`, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            window.updateGlobalBadges(data);

            itemRows.forEach(row => {
                if (action === 'remove') {
                    row.remove();
                } else {
                    const qtySpan = row.querySelector('.qty-val');
                    if (qtySpan) qtySpan.textContent = data.quantity;
                }
            });

            // If cart is empty now, refresh the whole UI to show empty state
            if (data.cart_count === 0) {
                window.refreshMiniCart();
            }

            // Update totals if they exist
            const footers = document.querySelectorAll('.mini-cart-footer, .modal-footer-cart');
            footers.forEach(footer => {
                const totalSpan = footer.querySelector('.btn-go-to-cart, .total-price, .grand-total');
                if (totalSpan) {
                    if (totalSpan.classList.contains('btn-go-to-cart')) {
                        totalSpan.textContent = `SHKO NË SHPORTË (${data.cart_total.toFixed(2)} €)`;
                    } else if (totalSpan.classList.contains('total-price') && !totalSpan.closest('.modal-footer-cart')) {
                         totalSpan.textContent = `€${data.cart_total.toFixed(2)}`;
                    } else if (footer.classList.contains('modal-footer-cart')) {
                        // Handle the new detailed modal footer
                        const subtotalEl = footer.querySelector('div:first-child > div:first-child span:last-child');
                        const deliveryEl = footer.querySelector('div:first-child > div:nth-child(2) span:last-child');
                        const savingsEl = footer.querySelector('div:first-child > div:nth-child(3) span:last-child');
                        const grandTotalEl = footer.querySelector('.grand-total') || footer.querySelector('div:first-child > div:last-child span:last-child');
                        
                        if (subtotalEl) subtotalEl.textContent = `€${data.cart_total.toFixed(2)}`;
                        if (deliveryEl) deliveryEl.textContent = data.delivery_fee > 0 ? `€${data.delivery_fee.toFixed(2)}` : 'Falas';
                        if (grandTotalEl) grandTotalEl.textContent = `€${data.grand_total.toFixed(2)}`;
                    }
                }
            });

            if (data.cart_count === 0) {
                // Desktop
                const desktopContainer = document.querySelector('.mini-cart-items');
                if (desktopContainer) {
                    desktopContainer.innerHTML = `
                        <div class="empty-mini-cart">
                            <i class="fas fa-shopping-basket fa-3x mb-3"></i>
                            <p>Shporta juaj është boshe.</p>
                        </div>`;
                }
                // Mobile
                const mobileContainer = document.querySelector('.mobile-cart-items-list');
                if (mobileContainer) {
                    mobileContainer.innerHTML = `
                        <div class="empty-cart-state-mobile">
                            <div class="icon-circle"><i class="fas fa-shopping-basket"></i></div>
                            <h4>Shporta juaj është boshe</h4>
                            <p>Ju nuk keni shtuar asnjë produkt në shportë akoma.</p>
                            <button class="btn-primary-mobile" onclick="closeCartModal()">Fillo Blerjen</button>
                        </div>`;
                }
                // Remove footer
                const mobileFooter = document.querySelector('.modal-footer-cart');
                if (mobileFooter) mobileFooter.remove();
            }

            if (window.location.pathname === '/cart/') {
                window.location.reload();
            }
        }
    })
    .catch(err => {
        console.error('Error updating mini cart:', err);
        if (qtySpan) qtySpan.textContent = currentQty;
        if (itemRow) {
            itemRow.style.opacity = '1';
            itemRow.style.pointerEvents = 'auto';
        }
    });
};

window.clearCart = function(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    // Improved confirmation dialog
    const confirmed = window.confirm('Kujdes: A jeni i sigurt që dëshironi të fshini të gjitha produktet nga shporta? Ky veprim nuk mund të kthehet mbrapsht.');
    if (!confirmed) return;

    const formData = new FormData();
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    formData.append('csrf_token', csrfToken);

    fetch('/cart/clear', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            refreshMiniCart();
            if (window.location.pathname === '/cart/') {
                window.location.reload();
            }
        }
    })
    .catch(err => console.error('Error clearing cart:', err));
};

window.openCategoriesModal = function() {
    window.closeCartModal();
    window.closeProfileModal();
    const modal = document.getElementById('mobile-categories-modal');
    if(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

window.closeCategoriesModal = function() {
    const modal = document.getElementById('mobile-categories-modal');
    if(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
};

window.openCartModal = function() {
    window.closeCategoriesModal();
    window.closeProfileModal();
    const modal = document.getElementById('mobile-cart-modal');
    if(modal) {
        // Refresh cart data whenever opening the modal to ensure it's not empty/stale
        if (typeof window.refreshMiniCart === 'function') {
            window.refreshMiniCart();
        }
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

window.closeCartModal = function() {
    const modal = document.getElementById('mobile-cart-modal');
    if(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
};

// --- FIX FOR BACK BUTTON CACHE (bfcache) ---
window.addEventListener('pageshow', (event) => {
    // If the page is loaded from cache (e.g. back button), force close all modals
    if (event.persisted) {
        if (typeof window.closeCategoriesModal === 'function') window.closeCategoriesModal();
        if (typeof window.closeCartModal === 'function') window.closeCartModal();
        if (typeof window.closeProfileModal === 'function') window.closeProfileModal();
    }
});

// Auto-close modals when any link inside them is clicked
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.full-screen-modal a').forEach(link => {
        link.addEventListener('click', () => {
            const modal = link.closest('.full-screen-modal');
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
});

window.openProfileModal = function() {
    window.closeCategoriesModal();
    window.closeCartModal();
    const modal = document.getElementById('mobile-profile-modal');
    if(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
};

window.closeProfileModal = function() {
    const modal = document.getElementById('mobile-profile-modal');
    if(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
};

window.confirmDelete = function(formElement) {
    Swal.fire({
        title: 'A jeni i sigurt?',
        text: "Ky veprim nuk mund të kthehet mbrapa!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#e11d48',
        cancelButtonColor: '#64748b',
        confirmButtonText: 'Po, fshije!',
        cancelButtonText: 'Anulo'
    }).then((result) => {
        if (result.isConfirmed) formElement.submit();
    });
    return false;
};

window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    toast.innerHTML = `
        <i class="fas ${icon}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

window.toggleFavorite = async function(btn, productId) {
    if (!productId) return;
    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : '';

    try {
        const response = await fetch(`/product/favorite/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken }
        });
        const data = await response.json();
        if (data.success) {
            const icon = btn.querySelector('i');
            
            // Use the unified global update function
            window.updateGlobalBadges({
                wishlist_count: data.wishlist_count !== undefined ? data.wishlist_count : data.count
            });

            if (data.action === 'added') {
                btn.classList.add('active');
                if (icon) { icon.classList.replace('far', 'fas'); }
                showToast('Produkti u shtua në të preferuarat!', 'success');
            } else {
                btn.classList.remove('active');
                if (icon) { icon.classList.replace('fas', 'far'); }
                showToast('Produkti u largua nga të preferuarat', 'info');
                
                // --- WISHLIST DYNAMIC EMPTY STATE ---
                if (window.location.pathname.includes('/wishlist')) {
                    const card = btn.closest('.product-card');
                    if (card) {
                        card.style.opacity = '0';
                        setTimeout(() => {
                            card.remove();
                            const remaining = document.querySelectorAll('.product-grid-v2 .product-card').length;
                            if (remaining === 0) {
                                const container = document.querySelector('.wishlist-section .container');
                                if (container) {
                                    container.innerHTML = `
                                        <div class="empty-state-card text-center py-5">
                                            <div class="empty-icon mb-4"><i class="far fa-heart fa-3x"></i></div>
                                            <h3>Nuk keni asnjë produkt të preferuar ende</h3>
                                            <p class="text-muted mb-4">Eksploroni produktet tona dhe shtoni ato që ju pëlqejnë këtu.</p>
                                            <a href="/products" class="btn btn-primary px-5 btn-lg">Eksploro Dyqanin</a>
                                        </div>
                                    `;
                                }
                            }
                        }, 300);
                    }
                }
            }
        } else {
            showToast('Duhet të jeni të kyçur për të ruajtur produktet.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Ndodhi një gabim.', 'error');
    }
};

function initCarouselSwipe() {
    const containers = document.querySelectorAll('.carousel-container');
    containers.forEach(container => {
        let touchstartX = 0;
        let touchendX = 0;
        
        container.addEventListener('touchstart', e => {
            touchstartX = e.changedTouches[0].clientX;
        }, {passive: true});
        
        container.addEventListener('touchend', e => {
            touchendX = e.changedTouches[0].clientX;
            const dx = touchendX - touchstartX;
            if (Math.abs(dx) > 50) {
                moveCarousel(null, container, dx < 0 ? 1 : -1);
            }
        }, {passive: true});
    });
}

function moveCarousel(event, btnOrTrack, direction) {
    if (event && event.preventDefault) { event.preventDefault(); event.stopPropagation(); }
    const container = btnOrTrack.closest('.carousel-container');
    if (!container) return;
    const track = container.querySelector('.carousel-track');
    const images = track ? track.querySelectorAll('img') : [];
    if (!images.length) return;
    let currentIndex = parseInt(container.getAttribute('data-index') || '0');
    currentIndex += direction;
    if (currentIndex < 0) currentIndex = images.length - 1;
    if (currentIndex >= images.length) currentIndex = 0;
    goToSlide(container, currentIndex);
}

function goToSlide(container, index) {
    const track = container.querySelector('.carousel-track');
    const dots = container.querySelectorAll('.indicator-dot');
    const thumbs = container.parentElement ? container.parentElement.querySelectorAll('.thumbnail') : null;
    container.setAttribute('data-index', index);
    if (track) track.style.transform = `translateX(-${index * 100}%)`;
    if (dots) dots.forEach((dot, i) => dot.classList.toggle('active', i === index));
    if (thumbs) {
        thumbs.forEach((thumb, i) => {
            thumb.style.borderColor = i === index ? 'var(--primary)' : 'transparent';
            thumb.style.opacity = i === index ? '1' : '0.7';
        });
    }
}

let slideIndex = 1;
let slideInterval;

function startSlideTimer() {
    clearInterval(slideInterval);
    slideInterval = setInterval(() => plusSlides(1), 5000);
}

window.plusSlides = function(n) { showSlides(slideIndex += n); }
window.currentSlide = function(n) { showSlides(slideIndex = n); }

function showSlides(n) {
    let i;
    const slides = document.getElementsByClassName("hero-slide");
    const dots = document.getElementsByClassName("dot");
    if (!slides || slides.length === 0) return;
    if (n > slides.length) slideIndex = 1;
    if (n < 1) slideIndex = slides.length;
    for (i = 0; i < slides.length; i++) slides[i].classList.remove("active");
    for (i = 0; i < dots.length; i++) dots[i].classList.remove("active");
    slides[slideIndex-1].classList.add("active");
    if (dots.length >= slideIndex) dots[slideIndex-1].classList.add("active");
    startSlideTimer();
}

function initHeroSwipe() {
    const hero = document.querySelector('.hero-carousel-container');
    if (!hero) return;
    
    let touchstartX = 0;
    let touchendX = 0;
    
    hero.addEventListener('touchstart', e => {
        touchstartX = e.changedTouches[0].clientX;
    }, {passive: true});
    
    hero.addEventListener('touchend', e => {
        touchendX = e.changedTouches[0].clientX;
        const dx = touchendX - touchstartX;
        if (Math.abs(dx) > 50) {
            plusSlides(dx < 0 ? 1 : -1);
        }
    }, {passive: true});
}

document.addEventListener('DOMContentLoaded', () => {
    initHeroSwipe();
});

function openQuickView(element) {
    const card = element.closest('.product-card');
    if (!card) return;
    const modal = document.getElementById('quickViewModal');
    if (!modal) return;
    
    document.getElementById('qv-image').src = card.getAttribute('data-img') || '';
    document.getElementById('qv-title').innerText = card.getAttribute('data-name') || '';
    document.getElementById('qv-price').innerText = (card.getAttribute('data-price') || '0') + ' €';
    document.getElementById('qv-description').innerText = card.getAttribute('data-desc') || '';
    
    const detailsBtn = modal.querySelector('a.btn-outline, a[href]');
    if (detailsBtn) detailsBtn.href = card.getAttribute('data-url') || '#';
    
    const addBtn = document.getElementById('qv-add-btn');
    if (addBtn) addBtn.onclick = () => addToCartQuickView(card.getAttribute('data-id'));

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeQuickView() {
    const modal = document.getElementById('quickViewModal');
    if (modal) { modal.classList.remove('show'); document.body.style.overflow = ''; }
}

window.onclick = function(event) {
    const modal = document.getElementById('quickViewModal');
    if (event.target == modal) closeQuickView();
};

// --- PRODUCT CAROUSEL SCROLL ---
window.scrollCarousel = function(btn, direction) {
    const wrapper = btn.closest('.product-carousel-wrapper');
    if (!wrapper) return;
    const carousel = wrapper.querySelector('.product-carousel');
    if (!carousel) return;
    
    const scrollAmount = carousel.clientWidth * 0.8;
    const maxScroll = carousel.scrollWidth - carousel.clientWidth;
    let target = carousel.scrollLeft + (direction * scrollAmount);
    
    // Clamp values to prevent overscrolling beyond the first/last product
    if (target < 0) target = 0;
    if (target > maxScroll) target = maxScroll;
    
    carousel.scrollTo({
        left: target,
        behavior: 'smooth'
    });
};

// Initial check for carousel buttons visibility
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.product-carousel').forEach(carousel => {
        const updateButtons = () => {
            const wrapper = carousel.closest('.product-carousel-wrapper');
            if (!wrapper) return;
            const prevBtn = wrapper.querySelector('.scroll-btn.prev');
            const nextBtn = wrapper.querySelector('.scroll-btn.next');
            const maxScroll = carousel.scrollWidth - carousel.clientWidth;
            
            if (prevBtn) prevBtn.style.opacity = carousel.scrollLeft <= 5 ? '0' : '1';
            if (prevBtn) prevBtn.style.pointerEvents = carousel.scrollLeft <= 5 ? 'none' : 'auto';
            if (nextBtn) nextBtn.style.opacity = carousel.scrollLeft >= maxScroll - 5 ? '0' : '1';
            if (nextBtn) nextBtn.style.pointerEvents = carousel.scrollLeft >= maxScroll - 5 ? 'none' : 'auto';
        };

        carousel.addEventListener('scroll', updateButtons);
        // Initial state
        setTimeout(updateButtons, 500);
        window.addEventListener('resize', updateButtons);
    });
});

function addToCartQuickView(productId) { addToCart(productId); closeQuickView(); }

function addToCart(productId) {
    if (!productId) return;
    const btns = document.querySelectorAll(`button[onclick="addToCart('${productId}')"]`);
    btns.forEach(btn => { btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; btn.disabled = true; });

    fetch(`/cart/add/${productId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Use the unified global update function
            window.updateGlobalBadges({
                cart_count: data.count,
                total_price: data.total_price // Assuming total_price is returned
            });
            
            // Refresh modal lists
            if (typeof window.refreshMiniCart === 'function') {
                window.refreshMiniCart();
            }
            
            btns.forEach(btn => {
                btn.innerHTML = '<i class="fas fa-check"></i>';
                btn.style.background = '#10b981';
                setTimeout(() => {
                    btn.innerHTML = '<i class="fas fa-shopping-basket"></i>';
                    btn.disabled = false;
                    btn.style.background = '';
                }, 1500);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        btns.forEach(btn => {
            btn.innerHTML = '<i class="fas fa-exclamation"></i>';
            setTimeout(() => { btn.innerHTML = '<i class="fas fa-shopping-basket"></i>'; btn.disabled = false; }, 2000);
        });
    });
}


// Global Refresh to fix any badge visibility blockers removed as it causes delay
// Relying on server-side rendering for initial load.

// Global Refresh to fix any badge visibility blockers removed as it causes delay
// Relying on server-side rendering for initial load.

