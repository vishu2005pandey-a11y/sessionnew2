document.addEventListener('DOMContentLoaded', function() {
    const tg = window.Telegram.WebApp;
    const phoneSection = document.getElementById('phone-section');
    const otpSection = document.getElementById('otp-section');
    const requestPhoneBtn = document.getElementById('request-phone-btn');
    const otpBoxes = document.querySelectorAll('.otp-box');
    const keys = document.querySelectorAll('.key');
    const verifyBtn = document.getElementById('verify-btn');
    
    let currentIndex = 0;
    
    // Initialize Telegram Web App
    tg.ready();
    tg.expand();
    
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
    }
    
    // Request Phone Access
    requestPhoneBtn.addEventListener('click', function() {
        // Since Telegram Web App doesn't directly access phone number,
        // we'll send a request to the bot to send OTP
        if (tg) {
            tg.sendData('request_otp:requested');
            showOtpSection();
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
                tg.sendData('verify_otp:' + otp);
            }
        }
    });
});
