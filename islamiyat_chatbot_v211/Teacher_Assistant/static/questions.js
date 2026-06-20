/* ═══════════════════════════════════════════════════════
   ISLAMIYAT QUESTION BANK — questions.js
   UI Render Functions ONLY — Data served from Python API
   400 Questions | Class 1-12 | Pakistani Curriculum
═══════════════════════════════════════════════════════ */

let QUESTIONS    = [];
let CLASS_GROUPS = [];
let activeFilter  = 'all';
let searchQuery   = '';

/* ═══════════════════════════════════════════════════════
   INIT — Fetch data from Python backend
═══════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {
  await loadData();
  renderQuestions();
  setupSearch();
  setupFilters();
  setupBackToTop();
  animateStats();
});

async function loadData() {
  try {
    const [qRes, gRes] = await Promise.all([
      fetch('/api/questions'),
      fetch('/api/questions/groups')
    ]);
    const qData = await qRes.json();
    const gData = await gRes.json();
    QUESTIONS    = qData.questions  || [];
    CLASS_GROUPS = gData.groups     || [];
  } catch (e) {
    console.error('Failed to load question bank from Python API:', e);
  }
}

/* ═══════════════════════════════════════════════════════
   RENDER
═══════════════════════════════════════════════════════ */
function renderQuestions() {
  const grid      = document.getElementById('questions-grid');
  const noResults = document.getElementById('no-results');
  const countEl   = document.getElementById('result-count');

  let filtered = QUESTIONS.filter(q => {
    const matchClass  = activeFilter === 'all' || q.classGroup === activeFilter;
    const matchSearch = !searchQuery ||
      q.q.toLowerCase().includes(searchQuery) ||
      q.a.toLowerCase().includes(searchQuery);
    return matchClass && matchSearch;
  });

  countEl.textContent = filtered.length === QUESTIONS.length
    ? `${QUESTIONS.length} sawaal mil gaye`
    : `${filtered.length} sawaal mile`;

  if (filtered.length === 0) {
    grid.innerHTML = '';
    noResults.style.display      = 'flex';
    noResults.style.flexDirection = 'column';
    noResults.style.alignItems   = 'center';
    return;
  }
  noResults.style.display = 'none';

  const groups = activeFilter === 'all'
    ? CLASS_GROUPS
    : CLASS_GROUPS.filter(g => g.key === activeFilter);

  let html = '';
  for (const group of groups) {
    const groupQuestions = filtered.filter(q => q.classGroup === group.key);
    if (groupQuestions.length === 0) continue;

    html += `
      <div class="class-group-header" data-group="${group.key}">
        <div class="class-group-icon ${group.color}">${group.icon}</div>
        <div class="class-group-info">
          <h2>${group.label}</h2>
          <p>${group.desc}</p>
        </div>
        <span class="class-group-count">${groupQuestions.length} sawaal</span>
      </div>`;

    for (const q of groupQuestions) {
      const qText = highlight(escapeHtml(q.q), searchQuery);
      const aText = highlight(escapeHtml(q.a), searchQuery);
      html += `
        <div class="q-card ${q.color}" id="qcard-${q.id}" role="article" aria-label="Question ${q.id}">
          <div class="q-card-header">
            <span class="q-num ${q.color}">Q${q.id}</span>
            <button class="q-copy-btn" id="copy-btn-${q.id}" onclick="copyQuestion(${q.id})" title="Copy karo" aria-label="Copy Question ${q.id}">
              <i class="fa-regular fa-copy"></i>
            </button>
          </div>
          <p class="q-question">${qText}</p>
          <div class="q-divider"></div>
          <div class="q-answer-label"><i class="fa-solid fa-circle-check"></i> Jawab</div>
          <p class="q-answer">${aText}</p>
        </div>`;
    }
  }

  grid.innerHTML = html;

  requestAnimationFrame(() => {
    const cards = grid.querySelectorAll('.q-card');
    cards.forEach((card, i) => {
      card.style.opacity    = '0';
      card.style.transform  = 'translateY(20px)';
      card.style.transition = `opacity 0.35s ease ${i * 0.02}s, transform 0.35s ease ${i * 0.02}s`;
      requestAnimationFrame(() => {
        card.style.opacity   = '1';
        card.style.transform = 'translateY(0)';
      });
    });
  });
}

/* ═══════════════════════════════════════════════════════
   HELPERS
═══════════════════════════════════════════════════════ */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function highlight(text, query) {
  if (!query) return text;
  const re = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  return text.replace(re, '<mark>$1</mark>');
}

function copyQuestion(id) {
  const q = QUESTIONS.find(x => x.id === id);
  if (!q) return;
  const txt = `Q${q.id}. ${q.q}\nA: ${q.a}`;
  navigator.clipboard.writeText(txt).then(() => {
    const btn = document.getElementById(`copy-btn-${id}`);
    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.innerHTML = '<i class="fa-regular fa-copy"></i>';
      btn.classList.remove('copied');
    }, 2000);
  }).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = txt;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  });
}

/* ═══════════════════════════════════════════════════════
   SEARCH
═══════════════════════════════════════════════════════ */
function setupSearch() {
  const input = document.getElementById('search-input');
  if (!input) return;
  input.addEventListener('input', () => {
    searchQuery = input.value.trim().toLowerCase();
    renderQuestions();
  });
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      input.focus();
      input.select();
    }
    if (e.key === 'Escape' && document.activeElement === input) {
      input.blur();
    }
  });
}

/* ═══════════════════════════════════════════════════════
   FILTERS
═══════════════════════════════════════════════════════ */
function setupFilters() {
  const tabs = document.querySelectorAll('.filter-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeFilter = tab.dataset.class;
      renderQuestions();
      document.getElementById('questions-main').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

/* ═══════════════════════════════════════════════════════
   BACK TO TOP
═══════════════════════════════════════════════════════ */
function setupBackToTop() {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;
  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  });
  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ═══════════════════════════════════════════════════════
   ANIMATED STATS
═══════════════════════════════════════════════════════ */
function animateStats() {
  const nums = document.querySelectorAll('.stat-num');
  nums.forEach(el => {
    const target = parseInt(el.textContent);
    if (isNaN(target)) return;
    let current  = 0;
    const step   = Math.ceil(target / 40);
    const timer  = setInterval(() => {
      current += step;
      if (current >= target) {
        el.textContent = target;
        clearInterval(timer);
      } else {
        el.textContent = current;
      }
    }, 30);
  });
}
