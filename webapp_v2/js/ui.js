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
  function fa(n) { return Number(n).toLocaleString('fa-IR'); }
  function year(y) { return String(y).replace(/\d/g, function (d) { return NK.T.digits[d]; }); }
  function select(opts, val, fn) {
    var s = h('select', 'c-input');
    opts.forEach(function (o) { var x = h('option', null, o.l); x.value = o.v; s.append(x); });
    s.value = String(val);
    s.addEventListener('change', function () { fn(s.value); });
    return s;
  }
  return { h: h, on: on, icon: icon, fa: fa, year: year, select: select };
})();
