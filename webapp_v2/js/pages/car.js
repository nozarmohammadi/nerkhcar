// Inner page of tab 1: one car.
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  function toggleSave(id) {
    var my = NK.S.my, i = my.indexOf(id);
    if (i === -1) my.push(id); else my.splice(i, 1);
    NK.draw();
  }
  NK.PAGES.car = function () {
    var S = NK.S, d = NK.byId(S.carId);
    if (!d) return NK.PAGES.prices();
    var saved = S.my.indexOf(d.id) !== -1;
    var back = U.on(U.h('button', 'c-link', T.car.back), function () { NK.go('prices'); });
    var tags = U.h('div', 'c-chips', null, [U.h('span', 'c-chip', T.car.fresh), U.h('span', 'c-chip', T.prices.noChange)]);
    var save = U.on(U.h('button', 'c-btn', saved ? T.car.saved : T.car.save), function () { toggleSave(d.id); });
    var cmp = U.on(U.h('button', 'c-btn c-btn--ghost', T.car.compare), function () { S.cmp[0] = d.id; NK.go('compare'); });
    return U.h('div', 'l-page', null, [back, P.title(d.name), P.note(P.sub(d)), P.price(d, true), tags,
      P.empty(T.car.chartSoon), save, cmp, P.note(T.disc)]);
  };
})();
