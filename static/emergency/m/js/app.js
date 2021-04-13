(function(e) {
  function t(t) { for (var r, o, u = t[0], c = t[1], s = t[2], l = 0, f = []; l < u.length; l++) o = u[l], Object.prototype.hasOwnProperty.call(a, o) && a[o] && f.push(a[o][0]), a[o] = 0; for (r in c) Object.prototype.hasOwnProperty.call(c, r) && (e[r] = c[r]);
    p && p(t); while (f.length) f.shift()(); return i.push.apply(i, s || []), n() }

  function n() { for (var e, t = 0; t < i.length; t++) { for (var n = i[t], r = !0, o = 1; o < n.length; o++) { var u = n[o];
        0 !== a[u] && (r = !1) } r && (i.splice(t--, 1), e = c(c.s = n[0])) } return e } var r = {},
    o = { app: 0 },
    a = { app: 0 },
    i = [];

  function u(e) { return c.p + "static/emergency/m/js/" + ({ about: "about" } [e] || e) + ".js" }

  function c(t) { if (r[t]) return r[t].exports; var n = r[t] = { i: t, l: !1, exports: {} }; return e[t].call(n.exports, n, n.exports, c), n.l = !0, n.exports } c.e = function(e) { var t = [],
      n = { about: 1 };
    o[e] ? t.push(o[e]) : 0 !== o[e] && n[e] && t.push(o[e] = new Promise((function(t, n) { for (var r = "static/emergency/m/css/" + ({ about: "about" } [e] || e) + ".css", a = c.p + r, i = document.getElementsByTagName("link"), u = 0; u < i.length; u++) { var s = i[u],
          l = s.getAttribute("data-href") || s.getAttribute("href"); if ("stylesheet" === s.rel && (l === r || l === a)) return t() } var f = document.getElementsByTagName("style"); for (u = 0; u < f.length; u++) { s = f[u], l = s.getAttribute("data-href"); if (l === r || l === a) return t() } var p = document.createElement("link");
      p.rel = "stylesheet", p.type = "text/css", p.onload = t, p.onerror = function(t) { var r = t && t.target && t.target.src || a,
          i = new Error("Loading CSS chunk " + e + " failed.\n(" + r + ")");
        i.code = "CSS_CHUNK_LOAD_FAILED", i.request = r, delete o[e], p.parentNode.removeChild(p), n(i) }, p.href = a; var d = document.getElementsByTagName("head")[0];
      d.appendChild(p) })).then((function() { o[e] = 0 }))); var r = a[e]; if (0 !== r)
      if (r) t.push(r[2]);
      else { var i = new Promise((function(t, n) { r = a[e] = [t, n] }));
        t.push(r[2] = i); var s, l = document.createElement("script");
        l.charset = "utf-8", l.timeout = 120, c.nc && l.setAttribute("nonce", c.nc), l.src = u(e); var f = new Error;
        s = function(t) { l.onerror = l.onload = null, clearTimeout(p); var n = a[e]; if (0 !== n) { if (n) { var r = t && ("load" === t.type ? "missing" : t.type),
                o = t && t.target && t.target.src;
              f.message = "Loading chunk " + e + " failed.\n(" + r + ": " + o + ")", f.name = "ChunkLoadError", f.type = r, f.request = o, n[1](f) } a[e] = void 0 } }; var p = setTimeout((function() { s({ type: "timeout", target: l }) }), 12e4);
        l.onerror = l.onload = s, document.head.appendChild(l) } return Promise.all(t) }, c.m = e, c.c = r, c.d = function(e, t, n) { c.o(e, t) || Object.defineProperty(e, t, { enumerable: !0, get: n }) }, c.r = function(e) { "undefined" !== typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }), Object.defineProperty(e, "__esModule", { value: !0 }) }, c.t = function(e, t) { if (1 & t && (e = c(e)), 8 & t) return e; if (4 & t && "object" === typeof e && e && e.__esModule) return e; var n = Object.create(null); if (c.r(n), Object.defineProperty(n, "default", { enumerable: !0, value: e }), 2 & t && "string" != typeof e)
      for (var r in e) c.d(n, r, function(t) { return e[t] }.bind(null, r)); return n }, c.n = function(e) { var t = e && e.__esModule ? function() { return e["default"] } : function() { return e }; return c.d(t, "a", t), t }, c.o = function(e, t) { return Object.prototype.hasOwnProperty.call(e, t) }, c.p = "/", c.oe = function(e) { throw console.error(e), e }; var s = window["webpackJsonp"] = window["webpackJsonp"] || [],
    l = s.push.bind(s);
  s.push = t, s = s.slice(); for (var f = 0; f < s.length; f++) t(s[f]); var p = l;
  i.push([0, "chunk-vendors"]), n() })({ 0: function(e, t, n) { e.exports = n("56d7") }, "034f": function(e, t, n) { "use strict";
    n("ee52") }, "56d7": function(e, t, n) { "use strict";
    n.r(t);
    n("c703"), n("ee75"), n("9edd"), n("d3f4"); var r = n("a593"),
      o = function() { var e = this,
          t = e.$createElement,
          n = e._self._c || t; return n("div", { attrs: { id: "app" } }, [n("router-view")], 1) },
      a = [],
      i = (n("034f"), n("c701")),
      u = {},
      c = Object(i["a"])(u, o, a, !1, null, null, null),
      s = c.exports,
      l = n("c730");
    // Object(l["a"])(
    //   "".concat("/static/emergency/m/js/", "service-worker.js"), { ready: function() { console.log("App is being served from cache by a service worker.\nFor more details, visit https://goo.gl/AFskqB") }, registered: function() { console.log("Service worker has been registered.") }, cached: function() { console.log("Content has been cached for offline use.") }, updatefound: function() { console.log("New content is downloading.") }, updated: function() { console.log("New content is available; please refresh.") }, offline: function() { console.log("No internet connection found. App is running in offline mode.") }, error: function(e) { console.error("Error during service worker registration:", e) } }
    //   );
    n("c585"); var f = n("a81e");
    r["a"].use(f["a"]); var p = [{ path: "/", name: "Home", component: function() { return n.e("about").then(n.bind(null, "bb51")) } }, { path: "/about", name: "About", component: function() { return n.e("about").then(n.bind(null, "f820")) } }, { path: "/emergency", name: "emergency", component: function() { return n.e("about").then(n.bind(null, "4757")) }, children: [{ path: "event/:id", name: "event", component: function() { return n.e("about").then(n.bind(null, "3f9c")) } }] }],
      d = new f["a"]({ mode: "hash", routes: p }),
      h = d,
      g = (n("9607"), n("8587")),
      m = n.n(g),
      b = n("db49"),
      v = m.a.create({ baseURL: b.HOST.HTTP, headers: { "Content-Type": "application/json" }, validateStatus: function(e) { return e >= 200 && e < 300 || 304 === e } });
    r["a"].prototype.$axios = v, r["a"].config.productionTip = !1, new r["a"]({ router: h, render: function(e) { return e(s) } }).$mount("#app") }, 9607: function(e, t, n) {}, db49: function(e, t, n) { var r, o, a = {},
      i = {};
    console.log("if process.env.VUE_APP_HOST"), a.HTTP = "/", i.HTTP = "/", r = "./", o = "/static", t.HOST = a, t.PROXY = i, t.publicPath = r, t.assetsDir = o }, ee52: function(e, t, n) {} });
//# sourceMappingURL=app.js.map