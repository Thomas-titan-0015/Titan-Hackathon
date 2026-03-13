// Pure — Catalog Page
(async function () {
    updateBadges();

    let allProducts = [];
    let activeCategory = new URLSearchParams(window.location.search).get('category') || '';

    // Load categories
    try {
        const cats = await API.getCategories();
        const container = document.getElementById('categoryPills');
        if (container) {
            let html = `<button class="pill ${!activeCategory ? 'active' : ''}" data-cat="">All</button>`;
            cats.forEach(c => {
                html += `<button class="pill ${activeCategory === c ? 'active' : ''}" data-cat="${c}">${c}</button>`;
            });
            container.innerHTML = html;
            container.addEventListener('click', e => {
                const pill = e.target.closest('.pill');
                if (!pill) return;
                activeCategory = pill.dataset.cat;
                container.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                renderProducts();
                // Track category view for personalization
                if (activeCategory && AUTH.isLoggedIn()) {
                    API.trackCategoryView(activeCategory).catch(() => {});
                }
            });
        }
    } catch (e) { console.error(e); }

    // Load products
    try {
        allProducts = await API.getProducts();
        renderProducts();
        // Track initial category from URL for personalization
        if (activeCategory && AUTH.isLoggedIn()) {
            API.trackCategoryView(activeCategory).catch(() => {});
        }
    } catch (e) { console.error(e); }

    // Search
    const searchInput = document.getElementById('catalogSearch');
    if (searchInput) searchInput.addEventListener('input', () => renderProducts());

    // Price range
    const priceRange = document.getElementById('priceRange');
    const priceVal = document.getElementById('priceVal');
    if (priceRange) {
        priceRange.addEventListener('input', () => {
            priceVal.textContent = `\u20b9${Number(priceRange.value).toLocaleString('en-IN')}`;
            renderProducts();
        });
    }

    // Sort
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) sortSelect.addEventListener('change', () => renderProducts());

    // Mobile filter toggle
    const filterToggle = document.getElementById('filterToggle');
    const sidebar = document.querySelector('.catalog-sidebar');
    if (filterToggle && sidebar) {
        filterToggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    }

    function renderProducts() {
        let filtered = [...allProducts];
        if (activeCategory) filtered = filtered.filter(p => p.category === activeCategory);

        const search = searchInput ? searchInput.value.toLowerCase() : '';
        if (search) filtered = filtered.filter(p => p.name.toLowerCase().includes(search));

        const maxPrice = priceRange ? parseFloat(priceRange.value) : Infinity;
        if (maxPrice < 10000) filtered = filtered.filter(p => p.price <= maxPrice);

        const sort = sortSelect ? sortSelect.value : '';
        if (sort === 'price-asc') filtered.sort((a, b) => a.price - b.price);
        else if (sort === 'price-desc') filtered.sort((a, b) => b.price - a.price);
        else if (sort === 'rating') filtered.sort((a, b) => b.rating - a.rating);
        else if (sort === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name));

        const grid = document.getElementById('productsGrid');
        if (grid) {
            grid.innerHTML = filtered.length
                ? filtered.map(productCardHTML).join('')
                : '<div class="empty-state"><h3>No pieces found</h3><p>Try adjusting your filters</p></div>';
        }
    }
})();
