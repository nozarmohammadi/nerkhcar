// State, tabs, router, deep links (startapp). Load this file last.
(function () {
  var U = NK.U, T = NK.T, root = document.getElementById('app');
  var S = NK.S = { page: 'prices', carId: null, q: '', brand: '', cmp: [null, null], my: [],
                   status: 'loading', rows: [], src: '', est: { id: null, km: '', cond: 0, res: null } };
  NK.TABS = ['prices', 'compare', 'estimate', 'my', 'more'];
  NK.byId = function (id) { return S.rows.filter(function (r) { return String(r.id) === String(id); })[0]; };
  NK.go = function (p) { S.page = p; NK.draw(); };
  NK.openCar = function (id) { S.carId = id; NK.go('car'); };

  function tabbar() {
    var cur = S.page === 'car' ? 'prices' : S.page, bar = U.h('nav', 'c-tabbar');
    NK.TABS.forEach(function (id) {
      var b = U.h('button', 'c-tab' + (id === cur ? ' c-tab--on' : ''), null, [U.icon(id), U.h('span', null, T.tab[id])]);
      bar.append(U.on(b, function () { NK.go(id); }));
    });
    return bar;
  }
  NK.draw = function () { root.replaceChildren(NK.PAGES[S.page](), tabbar()); };

  // Deep link: car_<id> | cmp_<id>_<id> | est ; optional source after "__" (ch, ig, bot, web).
  function applyLink() {
    var tg = window.Telegram && Telegram.WebApp;
    var raw = (tg && tg.initDataUnsafe && tg.initDataUnsafe.start_param) || location.hash.slice(1);
    var parts = raw.split('__'), p = parts[0].split('_');
    S.src = parts[1] || '';
    if (p[0] === 'car' && NK.byId(p[1])) { S.carId = p[1]; S.page = 'car'; }
    else if (p[0] === 'cmp' && NK.byId(p[1]) && NK.byId(p[2])) { S.cmp = [p[1], p[2]]; S.page = 'compare'; }
    else if (p[0] === 'est') S.page = 'estimate';
  }
  var linked = false;
  NK.load = async function () {
    S.status = 'loading'; NK.draw();
    try {
      var d = await NK.api.prices();
      S.rows = (d.rows || []).map(function (r, i) { return Object.assign({ id: r.trim_id != null ? r.trim_id : i }, r); });
      S.status = d.status || 'ok';
    } catch (e) { S.status = 'error'; }
    if (!linked) { applyLink(); linked = true; }
    NK.draw();
  };
  (function init() {
    var tg = window.Telegram && Telegram.WebApp;
    if (tg) { tg.ready(); tg.expand(); if (tg.colorScheme) document.documentElement.dataset.theme = tg.colorScheme; }
    document.title = T.app;
    NK.load();
  })();
})();
