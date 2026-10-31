// Tab 5: more (future features, about, theme).
(function () {
  var U = NK.U, T = NK.T, P = NK.P;
  function toggleTheme() {
    var r = document.documentElement;
    var dark = matchMedia('(prefers-color-scheme: dark)').matches;
    var cur = r.dataset.theme || (dark ? 'dark' : 'light');
    r.dataset.theme = cur === 'dark' ? 'light' : 'dark';
  }
  NK.PAGES.more = function () {
    var items = T.more.items.map(function (t) { return U.h('div', 'c-row c-row--dim', t); });
    var theme = U.on(U.h('button', 'c-btn c-btn--ghost', T.more.theme), toggleTheme);
    return U.h('div', 'l-page', null, [P.title(T.more.title)].concat(items, [theme]));
  };
})();
