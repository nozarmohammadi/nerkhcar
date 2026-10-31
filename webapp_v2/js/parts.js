// Reusable UI parts shared by pages. Page files only compose these.
window.NK = window.NK || {};
NK.P = (function () {
  var U = NK.U, T = NK.T;
  function title(x) { return U.h('h1', 'c-title', x); }
  function note(x) { return U.h('p', 'c-note', x); }
  function sub(d) { return d.brand + ' · ' + U.year(d.year); }
  function price(d, big) {
    return U.h('div', 'c-price' + (big ? ' c-price--big' : ''), null, [
      U.h('span', 'c-price__num', U.fa(d.price_m)), U.h('span', 'c-price__unit', T.prices.unit)]);
  }
  function row(d) {
    var main = U.h('div', 'c-row__main', null, [U.h('b', 'c-row__name', d.name), U.h('span', 'c-row__sub', sub(d))]);
    return U.on(U.h('div', 'c-row', null, [main, price(d)]), function () { NK.openCar(d.id); });
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
  return { title: title, note: note, sub: sub, price: price, row: row, empty: empty, state: state, options: options };
})();
