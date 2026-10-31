// Tiny DOM helpers. Safe DOM building only (rule).
window.NK = window.NK || {};
NK.PAGES = {};
NK.U = (function () {
  var NS = 'http://www.w3.org/2000/svg';
  function h(tag, cls, text, kids) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    (kids || []).forEach(function (k) { e.append(k); });
    return e;
  }
  function on(el, fn) { el.addEventListener('click', fn); return el; }
  function icon(name) {
    var s = document.createElementNS(NS, 'svg');
    s.setAttribute('viewBox', '0 0 24 24');
    s.setAttribute('class', 'c-icon');
    var p = document.createElementNS(NS, 'path');
    p.setAttribute('d', NK.ICONS[name]);
    s.append(p);
    return s;
  }
  // Brand logo: two filled shapes, colors come from CSS classes.
  function logo() {
    var s = document.createElementNS(NS, 'svg');
    s.setAttribute('viewBox', NK.LOGO.view);
    s.setAttribute('class', 'c-logo__img');
    ['car', 'arrow'].forEach(function (k) {
      var p = document.createElementNS(NS, 'path');
      p.setAttribute('class', 'c-logo__' + k);
      p.setAttribute('d', NK.LOGO[k]);
      s.append(p);
    });
    return s;
  }
  function fa(n) { return Number(n).toLocaleString('fa-IR'); }
  // Full price in toman from a value in million toman (display only).
  function full(m) { return fa(Math.round(Number(m) * 1000000)); }
  function year(y) { return String(y).replace(/\d/g, function (d) { return NK.T.digits[d]; }); }
  function select(opts, val, fn) {
    var s = h('select', 'c-input');
    opts.forEach(function (o) { var x = h('option', null, o.l); x.value = o.v; s.append(x); });
    s.value = String(val);
    s.addEventListener('change', function () { fn(s.value); });
    return s;
  }
  return { h: h, on: on, icon: icon, logo: logo, fa: fa, full: full, year: year, select: select };
})();
