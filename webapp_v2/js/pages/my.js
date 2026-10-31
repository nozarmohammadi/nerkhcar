// Tab 4: saved cars (memory only for now; server storage comes later).
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  NK.PAGES.my = function () {
    var S = NK.S, page = U.h('div', 'l-page', null, [P.title(T.my.title)]);
    var cars = S.my.map(NK.byId).filter(Boolean);
    if (!cars.length) {
      page.append(P.empty(T.my.empty, T.my.hint, T.my.go, function () { NK.go('prices'); }));
      return page;
    }
    cars.forEach(function (d) { page.append(P.row(d)); });
    return page;
  };
})();
