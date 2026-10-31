// Data layer. Read-only API on same origin. initData goes in the Authorization header.
window.NK = window.NK || {};
(function () {
  var useMock = /[?&]mock/.test(location.search);
  function headers() {
    var tg = window.Telegram && Telegram.WebApp;
    var h = { 'Content-Type': 'application/json' };
    if (tg && tg.initData) h.Authorization = 'tma ' + tg.initData;
    return h;
  }
  async function call(path, opts) {
    var r = await fetch(path, Object.assign({ headers: headers(), cache: 'no-store' }, opts));
    if (!r.ok) throw new Error('http ' + r.status);
    return r.json();
  }
  NK.api = {
    prices: function () { return useMock ? Promise.resolve(NK.mock) : call('/api/prices/daily'); },
    estimate: function (body) {
      if (useMock) return Promise.resolve({ low: 900, high: 1000 });
      return call('/api/estimate', { method: 'POST', body: JSON.stringify(body) });
    }
  };
})();
