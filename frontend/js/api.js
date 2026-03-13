// Pure — API Wrappers + Auth Helpers

// ── Guest session management ─────────────────────────
const GUEST = {
    _key: 'pure_guest_id',
    getId() {
        let id = localStorage.getItem(this._key);
        if (!id) { id = crypto.randomUUID(); localStorage.setItem(this._key, id); }
        return id;
    },
    clear() { localStorage.removeItem(this._key); }
};

const AUTH = {
    getToken() { return localStorage.getItem(CONFIG.TOKEN_KEY); },
    getUser() {
        const u = localStorage.getItem(CONFIG.USER_KEY);
        return u ? JSON.parse(u) : null;
    },
    isLoggedIn() { return !!this.getToken(); },
    isAdmin() { const u = this.getUser(); return u && u.role === 'admin'; },
    save(token, user) {
        localStorage.setItem(CONFIG.TOKEN_KEY, token);
        localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
        GUEST.clear();
    },
    logout() {
        localStorage.removeItem(CONFIG.TOKEN_KEY);
        localStorage.removeItem(CONFIG.USER_KEY);
        window.location.href = 'login.html';
    },
    requireLogin() {
        if (!this.isLoggedIn()) { window.location.href = 'login.html'; return false; }
        return true;
    },
    requireAdmin() {
        if (!this.isLoggedIn() || !this.isAdmin()) { window.location.href = 'login.html'; return false; }
        return true;
    }
};

