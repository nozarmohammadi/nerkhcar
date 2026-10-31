// Tab 1: prices (fx strip, search, brand chips, list).
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  // Full toman value for fx item i (dollar, coin, gold); soon label when no fresh data.
  function fxText(i) {
    var fx = NK.S.fx, key = ['dollar', 'coin', 'gold'][i], v = null;
    ((fx && fx.rows) || []).forEach(function (r) { if (r.key === key) v = Number(r.toman); });
    if (!v || !isFinite(v)) return T.fx.soon;
    try { return Math.round(v).toLocaleString('fa-IR'); } catch (e) { return String(Math.round(v)); }
  }
  function fxStrip() {
    return U.h('div', 'c-fx', null, T.fx.items.map(function (n, i) {
      return U.h('div', 'c-fx__item', null, [U.h('span', 'c-note', n), U.h('b', 'c-fx__value', fxText(i))]);
    }));
  }
  function filtered() {
    var S = NK.S;
    return S.rows.filter(function (r) {
      return (!S.brand || r.brand === S.brand) && r.name.indexOf(S.q) !== -1;
    });
  }
  function groups(rows) {
    var order = [], by = {};
    rows.forEach(function (r) {
      var b = r.brand || '';
      if (!by[b]) { by[b] = []; order.push(b); }
      by[b].push(r);
    });
    return U.h('div', 'l-stack', null, order.map(function (b) {
      var head = U.h('div', 'c-card__head', null, [U.h('span', 'c-card__bar'), U.h('b', 'c-card__name', b)]);
      return U.h('section', 'c-card', null, [head].concat(by[b].map(function (d) { return P.row(d, true); })));
    }));
  }
  function cta() {
    var txt = U.h('div', null, null, [U.h('b', 'c-cta__title', T.prices.myTitle), U.h('span', 'c-cta__sub', T.prices.mySub)]);
    var b = U.h('button', 'c-cta', null, [txt, U.h('span', 'c-cta__plus', '+')]);
    b.setAttribute('aria-label', T.prices.myTitle);
    b.addEventListener('click', function () { NK.S.page = 'my'; NK.draw(); });
    return b;
  }
  function list() {
    var st = P.state();
    if (st) return st;
    var rows = filtered();
    if (!rows.length) return P.empty(T.state.empty);
    return groups(rows);
  }
  function chips() {
    var S = NK.S, box = U.h('div', 'c-chips');
    var brands = [''].concat(S.rows.map(function (r) { return r.brand; }).filter(function (b, i, a) { return a.indexOf(b) === i; }));
    brands.forEach(function (b) {
      var c = U.h('span', 'c-chip' + (b === S.brand ? ' c-chip--on' : ''), b || T.prices.all);
      box.append(U.on(c, function () { S.brand = b; NK.draw(); }));
    });
    return box;
  }
  NK.PAGES.prices = function () {
    var q = U.h('input', 'c-input'), box = U.h('div', null, null, [list()]);
    q.placeholder = T.prices.search;
    q.value = NK.S.q;
    q.addEventListener('input', function () { NK.S.q = q.value; box.replaceChildren(list()); });
    return U.h('div', 'l-page', null, [U.h('div', 'c-hd', null, [P.wordmark(), P.motif(), P.brand()]), fxStrip(), q, chips(), box, cta(), P.note(T.disc)]);
  };
})();
