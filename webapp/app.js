// Mini-app shell: hash routing, bottom menu, placeholder pages.
(function () {
  "use strict";
  var T = window.TEXTS;
  var tg = window.Telegram && window.Telegram.WebApp;
  var main = document.getElementById("main");
  var nav = document.getElementById("nav");

  function make(tag, text, cls) {
    var node = document.createElement(tag);
    if (text) { node.textContent = text; }
    if (cls) { node.className = cls; }
    return node;
  }

  function currentKey() {
    var key = location.hash.replace("#", "");
    for (var i = 0; i < T.menu.length; i++) {
      if (T.menu[i][0] === key) { return key; }
    }
    return T.menu[0][0];
  }

  function labelOf(key) {
    for (var i = 0; i < T.menu.length; i++) {
      if (T.menu[i][0] === key) { return T.menu[i][1]; }
    }
    return "";
  }

  function renderNav(active) {
    nav.textContent = "";
    T.menu.forEach(function (item) {
      var link = make("a", item[1], item[0] === active ? "tab on" : "tab");
      link.href = "#" + item[0];
      nav.appendChild(link);
    });
  }

  function renderPage(key) {
    main.textContent = "";
    main.appendChild(make("h2", labelOf(key)));
    main.appendChild(make("p", T.soon, "muted"));
  }

  function show() {
    var key = currentKey();
    renderNav(key);
    renderPage(key);
    window.scrollTo(0, 0);
  }

  document.title = T.title;
  document.getElementById("title").textContent = T.title;
  window.addEventListener("hashchange", show);
  if (tg) { tg.ready(); tg.expand(); }
  show();
})();
