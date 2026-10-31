// Reusable UI parts shared by pages. Page files only compose these.
window.NK = window.NK || {};
NK.P = (function () {
  var U = NK.U, T = NK.T;
  function title(x) { return U.h('h1', 'c-title', x); }
  function note(x) { return U.h('p', 'c-note', x); }
  function sub(d) { return d.brand + ' · ' + U.year(d.year); }
  function price(d, big) {
    return U.h('div', 'c-price' + (big ? ' c-price--big' : ''), null, [
      U.h('span', 'c-price__num', U.full(d.price_m)), U.h('span', 'c-price__unit', T.prices.unitFull)]);
  }
  function row(d, short) {
    var main = U.h('div', 'c-row__main', null, [U.h('b', 'c-row__name', d.name), U.h('span', 'c-row__sub', short ? U.year(d.year) : sub(d))]);
    return U.on(U.h('div', 'c-row', null, [main, price(d)]), function () { NK.openCar(d.id); });
  }
  // Header motif: three fading gold speed lines between the name and the logo.
  function motif() {
    return U.h('div', 'c-hd__lines', null, [1, 2, 3].map(function (n) { return U.h('i', 'c-hd__line c-hd__line--' + n); }));
  }
  // Header wordmark: Persian name + small English name under it (right side).
  function wordmark() {
    return U.h('div', 'c-hd__text', null, [U.h('h1', 'c-hd__title', T.appTitle), U.h('span', 'c-hd__en', T.appEn)]);
  }
  // Brand mark: the logo only (header, left side).
  function brand() {
    var svg = U.logo();
    return U.h('div', 'c-brand', null, [svg]);
  }
  function empty(msg, hint, label, fn) {
    var box = U.h('div', 'c-empty', null, [U.h('p', null, msg)]);
    if (hint) box.append(U.h('span', 'c-note', hint));
    if (label) box.append(U.on(U.h('button', 'c-btn', label), fn));
    return box;
  }
  function state() {
    var st = NK.S.status;
    if (st === 'ok') return null;
    if (st === 'loading') {
      var w = U.h('div');
      for (var i = 0; i < 6; i++) w.append(U.h('div', 'c-skeleton'));
      return w;
    }
    return empty(T.state[st] || T.state.error, null, T.state.retry, NK.load);
  }
  function options() { return NK.S.rows.map(function (r) { return { v: r.id, l: r.name + ' · ' + U.year(r.year) }; }); }
  return { motif: motif, wordmark: wordmark, brand: brand, title: title, note: note, sub: sub, price: price, row: row, empty: empty, state: state, options: options };
})();
