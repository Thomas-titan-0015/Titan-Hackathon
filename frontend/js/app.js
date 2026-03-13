// Tanishq — Home Page
(async function () {
    updateBadges();

    const catIcons = {
        Rings: '💍', Necklaces: '📿', Earrings: '✨', Bracelets: '⌚',
        Pendants: '💎', Bangles: '🔗',
    };

    // Use personalized categories for logged-in users, fallback to default
    try {
        let cats;
        if (AUTH.isLoggedIn()) {
            try { cats = await API.getPersonalizedCategories(); } catch { cats = null; }
        }
        if (!cats) cats = await API.getCategories();
        const grid = document.getElementById('categoriesGrid');
        if (grid) {
            grid.innerHTML = cats.map(cat => `
                <a href="catalog.html?category=${encodeURIComponent(cat)}" class="category-card">
                    <span class="category-icon">${catIcons[cat] || '💎'}</span>
                    <span class="category-name">${cat}</span>
                </a>
            `).join('');
        }
    } catch (e) { console.error('Categories error:', e); }

    // Show "Recommended for You" section for logged-in users with preferences
    if (AUTH.isLoggedIn()) {
        try {
            const prefCats = await API.getPersonalizedCategories();
            if (prefCats && prefCats.length > 0) {
                const topCat = prefCats[0];
                const allProducts = await API.getProducts({ category: topCat });
                const recGrid = document.getElementById('recommendedGrid');
                const recSection = document.getElementById('recommendedSection');
                if (recGrid && allProducts.length > 0) {
                    if (recSection) recSection.style.display = 'block';
                    document.getElementById('recCategoryName').textContent = topCat;
                    recGrid.innerHTML = allProducts.slice(0, 4).map(productCardHTML).join('');
                }
            }
        } catch (e) { console.error('Recommended error:', e); }
    }

    try {
        const products = await API.getProducts({ featured: true });
        const grid = document.getElementById('featuredGrid');
        if (grid) {
            grid.innerHTML = products.slice(0, 8).map(productCardHTML).join('');
        }
    } catch (e) { console.error('Featured error:', e); }

    try {
        const all = await API.getProducts();
        const sorted = all.sort((a, b) => b.rating - a.rating);
        const grid = document.getElementById('trendingGrid');
        if (grid) {
            grid.innerHTML = sorted.slice(0, 4).map(productCardHTML).join('');
        }
    } catch (e) { console.error('Trending error:', e); }
})();