const API = {
    _headers() {
        const h = { 'Content-Type': 'application/json', 'x-api-key': CONFIG.API_KEY };
        const token = AUTH.getToken();
        if (token) h['Authorization'] = `Bearer ${token}`;
        else h['x-guest-id'] = GUEST.getId();
        return h;
    },

    async get(path) {
        const res = await fetch(`${CONFIG.API_BASE}${path}`, { headers: this._headers() });
        if (res.status === 401 && AUTH.isLoggedIn()) { AUTH.logout(); return; }
        if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
        return res.json();
    },

    async post(path, body = {}) {
        const res = await fetch(`${CONFIG.API_BASE}${path}`, {
            method: 'POST', headers: this._headers(), body: JSON.stringify(body),
        });
        if (res.status === 401 && AUTH.isLoggedIn()) { AUTH.logout(); return; }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `POST ${path} failed: ${res.status}`);
        }
        return res.json();
    },

    async put(path, body = {}) {
        const res = await fetch(`${CONFIG.API_BASE}${path}`, {
            method: 'PUT', headers: this._headers(), body: JSON.stringify(body),
        });
        if (res.status === 401 && AUTH.isLoggedIn()) { AUTH.logout(); return; }
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `PUT ${path} failed: ${res.status}`);
        }
        return res.json();
    },

    async del(path) {
        const res = await fetch(`${CONFIG.API_BASE}${path}`, {
            method: 'DELETE', headers: this._headers(),
        });
        if (res.status === 401 && AUTH.isLoggedIn()) { AUTH.logout(); return; }
        if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`);
        return res.json();
    },

    // Auth
    login(email, password) { return this.post('/api/auth/login', { email, password }); },
    register(name, email, password) {
        return this.post('/api/auth/register', { name, email, password });
    },
    verifyOTP(email, otp) { return this.post('/api/auth/verify-otp', { email, otp }); },
    resendOTP(email) { return this.post('/api/auth/resend-otp', { email }); },
    getProfileCompletion() { return this.get('/api/auth/profile-completion'); },
    updateProfile(data) { return this.put('/api/auth/profile', data); },
    sendPhoneOTP(phone) { return this.post('/api/auth/send-phone-otp', { phone }); },
    verifyPhoneOTP(phone, otp) { return this.post('/api/auth/verify-phone-otp', { phone, otp }); },

    // Preferences
    trackCategoryView(category) { return this.post('/api/auth/track-category', { category }); },
    getPersonalizedCategories() { return this.get('/api/products/personalized-categories'); },

    // Products
    getProducts(params = {}) {
        const qs = new URLSearchParams(params).toString();
        return this.get(`/api/products${qs ? '?' + qs : ''}`);
    },
    getProduct(id) { return this.get(`/api/products/${id}`); },
    getCategories() { return this.get('/api/products/categories'); },
    getPopupRecommendations(categories = '', exclude = '', limit = 3) {
        const qs = new URLSearchParams({ categories, exclude, limit }).toString();
        return this.get(`/api/products/popup-recommendations?${qs}`);
    },

    // Cart
    getCart() { return this.get('/api/cart'); },
    addToCart(item_id, quantity = 1) { return this.post('/api/cart', { item_id, quantity }); },
    removeFromCart(cartItemId) { return this.del(`/api/cart/${cartItemId}`); },

    // Wishlist
    getWishlist() { return this.get('/api/wishlist'); },
    addToWishlist(item_id) { return this.post('/api/wishlist', { item_id }); },
    removeFromWishlist(wishItemId) { return this.del(`/api/wishlist/${wishItemId}`); },

    // Chat
    chat(message, session_id = null) { return this.post('/api/chat', { message, session_id }); },
    chatFeedback(session_id, item_id, action) { return this.post('/api/chat/feedback', { session_id, item_id, action }); },

    // Orders & Promo
    placeOrder(promo_code = null) {
        const body = {};
        if (promo_code) body.promo_code = promo_code;
        if (!AUTH.isLoggedIn()) body.guest_session = GUEST.getId();
        return this.post('/api/orders', body);
    },
    getOrders() { return this.get('/api/orders'); },
    getPromoInfo() { return this.get('/api/orders/promo-info'); },

    // Dashboard
    dashOverview() { return this.get('/api/dashboard/overview'); },
    dashSessions(path = '') { return this.get(`/api/dashboard/sessions${path ? '?path=' + path : ''}`); },
    dashConversation(sessionId) { return this.get(`/api/dashboard/conversations?session_id=${sessionId}`); },
    dashUsers() { return this.get('/api/dashboard/users'); },
    dashRecStats() { return this.get('/api/dashboard/recommendation-stats'); },
};


// ── Toast ────────────────────────────────────────────
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}


// ── Badge updater ────────────────────────────────────
async function updateBadges() {
    try {
        const cart = await API.getCart();
        document.querySelectorAll('.cart-badge').forEach(b => {
            if (cart && cart.length) { b.style.display = 'flex'; b.textContent = cart.length; }
            else b.style.display = 'none';
        });
    } catch (e) { /* ignore */ }
    if (AUTH.isLoggedIn()) {
        try {
            const wish = await API.getWishlist();
            document.querySelectorAll('.wish-badge').forEach(b => {
                if (wish && wish.length) { b.style.display = 'flex'; b.textContent = wish.length; }
                else b.style.display = 'none';
            });
        } catch (e) { /* ignore */ }
    }
}


// ── Update nav for auth state ────────────────────────
function updateNav() {
    const authLinks = document.getElementById('authLinks');
    if (!authLinks) return;
    if (AUTH.isLoggedIn()) {
        const user = AUTH.getUser();
        let html = '';
        if (AUTH.isAdmin()) {
            html += '<a href="dashboard.html" class="nav-link">Dashboard</a>';
        }
        html += `<a href="profile.html" class="nav-user-wrap" id="navUserWrap" title="My Profile">
            <span class="profile-ring" id="profileRing">
                <svg class="profile-ring-svg" viewBox="0 0 40 40">
                    <circle cx="20" cy="20" r="18" fill="none" stroke="var(--border)" stroke-width="3"/>
                    <circle cx="20" cy="20" r="18" fill="none" stroke="var(--accent)" stroke-width="3"
                        stroke-dasharray="113.1" stroke-dashoffset="113.1" stroke-linecap="round"
                        class="profile-ring-progress" id="profileRingProgress"
                        transform="rotate(-90 20 20)"/>
                </svg>
                <span class="profile-ring-initial">${user ? user.name.charAt(0).toUpperCase() : 'U'}</span>
            </span>
            <span class="nav-user-name">${user ? user.name : 'User'}</span>
        </a>`;
        html += '<a href="#" class="nav-link" onclick="AUTH.logout(); return false;">Logout</a>';
        authLinks.innerHTML = html;
        loadProfileCompletion();
    } else {
        authLinks.innerHTML = '<a href="login.html" class="nav-link btn-outline-sm">Sign In</a>';
    }
}

async function loadProfileCompletion() {
    try {
        const data = await API.getProfileCompletion();
        const pct = data.percentage || 0;
        const circumference = 2 * Math.PI * 18; // 113.1
        const offset = circumference - (pct / 100) * circumference;
        const ring = document.getElementById('profileRingProgress');
        if (ring) ring.style.strokeDashoffset = offset;

        // Show profile prompt if DOB or anniversary missing
        if (data.missing && (data.missing.includes('date_of_birth') || data.missing.includes('anniversary_date'))) {
            const prompted = sessionStorage.getItem('tanishq_profile_prompted');
            if (!prompted) {
                sessionStorage.setItem('tanishq_profile_prompted', '1');
                setTimeout(() => showProfilePrompt(data.missing), 2000);
            }
        }
    } catch (e) { /* ignore */ }
}

function showProfilePrompt(missing) {
    const overlay = document.createElement('div');
    overlay.id = 'profilePromptOverlay';
    overlay.className = 'popup-overlay';
    const needDob = missing.includes('date_of_birth');
    const needAnniv = missing.includes('anniversary_date');
    overlay.innerHTML = `
        <div class="popup-modal email-popup-modal" style="max-width:420px">
            <button class="popup-close" onclick="document.getElementById('profilePromptOverlay').remove()">&times;</button>
            <div class="popup-header">
                <span class="popup-badge">Complete Your Profile</span>
                <h3 class="popup-title">Help Us Celebrate With You</h3>
            </div>
            <p class="email-popup-desc">Share your special dates so we can send you personalised offers and birthday surprises!</p>
            <form id="profilePromptForm" class="profile-prompt-form">
                ${needDob ? `<div class="form-group"><label>Date of Birth</label><input type="date" id="profileDob" class="profile-date-input"></div>` : ''}
                ${needAnniv ? `<div class="form-group"><label>Anniversary Date</label><input type="date" id="profileAnniv" class="profile-date-input"></div>` : ''}
                <button type="submit" class="btn-primary full-width" id="profilePromptBtn">Save</button>
            </form>
            <p class="email-popup-note" style="margin-top:8px;cursor:pointer;" onclick="document.getElementById('profilePromptOverlay').remove()">Skip for now</p>
        </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

    document.getElementById('profilePromptForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const btn = document.getElementById('profilePromptBtn');
        btn.disabled = true;
        btn.textContent = 'Saving...';
        const payload = {};
        const dobEl = document.getElementById('profileDob');
        const annivEl = document.getElementById('profileAnniv');
        if (dobEl && dobEl.value) payload.date_of_birth = dobEl.value;
        if (annivEl && annivEl.value) payload.anniversary_date = annivEl.value;
        try {
            const updated = await API.updateProfile(payload);
            AUTH.save(AUTH.getToken(), updated);
            if (typeof showToast === 'function') showToast('Profile updated!');
            overlay.remove();
            loadProfileCompletion();
        } catch (err) {
            btn.disabled = false;
            btn.textContent = 'Save';
        }
    });
}

