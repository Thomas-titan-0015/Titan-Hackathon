// Tanishq — Chat UI
(function () {
    const fab = document.getElementById('chatFab');
    const panel = document.getElementById('chatPanel');
    const closeBtn = document.getElementById('chatClose');
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');
    const msgs = document.getElementById('chatMessages');
    if (!fab) return;

    let chatSessionId = null;

    // Show greeting bubble on page load (stays until user clicks chat fab)
    const greetBubble = document.createElement('div');
    greetBubble.className = 'chat-greet-bubble';
    greetBubble.innerHTML = 'Hi! How can I help you? 💎';
    greetBubble.addEventListener('click', () => { openChat(); });
    fab.parentElement.appendChild(greetBubble);

    function dismissGreet() {
        greetBubble.classList.add('chat-greet-hide');
        setTimeout(() => greetBubble.remove(), 300);
    }

    function openChat() {
        dismissGreet();
        panel.classList.add('open');
        if (msgs.children.length === 0) {
            appendBot("Welcome to Tanishq! I'm your personal jewelry consultant. How can I help you today?");
        }
        input.focus();
    }

    fab.addEventListener('click', () => {
        if (panel.classList.contains('open')) {
            panel.classList.remove('open');
        } else {
            openChat();
        }
    });
    closeBtn.addEventListener('click', () => panel.classList.remove('open'));

    sendBtn.addEventListener('click', send);
    input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });

    async function send() {
        const text = input.value.trim();
        if (!text) return;

        appendUser(text);
        input.value = '';
        showTyping();

        try {
            const res = await API.chat(text, chatSessionId);
            chatSessionId = res.session_id;
            removeTyping();
            appendBot(res.text, res.recommendations);
        } catch (e) {
            removeTyping();
            appendBot("I'm sorry, I'm having trouble connecting. Please try again.");
        }
    }

    function appendUser(text) {
        const d = document.createElement('div');
        d.className = 'chat-msg user';
        d.innerHTML = `<div class="chat-bubble user">${escapeHTML(text)}</div>`;
        msgs.appendChild(d);
        msgs.scrollTop = msgs.scrollHeight;
    }

    function appendBot(text, recs) {
        const d = document.createElement('div');
        d.className = 'chat-msg bot';
        let html = `<div class="chat-bubble bot">${escapeHTML(text)}</div>`;
        if (recs && recs.length) {
            html += '<div class="chat-recs">';
            recs.forEach(r => {
                html += `
                <div class="chat-rec-card">
                    <img src="${r.image_url}" alt="${escapeHTML(r.name)}">
                    <div class="chat-rec-info">
                        <div class="chat-rec-name">${escapeHTML(r.name)}</div>
                        <div class="chat-rec-price">₹${r.price.toLocaleString('en-IN', {minimumFractionDigits: 2})}</div>
                        <div class="chat-rec-reason">${escapeHTML(r.reason)}</div>
                        <div class="chat-rec-actions">
                            <button onclick="chatLike('${chatSessionId}',${r.id})" title="Love it">♥</button>
                            <button onclick="chatDislike('${chatSessionId}',${r.id})" title="Not for me">✕</button>
                            <button onclick="quickCart(${r.id})" title="Add to cart">🛒</button>
                        </div>
                    </div>
                </div>`;
            });
            html += '</div>';
        }
        d.innerHTML = html;
        msgs.appendChild(d);
        msgs.scrollTop = msgs.scrollHeight;
    }

    function showTyping() {
        const d = document.createElement('div');
        d.className = 'chat-msg bot typing-indicator';
        d.innerHTML = '<div class="chat-bubble bot"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
        msgs.appendChild(d);
        msgs.scrollTop = msgs.scrollHeight;
    }

    function removeTyping() {
        const t = msgs.querySelector('.typing-indicator');
        if (t) t.remove();
    }

    function escapeHTML(str) {
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    window.chatLike = async (sid, itemId) => {
        try { await API.chatFeedback(sid, itemId, 'like'); showToast('Thanks for the feedback!'); }
        catch (e) { /* ignore */ }
    };
    window.chatDislike = async (sid, itemId) => {
        try { await API.chatFeedback(sid, itemId, 'dislike'); showToast('Noted, we\'ll refine our picks.'); }
        catch (e) { /* ignore */ }
    };
})();
