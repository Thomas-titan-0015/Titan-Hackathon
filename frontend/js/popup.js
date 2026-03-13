// Tanishq — Popup System
// 1) Phone OTP verification popup at 5 seconds (logged-in users without verified phone)
// 2) Product recommendation popup at 70th-percentile session time
(function () {
    const EMAIL_POPUP_DELAY = 5000;
    const PERCENTILE_70 = 0.70;
    const DEFAULT_SESSION_DURATION = 300000; // 5 min default; 70th %ile ≈ 3.5 min
    const SESSION_KEY = 'tanishq_popup_state';
    const SESSION_TIMES_KEY = 'tanishq_session_times';

    let browsedCategories = [];
    let shownProductIds = [];
    let sessionStart = Date.now();

    function getState() {
        try { return JSON.parse(sessionStorage.getItem(SESSION_KEY) || '{}'); } catch { return {}; }
    }
    function setState(obj) {
        sessionStorage.setItem(SESSION_KEY, JSON.stringify({ ...getState(), ...obj }));
    }
    function getStoredTimes() {
        try { return JSON.parse(localStorage.getItem(SESSION_TIMES_KEY) || '[]'); } catch { return []; }
    }
    function recordSessionDuration(dur) {
        const times = getStoredTimes();
        times.push(dur);
        if (times.length > 30) times.shift();
        localStorage.setItem(SESSION_TIMES_KEY, JSON.stringify(times));
    }
    function compute70thPercentile() {
        const times = getStoredTimes();
        if (times.length < 3) return Math.round(DEFAULT_SESSION_DURATION * PERCENTILE_70);
        const sorted = [...times].sort((a, b) => a - b);
        const idx = Math.floor(sorted.length * PERCENTILE_70);
        return sorted[Math.min(idx, sorted.length - 1)];
    }

    function trackCategory() {
        const params = new URLSearchParams(window.location.search);
        const cat = params.get('category');
        if (cat && !browsedCategories.includes(cat)) browsedCategories.push(cat);
        document.querySelectorAll('.product-card-category').forEach(el => {
            const c = el.textContent.trim();
            if (c && !browsedCategories.includes(c)) browsedCategories.push(c);
        });
    }

    /* ───── 1. Phone OTP popup (5 seconds, logged-in users only) ───── */
    function scheduleEmailPopup() {
        if (getState().emailShown) return;
        if (!AUTH.isLoggedIn()) return;
        const user = AUTH.getUser();
        if (user && user.phone_verified) return;
        setTimeout(showPhoneOTPPopup, EMAIL_POPUP_DELAY);
    }

    function showPhoneOTPPopup() {
        if (getState().emailShown) return;
        if (!AUTH.isLoggedIn()) return;
        setState({ emailShown: true });

        const overlay = document.createElement('div');
        overlay.id = 'tanishqPhonePopup';
        overlay.className = 'popup-overlay';
        overlay.innerHTML = `
            <div class="popup-modal email-popup-modal">
                <button class="popup-close" onclick="document.getElementById('tanishqPhonePopup').remove()">&times;</button>
                <div class="popup-header">
                    <span class="popup-badge">Verify Your Phone</span>
                    <h3 class="popup-title">Stay Connected</h3>
                </div>
                <p class="email-popup-desc">Add your phone number to receive order updates, exclusive deals, and complete your profile.</p>
                <div id="phoneStep1">
                    <form id="phoneOTPForm" class="email-optin-form" onsubmit="return false;">
                        <div style="display:flex;gap:8px;align-items:center;">
                            <span style="color:var(--text-secondary);font-size:.95rem;white-space:nowrap;">+91</span>
                            <input type="tel" id="phoneOTPInput" placeholder="Enter 10-digit mobile number" maxlength="10" pattern="[0-9]{10}" required style="flex:1;">
                        </div>
                        <button type="submit" class="btn-primary" id="phoneSendBtn">Send OTP</button>
                    </form>
                </div>
                <div id="phoneStep2" style="display:none;">
                    <p style="color:var(--text-secondary);font-size:.88rem;margin-bottom:12px;" id="phoneSentMsg"></p>
                    <form id="phoneVerifyForm" class="email-optin-form" onsubmit="return false;">
                        <input type="text" id="phoneOTPCode" placeholder="Enter 6-digit OTP" maxlength="6" pattern="[0-9]{6}" required>
                        <button type="submit" class="btn-primary" id="phoneVerifyBtn">Verify</button>
                    </form>
                    <button style="background:none;border:none;color:var(--accent);font-size:.82rem;margin-top:8px;cursor:pointer;" id="phoneResendBtn">Resend OTP</button>
                </div>
                <p class="email-popup-note">We'll only use this for order updates & exclusive offers.</p>
            </div>
        `;
        document.body.appendChild(overlay);

        let currentPhone = '';

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });

        document.getElementById('phoneOTPForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const raw = document.getElementById('phoneOTPInput').value.trim();
            if (!/^\d{10}$/.test(raw)) { if (typeof showToast === 'function') showToast('Enter a valid 10-digit number', 'error'); return; }
            currentPhone = '+91' + raw;
            const btn = document.getElementById('phoneSendBtn');
            btn.textContent = 'Sending...';
            btn.disabled = true;
            try {
                await API.sendPhoneOTP(currentPhone);
                document.getElementById('phoneStep1').style.display = 'none';
                document.getElementById('phoneStep2').style.display = 'block';
                document.getElementById('phoneSentMsg').textContent = 'OTP sent to +91 ' + raw;
            } catch (err) {
                if (typeof showToast === 'function') showToast(err.message || 'Failed to send OTP', 'error');
                btn.textContent = 'Send OTP';
                btn.disabled = false;
            }
        });

        document.getElementById('phoneVerifyForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const otp = document.getElementById('phoneOTPCode').value.trim();
            if (!/^\d{6}$/.test(otp)) { if (typeof showToast === 'function') showToast('Enter a valid 6-digit OTP', 'error'); return; }
            const btn = document.getElementById('phoneVerifyBtn');
            btn.textContent = 'Verifying...';
            btn.disabled = true;
            try {
                const updatedUser = await API.verifyPhoneOTP(currentPhone, otp);
                if (updatedUser) {
                    AUTH.save(AUTH.getToken(), updatedUser);
                }
                btn.textContent = 'Verified ✓';
                if (typeof showToast === 'function') showToast('Phone verified successfully!');
                setTimeout(() => overlay.remove(), 1500);
            } catch (err) {
                if (typeof showToast === 'function') showToast(err.message || 'Invalid OTP', 'error');
                btn.textContent = 'Verify';
                btn.disabled = false;
            }
        });

        document.getElementById('phoneResendBtn').addEventListener('click', async () => {
            try {
                await API.sendPhoneOTP(currentPhone);
                if (typeof showToast === 'function') showToast('OTP resent!');
            } catch (err) {
                if (typeof showToast === 'function') showToast('Failed to resend', 'error');
            }
        });

        setTimeout(() => { if (document.getElementById('tanishqPhonePopup')) overlay.remove(); }, 60000);
    }

    /* ───── 2. Product popup at 70th percentile ───── */
    function scheduleProductPopup() {
        if (getState().productShown) return;
        const delay = compute70thPercentile();
        setTimeout(() => { trackCategory(); showProductPopup(); }, delay);
    }

    async function showProductPopup() {
        if (getState().productShown) return;
        setState({ productShown: true });
        try {
            const cats = browsedCategories.length ? browsedCategories.join(',') : '';
            const exclude = shownProductIds.join(',');
            const recs = await API.getPopupRecommendations(cats, exclude, 3);
            if (!recs || recs.length === 0) return;
            recs.forEach(r => { if (!shownProductIds.includes(r.id)) shownProductIds.push(r.id); });
            renderProductPopup(recs);
        } catch (e) { console.error('Popup error:', e); }
    }

    function renderProductPopup(products) {
        const existing = document.getElementById('tanishqProductPopup');
        if (existing) existing.remove();

        const overlay = document.createElement('div');
        overlay.id = 'tanishqProductPopup';
        overlay.className = 'popup-overlay';
        overlay.innerHTML = `
            <div class="popup-modal">
                <button class="popup-close" onclick="document.getElementById('tanishqProductPopup').remove()">&times;</button>
                <div class="popup-header">
                    <span class="popup-badge">AI Recommendation</span>
                    <h3 class="popup-title">Curated Just For You</h3>
                </div>
                <div class="popup-products">
                    ${products.map(p => `
                        <div class="popup-product" onclick="window.location.href='product.html?id=${p.id}'">
                            <img src="${p.image_url}" alt="${p.name}">
                            <div class="popup-product-info">
                                <div class="popup-product-cat">${p.category}</div>
                                <div class="popup-product-name">${p.name}</div>
                                <div class="popup-product-price">₹${p.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
                            </div>
                            <button class="popup-add-btn" onclick="event.stopPropagation(); quickCart(${p.id}); document.getElementById('tanishqProductPopup').remove();">
                                Add to Cart
                            </button>
                        </div>
                    `).join('')}
                </div>
                <div class="popup-footer">
                    <a href="catalog.html" class="popup-browse">Browse All Collections →</a>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });
        setTimeout(() => { if (document.getElementById('tanishqProductPopup')) overlay.remove(); }, 30000);
    }

    /* ───── Record session duration on unload ───── */
    window.addEventListener('beforeunload', () => {
        recordSessionDuration(Date.now() - sessionStart);
    });

    /* ───── Init ───── */
    function init() {
        setTimeout(trackCategory, 2000);
        scheduleEmailPopup();
        scheduleProductPopup();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
