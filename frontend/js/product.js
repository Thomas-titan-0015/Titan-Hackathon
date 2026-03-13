// Pure — Product Detail
(async function () {
    updateBadges();

    const id = new URLSearchParams(window.location.search).get('id');
    if (!id) { window.location.href = 'catalog.html'; return; }

    try {
        const p = await API.getProduct(id);
        document.getElementById('breadcrumbCat').textContent = p.category;
        document.getElementById('breadcrumbName').textContent = p.name;
        document.getElementById('productImage').src = p.image_url;
        document.getElementById('productImage').alt = p.name;
        document.getElementById('productCategory').textContent = p.category;
        document.getElementById('productName').textContent = p.name;

        const stars = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));
        document.getElementById('productRating').innerHTML = `<span class="stars">${stars}</span> ${p.rating} (${p.reviews_count} reviews)`;
        document.getElementById('productPrice').textContent = `₹${p.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;

        if (p.original_price && p.original_price > p.price) {
            const discount = Math.round((1 - p.price / p.original_price) * 100);
            document.getElementById('productOriginal').textContent = `₹${p.original_price.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
            document.getElementById('productDiscount').textContent = `${discount}% OFF`;
        }

        document.getElementById('productDesc').textContent = p.description;

        if (p.attributes) {
            const container = document.getElementById('productAttrs');
            container.innerHTML = Object.entries(p.attributes).map(([k, v]) =>
                `<span class="attr-tag">${k}: ${v}</span>`
            ).join('');
        }

        document.getElementById('stockStatus').textContent = p.in_stock ? 'In Stock' : 'Out of Stock';
        document.getElementById('stockStatus').className = p.in_stock ? 'stock-status in-stock' : 'stock-status out-of-stock';

        document.getElementById('addCartBtn').addEventListener('click', async () => {
            try { await API.addToCart(p.id); showToast('Added to cart!'); updateBadges(); }
            catch (e) { showToast('Failed to add', 'error'); }
        });

        document.getElementById('addWishBtn').addEventListener('click', async () => {
            if (!AUTH.isLoggedIn()) { showToast('Please sign in to use wishlist', 'error'); return; }
            try { await API.addToWishlist(p.id); showToast('Added to wishlist!'); updateBadges(); }
            catch (e) { showToast('Already in wishlist', 'error'); }
        });
    } catch (e) {
        document.querySelector('.product-detail').innerHTML = '<div class="empty-state"><h3>Product not found</h3><a href="catalog.html" class="btn-primary">Browse Collection</a></div>';
    }
})();
