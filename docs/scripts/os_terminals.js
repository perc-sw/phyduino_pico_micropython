/* Fits tutorial pages to the visitor's computer (styles in ../style/doc_pages.css):
   - terminal windows marked data-os-term, written as Windows PowerShell, are drawn like
     that system's terminal;
   - anything marked data-os-note="win", "mac" or "linux" shows only on that system;
   - a data-os-switch heading becomes a drop-down of the systems, to change it, in place of
     the headings marked data-os-title.
   When the system isn't Windows, macOS or Linux (phones, tablets, ChromeOS), everything stays
   shown and the drop-down asks for one. Without JavaScript everything shows.
   Choosing a system changes the page in place and sets ?os= in the address, so the view
   doesn't move and a reload keeps the choice. ?os=win, ?os=mac or ?os=linux chooses one. */
(function () {
  var names = { win: "Windows", mac: "macOS", linux: "Linux" };
  var looks = {
    win:   { cls: "term-win",   title: "Windows PowerShell" },
    mac:   { cls: "term-mac",   title: "student \u2014 -zsh \u2014 80\u00d724" },
    linux: { cls: "term-linux", title: "student@ubuntu: ~" }
  };

  // The ?os= choice, else the platform the browser reports; null if it's none of the three
  function detect() {
    var forced = new URLSearchParams(window.location.search).get("os");
    if (names[forced]) return forced;
    var ua = navigator.userAgent;
    var platform = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || ua;
    if (/android|iphone|ipad|ipod|cros|chrome os/i.test(ua + " " + platform)) return null;
    if (/win/i.test(platform)) return "win";
    if (/mac/i.test(platform)) return "mac";
    if (/linux|x11/i.test(platform)) return "linux";
    return null;
  }

  // Shell prompt for each look, built from elements (no HTML strings)
  function prompt(os) {
    var span = document.createElement("span");
    span.className = "prompt shell";
    if (os === "linux") {
      var user = document.createElement("span");
      user.className = "user";
      user.textContent = "student@ubuntu";
      var path = document.createElement("span");
      path.className = "path";
      path.textContent = "~";
      span.append(user, ":", path, "$ ");
    } else if (os === "mac") {
      span.textContent = "student@MacBook ~ % ";
    } else {
      span.textContent = "PS C:\\Users\\student> ";
    }
    return span;
  }

  // Shows the page for one system: its notes, its terminals, and no per-section headings
  function show(os) {
    document.querySelectorAll("[data-os-note]").forEach(function (note) {
      note.hidden = note.dataset.osNote !== os;
    });
    document.querySelectorAll("[data-os-title]").forEach(function (title) {
      title.hidden = true;
    });
    var look = looks[os];
    document.querySelectorAll("[data-os-term]").forEach(function (term) {
      Object.keys(looks).forEach(function (key) { term.classList.remove(looks[key].cls); });
      term.classList.add(look.cls);
      term.querySelector(".term-bar").textContent = look.title;
      term.querySelectorAll(".prompt.shell").forEach(function (old) {
        old.replaceWith(prompt(os));
      });
    });
  }

  // A drop-down of the systems with this one chosen, or "Choose your system..." when it
  // couldn't be detected; picking one shows that system's steps
  function fillSwitch(heading, os, selects) {
    var select = document.createElement("select");
    select.setAttribute("aria-label", "Your computer's system");
    if (!os) {
      var blank = document.createElement("option");
      blank.value = "";
      blank.textContent = "Choose your system\u2026";
      select.append(blank);
    }
    Object.keys(names).forEach(function (key) {
      var option = document.createElement("option");
      option.value = key;
      option.textContent = names[key];
      option.selected = key === os;
      select.append(option);
    });
    select.addEventListener("change", function () {
      var key = select.value;
      if (!key) return;
      selects.forEach(function (other) {
        other.value = key;
        var blank = other.querySelector('option[value=""]');
        if (blank) blank.remove();
      });
      var params = new URLSearchParams(window.location.search);
      params.set("os", key);
      history.replaceState(null, "", "?" + params.toString() + window.location.hash);
      show(key);
    });
    heading.append(select);
    selects.push(select);
  }

  var os = detect();
  var selects = [];

  document.querySelectorAll("[data-os-switch]").forEach(function (heading) {
    fillSwitch(heading, os, selects);
    heading.hidden = false;
  });

  if (os) show(os);
})();
