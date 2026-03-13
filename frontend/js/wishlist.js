// Pure — Wishlist Page
(async function () {
    if (!AUTH.requireLogin()) return;
    updateBadges();
    await loadWishlist();

    async function loadWishlist() {
        try {
            const items = await API.getWishlist();
            const grid = document.getElementById('wishlistGrid');
            if (!items || items.length === 0) {
                grid.innerHTML = '<div class="empty-state"><h3>Your wishlist is empty</h3><p>Save pieces you love for later</p><a href="catalog.html" class="btn-primary">Explore Collection</a></div>';
                return;
            }
            grid.innerHTML = items.map(wi => {
                const p = wi.item;
                return productCardHTML(p) + `<button class="wish-remove-btn" onclick="removeWish(${wi.id})">Remove from Wishlist</button>`;
            }).join('');
        } catch (e) { console.error(e); }
    }

    window.removeWish = async (id) => {
        try { await API.removeFromWishlist(id); showToast('Removed'); await loadWishlist(); updateBadges(); }
        catch (e) { showToast('Error', 'error'); }
    };
})();
