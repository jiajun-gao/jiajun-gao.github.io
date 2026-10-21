(() => {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const screens = Array.from(document.querySelectorAll('.screen')).map(el => ({ el, eyes: el.querySelector('.eyes') }));
  const face = document.getElementById('jarvis-face');
  const logBody = document.getElementById('log');

  // ---- Moods and the simulated serial log ----
  const MOODS = ['neutral', 'happy', 'curious', 'sleepy', 'alert'];
  const MOOD_LINES = {
    neutral: ['I', 'wake', '"hey jarvis" detected (offline)'],
    happy: ['I', 'tts', '"Nice to meet you!"'],
    curious: ['I', 'asr', '"what are you working on?"'],
    sleepy: ['I', 'idle', 'no wake word for 60 s, dimming face'],
    alert: ['W', 'arbiter', 'cliff sensor tripped, motion vetoed']
  };
  let mood = 'neutral';
  let tick = 4659;

  function addLine(level, tag, msg) {
    if (!logBody) return;
    tick += 300 + Math.floor(Math.random() * 1400);
    const ln = document.createElement('div');
    ln.className = 'ln new' + (level === 'W' ? ' w' : '');
    [['lv', level], ['tk', ` (${tick}) `], ['tag', tag + ':'], ['msg', ' ' + msg]].forEach(([cls, text]) => {
      const span = document.createElement('span');
      span.className = cls;
      span.textContent = text;
      ln.appendChild(span);
    });
    logBody.appendChild(ln);
    while (logBody.children.length > 7) logBody.firstElementChild.remove();
  }

  function setMood(next, withLog = true) {
    mood = next;
    screens.forEach(s => { s.el.dataset.mood = next; });
    if (withLog) addLine(...MOOD_LINES[next]);
  }

  if (face) {
    face.addEventListener('click', () => setMood(MOODS[(MOODS.indexOf(mood) + 1) % MOODS.length]));
  }

  // ---- Eyes follow the pointer ----
  let px = null, py = null, frame = 0, lastMove = 0;

  function look(s, x, y, r) {
    s.eyes.style.setProperty('--tx', x.toFixed(2) + 'px');
    s.eyes.style.setProperty('--ty', y.toFixed(2) + 'px');
  }
  function aim() {
    frame = 0;
    for (const s of screens) {
      const r = s.el.getBoundingClientRect();
      if (!r.width) continue;
      const dx = px - (r.left + r.width / 2);
      const dy = py - (r.top + r.height / 2);
      const d = Math.hypot(dx, dy) || 1;
      const k = d / (d + 180);
      look(s, dx / d * k * r.width * .14, dy / d * k * r.height * .14);
    }
  }
  function queueAim() {
    if (px === null || frame) return;
    frame = requestAnimationFrame(aim);
  }
  function onPointer(e) {
    px = e.clientX;
    py = e.clientY;
    lastMove = performance.now();
    queueAim();
  }
  window.addEventListener('pointermove', onPointer, { passive: true });
  window.addEventListener('pointerdown', onPointer, { passive: true });
  window.addEventListener('scroll', queueAim, { passive: true });

  // When nobody is moving the pointer, glance around now and then
  setInterval(() => {
    if (reduce.matches || document.hidden || performance.now() - lastMove < 4000) return;
    const angle = Math.random() * Math.PI * 2;
    const reach = Math.random() * .9;
    for (const s of screens) {
      const r = s.el.getBoundingClientRect();
      look(s, Math.cos(angle) * reach * r.width * .1, Math.sin(angle) * reach * r.height * .1);
    }
  }, 2600);

  // ---- Blinking ----
  function blink() {
    screens.forEach(s => {
      if (s.el.dataset.mood === 'sleepy') return;
      s.el.classList.add('blink');
      setTimeout(() => s.el.classList.remove('blink'), 120);
    });
  }
  (function scheduleBlink() {
    setTimeout(() => {
      if (!reduce.matches && !document.hidden) {
        blink();
        if (Math.random() < .2) setTimeout(blink, 260);
      }
      scheduleBlink();
    }, 2200 + Math.random() * 3800);
  })();
  if (!reduce.matches) setTimeout(blink, 500);

  // ---- Copy email ----
  document.querySelectorAll('[data-copy]').forEach(btn => {
    const label = btn.textContent;
    let timer = 0;
    const show = text => {
      btn.textContent = text;
      clearTimeout(timer);
      timer = setTimeout(() => { btn.textContent = label; }, 2000);
    };
    const selectTarget = () => {
      const target = document.getElementById(btn.getAttribute('aria-controls'));
      if (!target) return;
      const range = document.createRange();
      range.selectNodeContents(target);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      show('Selected');
    };
    const copied = () => {
      show('Copied');
      const before = mood;
      setMood('happy', false);
      addLine('I', 'mail', 'address copied to clipboard');
      setTimeout(() => setMood(before === 'happy' ? 'neutral' : before, false), 1800);
    };
    btn.addEventListener('click', () => {
      try {
        navigator.clipboard.writeText(btn.dataset.copy).then(copied, selectTarget);
      } catch (err) {
        selectTarget();
      }
    });
  });
})();
