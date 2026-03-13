// Pure — Cart Page (Guest + Logged-in)
(async function () {
    updateBadges();
    await loadCart();
    await loadPromoInfo();

    // Promo code apply
    document.getElementById('applyPromoBtn')?.addEventListener('click', applyPromo);
    document.getElementById('promoInput')?.addEventListener('keydown', e => { if (e.key === 'Enter') applyPromo(); });

    // Payment method toggle
    document.querySelectorAll('input[name="payMethod"]').forEach(r => {
        r.addEventListener('change', () => {
            document.getElementById('cardFields').style.display = r.value === 'card' ? 'block' : 'none';
            document.getElementById('upiFields').style.display = r.value === 'upi' ? 'block' : 'none';
        });
    });

    // Checkout
    document.getElementById('checkoutBtn')?.addEventListener('click', async () => {
        const btn = document.getElementById('checkoutBtn');
        btn.disabled = true;
        btn.textContent = 'Processing...';
        try {
            const promo = window._appliedPromo || null;
            const order = await API.placeOrder(promo);
            const total = order.total - (order.discount || 0);
            showToast(`Order placed! Total: ₹${total.toLocaleString('en-IN', {minimumFractionDigits: 2})}`);
            window._appliedPromo = null;
            await loadCart();
            updateBadges();
        } catch (e) { showToast(e.message || 'Order failed', 'error'); }
        finally { btn.disabled = false; btn.textContent = 'Place Order'; }
    });

    async function loadCart() {
        try {
            const items = await API.getCart();
            const emptyEl = document.getElementById('emptyCart');
            const contentEl = document.getElementById('cartContent');

            if (!items || items.length === 0) {
                emptyEl.style.display = 'block';
                contentEl.style.display = 'none';
                return;
            }
            emptyEl.style.display = 'none';
            contentEl.style.display = 'block';

            const container = document.getElementById('cartItems');
            container.innerHTML = items.map(ci => `
                <div class="cart-item">
                    <img src="${ci.item.image_url}" alt="${ci.item.name}" class="cart-item-img">
                    <div class="cart-item-info">
                        <div class="cart-item-name">${ci.item.name}</div>
                        <div class="cart-item-category">${ci.item.category}</div>
                        <div class="cart-item-price">₹${ci.item.price.toLocaleString('en-IN', {minimumFractionDigits: 2})} × ${ci.quantity}</div>
                    </div>
                    <button class="btn-icon btn-danger" onclick="removeCartItem(${ci.id})">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                    </button>
                </div>
            `).join('');

            const subtotal = items.reduce((s, ci) => s + ci.item.price * ci.quantity, 0);
            const tax = subtotal * 0.08;
            const discount = window._discountAmount || 0;
            const total = subtotal + tax - discount;

            document.getElementById('subtotal').textContent = `₹${subtotal.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
            document.getElementById('tax').textContent = `₹${tax.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
            document.getElementById('discountRow').style.display = discount > 0 ? 'flex' : 'none';
            document.getElementById('discountAmount').textContent = `-₹${discount.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
            document.getElementById('total').textContent = `₹${total.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
        } catch (e) { console.error(e); }
    }

    async function loadPromoInfo() {
        const promoMsg = document.getElementById('promoMessage');
        try {
            const info = await API.getPromoInfo();
            if (info.eligible) {
                promoMsg.innerHTML = `<span class="promo-success">You're eligible! Use code <strong>${info.code}</strong> for \u20b9${info.discount} off</span>`;
            } else {
                promoMsg.innerHTML = `<span class="promo-hint">${info.message}</span>`;
            }
        } catch (e) { /* ignore */ }
    }

    async function applyPromo() {
        const input = document.getElementById('promoInput');
        const msg = document.getElementById('promoMessage');
        const code = input.value.trim().toUpperCase();
        if (!code) return;

        if (!AUTH.isLoggedIn()) {
            msg.innerHTML = '<span class="promo-error">Please sign in to use promo codes</span>';
            return;
        }

        if (code === 'TANISHQ1000') {
            window._appliedPromo = code;
            window._discountAmount = 1000;
            msg.innerHTML = '<span class="promo-success">TANISHQ1000 applied — ₹1,000 off!</span>';
            await loadCart();
        } else {
            msg.innerHTML = '<span class="promo-error">Invalid promo code</span>';
        }
    }

    window.removeCartItem = async (id) => {
        try { await API.removeFromCart(id); showToast('Removed'); await loadCart(); updateBadges(); }
        catch (e) { showToast('Error removing item', 'error'); }
    };
})();
