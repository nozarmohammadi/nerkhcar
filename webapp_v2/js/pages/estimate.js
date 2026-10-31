// Tab 3: estimate form. Result is a range only, never a reference number.
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  function result(res) {
    if (!res) return U.h('i');
    if (res === 'error') return P.empty(T.state.error);
    var range = U.fa(res.low) + ' – ' + U.fa(res.high);
    return U.h('div', 'c-result', null, [U.h('span', 'c-note', T.estimate.result),
      U.h('b', 'c-price__num', range), U.h('span', 'c-price__unit', T.prices.unit), P.note(T.disc)]);
  }
  async function submit(e) {
    try { e.res = await NK.api.estimate({ trim_id: e.id, km: +e.km || 0, cond: +e.cond }); }
    catch (err) { e.res = 'error'; }
    NK.draw();
  }
  NK.PAGES.estimate = function () {
    var e = NK.S.est, st = P.state(), page = U.h('div', 'l-page', null, [P.title(T.estimate.title)]);
    if (st) { page.append(st); return page; }
    if (e.id == null) e.id = NK.S.rows[0].id;
    var km = U.h('input', 'c-input');
    km.type = 'number'; km.value = e.km;
    km.addEventListener('input', function () { e.km = km.value; });
    var conds = T.estimate.conds.map(function (c, i) { return { v: i, l: c }; });
    var form = U.h('div', 'c-form', null, [U.h('label', 'c-label', T.estimate.car),
      U.select(P.options(), e.id, function (v) { e.id = v; }), U.h('label', 'c-label', T.estimate.km), km,
      U.h('label', 'c-label', T.estimate.cond), U.select(conds, e.cond, function (v) { e.cond = v; }),
      U.on(U.h('button', 'c-btn', T.estimate.go), function () { submit(e); })]);
    page.append(form, result(e.res));
    return page;
  };
})();
