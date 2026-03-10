(function () {
  var THEMES = [
    { key: "monokai", label: "MNK", name: "Monokai" },
    { key: "vscode", label: "VSC", name: "VSCode" },
    { key: "1c", label: "DSN", name: "Конфигуратор" }
  ];
  var DEFAULT_THEME = THEMES[0].key;
  var STORAGE_KEY = "__code_theme";
  var THEME_PATTERN = /(?:1c|monokai|vscode)\.css$/;

  function getThemeMeta(theme) {
    return THEMES.find(function (item) {
      return item.key === theme;
    }) || THEMES[0];
  }

  function getStoredTheme() {
    var storedTheme;

    if (typeof __md_get === "function") {
      storedTheme = __md_get(STORAGE_KEY);
      if (storedTheme && typeof storedTheme.theme === "string") {
        return getThemeMeta(storedTheme.theme).key;
      }
    }

    return document.documentElement.getAttribute("data-code-theme") || DEFAULT_THEME;
  }

  function setStoredTheme(theme) {
    if (typeof __md_set === "function") {
      __md_set(STORAGE_KEY, { theme: theme });
    }
  }

  function getStylesheet() {
    var stylesheet = document.querySelector("link[data-code-theme-stylesheet]");

    if (!stylesheet) {
      stylesheet = document.querySelector(
        'link[href$="stylesheets/1c.css"], ' +
        'link[href$="stylesheets/monokai.css"], ' +
        'link[href$="stylesheets/vscode.css"]'
      );
    }

    if (stylesheet) {
      stylesheet.setAttribute("data-code-theme-stylesheet", "");
    }

    return stylesheet;
  }

  function syncNativeTooltip(control, description) {
    var tooltipId;
    var tooltip;
    var tooltipInner;

    if (!control) {
      return;
    }

    control.setAttribute("data-code-theme-title", description);
    tooltipId = control.getAttribute("aria-describedby");
    if (!tooltipId) {
      control.setAttribute("title", description);
      return;
    }

    control.removeAttribute("title");

    tooltip = document.getElementById(tooltipId);
    if (!tooltip) {
      return;
    }

    tooltipInner = tooltip.querySelector(".md-tooltip2__inner, .md-tooltip__inner");
    if (tooltipInner) {
      tooltipInner.textContent = description;
    }
  }

  function restoreNativeTooltip(event) {
    var control = event.currentTarget;
    var description = control.getAttribute("data-code-theme-title");

    if (!description) {
      return;
    }

    window.setTimeout(function () {
      control.setAttribute("title", description);
    }, 0);
  }

  function prepareNativeTooltip(event) {
    var control = event.currentTarget;
    var description = control.getAttribute("data-code-theme-title");

    if (!description) {
      return;
    }

    control.setAttribute("title", description);
  }

  function bindNativeTooltip(control) {
    if (!control || control.hasAttribute("data-code-theme-tooltip-bound")) {
      return;
    }

    control.setAttribute("data-code-theme-tooltip-bound", "true");
    control.addEventListener("mouseenter", prepareNativeTooltip);
    control.addEventListener("focusin", prepareNativeTooltip);
    control.addEventListener("mouseleave", restoreNativeTooltip);
    control.addEventListener("focusout", restoreNativeTooltip);
  }

  function updateControl(theme) {
    var control = document.querySelector("[data-code-theme-toggle]");
    var label = document.querySelector("[data-code-theme-label]");
    var currentTheme = getThemeMeta(theme);
    var currentIndex = THEMES.findIndex(function (item) {
      return item.key === currentTheme.key;
    });
    var nextTheme = THEMES[(currentIndex + 1) % THEMES.length];
    var description;

    if (!control || !label) {
      return;
    }

    label.textContent = currentTheme.label;
    description = "Следующая схема подсветки: " + nextTheme.name + " (" + nextTheme.label + ")";
    syncNativeTooltip(control, description);
    control.setAttribute(
      "aria-label",
      "Сменить схему подсветки кода. " + description
    );
  }

  function applyTheme(theme, persist) {
    var themeMeta = getThemeMeta(theme);
    var stylesheet = getStylesheet();

    if (persist === undefined) {
      persist = true;
    }

    document.documentElement.setAttribute("data-code-theme", themeMeta.key);
    if (stylesheet) {
      stylesheet.href = stylesheet.href.replace(THEME_PATTERN, themeMeta.key + ".css");
    }

    if (persist) {
      setStoredTheme(themeMeta.key);
    }

    updateControl(themeMeta.key);
  }

  function cycleTheme() {
    var currentTheme = getThemeMeta(
      document.documentElement.getAttribute("data-code-theme") || DEFAULT_THEME
    );
    var currentIndex = THEMES.findIndex(function (item) {
      return item.key === currentTheme.key;
    });
    var nextTheme = THEMES[(currentIndex + 1) % THEMES.length];

    applyTheme(nextTheme.key);
  }

  function initializeThemeSwitcher() {
    bindNativeTooltip(document.querySelector("[data-code-theme-toggle]"));
    applyTheme(getStoredTheme(), false);
  }

  document.addEventListener("click", function (event) {
    var toggle = event.target.closest("[data-code-theme-toggle]");

    if (!toggle) {
      return;
    }

    event.preventDefault();
    cycleTheme();
  });

  document.addEventListener("DOMContentLoaded", initializeThemeSwitcher);

  if (document.readyState !== "loading") {
    initializeThemeSwitcher();
  }
})();
