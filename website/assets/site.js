const pages = [
  ["Home","index.html","home"],["Platform","platform.html","platform"],["Research","research.html","research"],
  ["Evidence","evidence.html","evidence"],["AI & MCP","ai.html","ai"],["Docs","docs.html","docs"],["Roadmap","roadmap.html","roadmap"]
];
const current = document.body.dataset.page || "home";
const nav = pages.map(([label,url,key]) => `<a href="${url}" ${current===key?'aria-current="page"':''}>${label}</a>`).join("");
document.getElementById("site-header").innerHTML = `
<header class="topbar"><div class="wrap nav-wrap"><a class="brand" href="index.html"><span class='brand-mark brand-mark-logo'><img src='assets/quantlab-logo.png' alt='QuantLab logo'></span><span>QUANTLAB<small>RESEARCH SYSTEMS</small></span></a>
<button class="menu-toggle" aria-label="Toggle navigation" aria-expanded="false">☰</button><nav class="nav">${nav}</nav><a class="nav-cta" href="https://github.com/Khem00/QuantLab-Public" target="_blank" rel="noopener">GitHub ↗</a></div></header>`;
document.getElementById("site-footer").innerHTML = `
<footer class="footer"><div class="wrap footer-main"><div><a class="brand" href="index.html"><span class="brand-mark">Q<span>·</span></span><span>QUANTLAB<small>RESEARCH SYSTEMS</small></span></a><p>Evidence-first quantitative research.<br>Reproducible by design. Qualified by evidence.</p></div><div class="footer-links"><div><b>EXPLORE</b><a href="platform.html">Platform</a><a href="research.html">Research</a><a href="evidence.html">Evidence</a></div><div><b>RESOURCES</b><a href="ai.html">AI & MCP</a><a href="docs.html">Documentation</a><a href="roadmap.html">Roadmap</a></div><div><b>PROJECT</b><a href="https://github.com/Khem00/QuantLab-Public" target="_blank" rel="noopener">GitHub ↗</a><a href="https://quantlab-reproduction-mcp.onrender.com" target="_blank" rel="noopener">MCP companion ↗</a></div></div></div><div class="wrap footer-bottom"><span>© <span id="year"></span> QuantLab</span><span>Historical research is not a guarantee of future results. Not investment advice.</span><a href="roadmap.html">Scope & limitations</a></div></footer>`;
document.getElementById("year").textContent = new Date().getFullYear();
const toggle = document.querySelector(".menu-toggle");
toggle?.addEventListener("click",()=>{const open=document.querySelector(".nav").classList.toggle("open");toggle.setAttribute("aria-expanded",String(open));});


// QuantLab custom cursor — desktop only, with accessible fallbacks.
(() => {
  if (window.matchMedia("(pointer: coarse)").matches ||
      window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const ring = document.createElement("div");
  const dot = document.createElement("div");
  ring.className = "ql-cursor";
  dot.className = "ql-cursor-dot";
  document.body.append(ring, dot);

  let x = innerWidth / 2, y = innerHeight / 2;
  let rx = x, ry = y, dx = x, dy = y;
  let active = false;

  document.addEventListener("mousemove", e => {
    x = e.clientX;
    y = e.clientY;
    if (!active) {
      active = true;
      document.body.classList.add("ql-cursor-active");
    }
  });

  document.addEventListener("mouseover", e => {
    ring.classList.toggle(
      "is-hovered",
      !!e.target.closest("a, button, [role='button'], input, select, textarea")
    );
  });

  function animate() {
    rx += (x - rx) * 0.15;
    ry += (y - ry) * 0.15;
    dx += (x - dx) * 0.35;
    dy += (y - dy) * 0.35;
    ring.style.transform = `translate(${rx}px,${ry}px) translate(-50%,-50%)`;
    dot.style.transform = `translate(${dx}px,${dy}px) translate(-50%,-50%)`;
    requestAnimationFrame(animate);
  }

  animate();
})();
