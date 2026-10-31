// Tab 2: compare two cars.
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  function tr(k, a, b) { return U.h('tr', null, null, [U.h('th', null, k), U.h('td', null, a), U.h('td', null, b)]); }
  function table(a, b) {
    var t = T.compare;
    return U.h('div', 'c-scroll', null, [U.h('table', 'c-table', null, [
      tr('', a.name, b.name), tr(t.year, U.year(a.year), U.year(b.year)),
      tr(t.price, U.fa(a.price_m), U.fa(b.price_m)), tr(t.diff, '', U.fa(Math.abs(a.price_m - b.price_m)))])]);
  }
  NK.PAGES.compare = function () {
    var S = NK.S, st = P.state(), page = U.h('div', 'l-page', null, [P.title(T.compare.title)]);
    if (st) { page.append(st); return page; }
    var ids = [S.cmp[0] != null ? S.cmp[0] : S.rows[0].id, S.cmp[1] != null ? S.cmp[1] : S.rows[1] ? S.rows[1].id : S.rows[0].id];
    [0, 1].forEach(function (i) {
      page.append(U.select(P.options(), ids[i], function (v) { S.cmp[i] = v; NK.draw(); }));
    });
    page.append(table(NK.byId(ids[0]), NK.byId(ids[1])), P.note(T.prices.unit + ' · ' + T.disc));
    return page;
  };
})();
