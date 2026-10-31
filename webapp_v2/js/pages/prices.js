// Tab 1: prices (fx strip, search, brand chips, list).
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  function fxStrip() {
    return U.h('div', 'c-fx', null, T.fx.items.map(function (n) {
      return U.h('div', 'c-fx__item', null, [U.h('span', 'c-note', n), U.h('b', 'c-fx__value', T.fx.soon)]);
    }));
  }
  function filtered() {
    var S = NK.S;
    return S.rows.filter(function (r) {
      return (!S.brand || r.brand === S.brand) && r.name.indexOf(S.q) !== -1;
    });
  }
  function list() {
    var st = P.state();
    if (st) return st;
    var rows = filtered();
    if (!rows.length) return P.empty(T.state.empty);
    return U.h('div', null, null, rows.map(P.row));
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
    return U.h('div', 'l-page', null, [P.title(T.app), fxStrip(), q, chips(), box, P.note(T.disc)]);
  };
})();
