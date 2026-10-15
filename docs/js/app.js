(function () {
  // 테마 전환: 저장은 편의 기능이라 실패해도 무시한다.
  const rootEl = document.documentElement;
  try { const t = localStorage.getItem("theme"); if (t) rootEl.dataset.theme = t; } catch (e) {}
  document.getElementById("themeBtn")?.addEventListener("click", () => {
    const dark = rootEl.dataset.theme ? rootEl.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    rootEl.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("theme", rootEl.dataset.theme); } catch (e) {}
  });

  // 목차 현재 위치 표시
  const links = [...document.querySelectorAll("#toc a[href^=\"#\"]")];
  const targets = links.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
  const io = new IntersectionObserver((ents) => {
    ents.forEach((en) => {
      if (!en.isIntersecting) return;
      links.forEach((a) => a.classList.toggle("on", a.getAttribute("href") === "#" + en.target.id));
    });
  }, { rootMargin: "-15% 0px -75% 0px" });
  targets.forEach((t) => io.observe(t));
})();
