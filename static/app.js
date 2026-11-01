// Theme toggle, tabs (remembered across page reloads), confirm prompts, dismissible alerts.
(function () {
  var root = document.documentElement;
  var saved = localStorage.getItem("sams-theme");
  if (!saved) saved = matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  root.setAttribute("data-theme", saved);

  document.addEventListener("DOMContentLoaded", function () {
    var toggle = document.getElementById("theme-toggle");
    if (toggle) {
      var label = function () { toggle.textContent = root.getAttribute("data-theme") === "dark" ? "Light mode" : "Dark mode"; };
      label();
      toggle.addEventListener("click", function () {
        var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        localStorage.setItem("sams-theme", next);
        label();
      });
    }

    var tabs = document.querySelectorAll(".tab[data-tab]");
    if (tabs.length) {
      var page = location.pathname;
      var show = function (name) {
        var found = false;
        tabs.forEach(function (t) { var on = t.dataset.tab === name; t.classList.toggle("active", on); found = found || on; });
        document.querySelectorAll(".panel").forEach(function (p) { p.classList.toggle("active", p.id === "tab-" + name); });
        return found;
      };
      var start = location.hash.slice(1) || sessionStorage.getItem("tab:" + page) || tabs[0].dataset.tab;
      if (!show(start)) show(tabs[0].dataset.tab);
      tabs.forEach(function (t) {
        t.addEventListener("click", function () { show(t.dataset.tab); sessionStorage.setItem("tab:" + page, t.dataset.tab); history.replaceState(null, "", "#" + t.dataset.tab); });
      });
    }

    document.querySelectorAll("form[data-confirm]").forEach(function (f) {
      f.addEventListener("submit", function (e) { if (!confirm(f.dataset.confirm)) e.preventDefault(); });
    });
    document.querySelectorAll(".flash button").forEach(function (b) {
      b.addEventListener("click", function () { b.parentElement.remove(); });
    });
    document.querySelectorAll("select[data-autosubmit]").forEach(function (s) {
      s.addEventListener("change", function () { s.form.submit(); });
    });
  });
})();
