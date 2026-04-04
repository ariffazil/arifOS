/* arifOS Theory Portal JS */

// ── Theme Toggle ──────────────────────────────────────────
(function () {
  const html = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  let theme = html.getAttribute('data-theme') || 'dark';

  function applyTheme(t) {
    theme = t;
    html.setAttribute('data-theme', t);
    if (toggle) {
      toggle.setAttribute('aria-label', `Switch to ${t === 'dark' ? 'light' : 'dark'} mode`);
      toggle.innerHTML = t === 'dark'
        ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }
  }

  if (toggle) {
    toggle.addEventListener('click', () => applyTheme(theme === 'dark' ? 'light' : 'dark'));
  }
  applyTheme(theme);
})();

// ── Live Health Status ────────────────────────────────────
async function checkStatus() {
  const tickerStatus = document.getElementById('tickerStatus');
  const heroDot = document.getElementById('heroStatusDot');
  const heroText = document.getElementById('heroStatusText');

  try {
    const res = await fetch('https://arifosmcp.arif-fazil.com/health', {
      method: 'GET',
      mode: 'cors',
      cache: 'no-store',
      signal: AbortSignal.timeout(5000)
    });
    if (!res.ok) throw new Error();
    const data = await res.json();

    if (tickerStatus) tickerStatus.textContent = 'LIVE';
    if (heroDot) { heroDot.className = 'endpoint-status-dot live'; }
    if (heroText) heroText.textContent = `STATUS: ${(data.status || 'HEALTHY').toUpperCase()}`;
  } catch (e) {
    if (tickerStatus) tickerStatus.textContent = 'CHECK /health';
    if (heroDot) heroDot.className = 'endpoint-status-dot';
    if (heroText) heroText.textContent = 'STATUS: SEE /health';
  }
}

checkStatus();
setInterval(checkStatus, 30000);

// ── Card entrance animations ──────────────────────────────
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0, rootMargin: '0px 0px -5% 0px' });

document.querySelectorAll(
  '.pillar, .theory-card, .e-card, .eco-card, .floor-row'
).forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = `opacity 0.5s ease ${i * 0.05}s, transform 0.5s ease ${i * 0.05}s, border-color 180ms cubic-bezier(0.16,1,0.3,1)`;
  observer.observe(el);
});

// ── Trinity layer hover accent ────────────────────────────
document.querySelectorAll('.trinity-layer').forEach(layer => {
  layer.addEventListener('mouseenter', () => {
    layer.style.borderColor = 'var(--color-gold)';
  });
  layer.addEventListener('mouseleave', () => {
    layer.style.borderColor = '';
  });
});

// ── Nav active section highlight ─────────────────────────
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link:not(.nav-cta)');

const navObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      navLinks.forEach(link => {
        link.style.color = link.getAttribute('href') === `#${e.target.id}`
          ? 'var(--color-gold)' : '';
      });
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });

sections.forEach(s => navObserver.observe(s));