document.addEventListener('DOMContentLoaded', updateNav);


// ── Product card generator ──────────────────────────
function productCardHTML(p) {
    const discount = p.original_price && p.original_price > p.price
        ? Math.round((1 - p.price / p.original_price) * 100) : 0;
    const stars = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));

    return `
    <div class="product-card" data-id="${p.id}">
        <div class="product-card-img">
            <img src="${p.image_url}" alt="${p.name}" loading="lazy">
            ${p.featured ? '<span class="product-card-badge">Bestseller</span>' : ''}
            ${discount > 0 ? `<span class="product-card-badge sale-badge">${discount}% OFF</span>` : ''}
            <div class="product-card-actions">
                <button class="product-card-action" title="Add to wishlist" onclick="event.stopPropagation(); quickWishlist(${p.id})">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                </button>
            </div>
        </div>
        <div class="product-card-body">
            <div class="product-card-category">${p.category}</div>
            <div class="product-card-name">${p.name}</div>
            <div class="product-card-rating"><span class="stars">${stars}</span> ${p.rating} (${p.reviews_count})</div>
            <div class="product-card-footer">
                <div>
                    <span class="product-card-price">₹${p.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>
                    ${p.original_price && p.original_price > p.price ? `<span class="product-card-original">₹${p.original_price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</span>` : ''}
                </div>
                <button class="product-card-cart-btn" title="Add to cart" onclick="event.stopPropagation(); quickCart(${p.id})">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                </button>
            </div>
        </div>
    </div>`;
}

async function quickCart(itemId) {
    try { await API.addToCart(itemId); showToast('Added to cart!'); updateBadges(); }
    catch (e) { showToast('Failed to add to cart', 'error'); }
}

async function quickWishlist(itemId) {
    if (!AUTH.isLoggedIn()) { showToast('Please sign in to use wishlist', 'error'); return; }
    try { await API.addToWishlist(itemId); showToast('Added to wishlist!'); updateBadges(); }
    catch (e) { showToast('Already in wishlist', 'error'); }
}

document.addEventListener('click', (e) => {
    const card = e.target.closest('.product-card');
    if (card && !e.target.closest('button')) {
        window.location.href = `product.html?id=${card.dataset.id}`;
    }
});
