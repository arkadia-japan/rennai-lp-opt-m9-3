document.addEventListener('DOMContentLoaded', () => {
  // Util: parse UTM params for attribution
  const params = new URLSearchParams(location.search);
  const utm = {
    source: params.get('utm_source') || '',
    medium: params.get('utm_medium') || '',
    campaign: params.get('utm_campaign') || '',
    content: params.get('utm_content') || '',
    term: params.get('utm_term') || ''
  };

  // Year stamp
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  // Measurement helpers
  const sendEvent = (name, params = {}) => {
    const payload = { event: name, event_time: Date.now(), ...params };
    if (window.gtag) {
      // GA4互換の簡易送信（本番タグ差替えで有効化）
      window.gtag('event', name, payload);
    } else if (window.dataLayer) {
      window.dataLayer.push(payload);
    }
    // Debug
    if (location.search.includes('debug=1')) {
      console.debug('[track]', name, payload);
    }
  };

  // Page view
  sendEvent('page_view', { page_location: location.href, ...utm });

  // Scroll depth (25/50/75/100)
  const marks = new Set();
  const onScroll = () => {
    const h = document.documentElement;
    const percent = Math.round(((h.scrollTop + h.clientHeight) / h.scrollHeight) * 100);
    [25,50,75,100].forEach(p => {
      if (percent >= p && !marks.has(p)) {
        marks.add(p);
        sendEvent('scroll_depth', { percent: p });
      }
    });
    if (marks.size === 4) window.removeEventListener('scroll', onScroll);
  };
  window.addEventListener('scroll', onScroll, { passive: true });

  // CTA click tracking
  document.addEventListener('click', (e) => {
    const a = e.target.closest('[data-cta]');
    if (!a) return;
    const pos = a.getAttribute('data-cta') || 'unknown';
    sendEvent('cta_click', { position: pos, ...utm });
  });

  // Forms
  const SPEC = window.FORM_SPEC || null;
  const forms = Array.from(document.querySelectorAll('form.lead-form'));

  // Form view when focusing email
  forms.forEach(form => {
    const email = form.querySelector('input[type="email"]');
    if (email) {
      email.addEventListener('focus', () => sendEvent('form_view', { form_id: form.id }));
    }
  });

  // Submit
  forms.forEach(form => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const email = (fd.get('email') || '').toString().trim();
      // Inline error helper
      const showErr = (msg) => {
        if ((SPEC && SPEC.error_behavior) === 'inline'){
          let n = form.querySelector('.form-error');
          if (!n) { n = document.createElement('div'); n.className = 'form-error'; form.append(n); }
          n.textContent = msg;
        } else { alert(msg); }
      };
      if (!email) { sendEvent('submit_error', { form_id: form.id, reason: 'empty_email' }); return showErr('メールアドレスを入力してください'); }
      // Consent check if present
      const consentEl = form.querySelector('input[type="checkbox"][name]');
      if (consentEl && !consentEl.checked) { sendEvent('submit_error', { form_id: form.id, reason: 'no_consent' }); return showErr('同意が必要です'); }

      sendEvent('form_submit', { form_id: form.id, ...utm });
      // Build payload
      const payload = {};
      fd.forEach((v,k)=>{ payload[k] = v });
      // Hidden-from-url params
      if (SPEC && Array.isArray(SPEC.hidden_from_url)){
        SPEC.hidden_from_url.forEach(k=>{ if (params.get(k)) payload[k] = params.get(k); });
      }
      // Attach UTM too
      Object.assign(payload, utm);

      const endpoint = form.dataset.endpoint || (SPEC && SPEC.endpoint) || '';
      const method = (form.dataset.method || (SPEC && SPEC.method) || 'POST').toUpperCase();
      if (!endpoint) {
        // Fallback demo
        alert('ご登録ありがとうございます！\n確認メールを送信しました。');
        sendEvent('submit_success', { form_id: form.id });
        form.reset();
        return;
      }

      fetch(endpoint, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(async (res)=>{
        if (!res.ok) throw new Error('HTTP '+res.status);
        sendEvent('submit_success', { form_id: form.id });
        const redirect = SPEC && SPEC.success_redirect;
        if (redirect) { location.href = redirect; }
        else { alert('ご登録ありがとうございます！\n確認メールを送信しました。'); form.reset(); }
      }).catch(err=>{
        console.error(err);
        sendEvent('submit_error', { form_id: form.id, reason: 'http_error' });
        showErr('送信に失敗しました。時間をおいて再度お試しください。');
      });
    });
  });

  // Prefill hidden inputs from URL where marked
  forms.forEach(form => {
    Array.from(form.querySelectorAll('input[type="hidden"][data-from-url]')).forEach(inp => {
      const k = inp.name; if (params.get(k)) inp.value = params.get(k);
    });
  });

  // FAQ accordion toggle
  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-faq-toggle]');
    if (!t) return;
    const id = t.getAttribute('aria-controls');
    const panel = id ? document.getElementById(id) : null;
    const expanded = t.getAttribute('aria-expanded') === 'true';
    t.setAttribute('aria-expanded', String(!expanded));
    if (panel) panel.hidden = expanded;
    sendEvent('faq_toggle', { question: t.textContent?.trim().slice(0,120) || '' });
  });

  // ===== Pixel-perfect overlay (design reference) =====
  // Usage: add query params e.g. ?overlay=1&ref=top.png&alpha=0.4&scale=1&blend=difference
  const enableOverlay = params.get('overlay');
  const refPath = params.get('ref'); // e.g. ref/top.png
  if (enableOverlay && refPath) {
    const img = new Image();
    img.src = refPath;
    img.alt = '';
    img.setAttribute('aria-hidden','true');
    img.className = 'design-overlay';
    document.documentElement.style.setProperty('--overlay-alpha', params.get('alpha') || '.4');
    document.documentElement.style.setProperty('--overlay-scale', params.get('scale') || '1');
    document.documentElement.style.setProperty('--overlay-blend', params.get('blend') || 'normal');

    const panel = document.createElement('div');
    panel.className = 'debug-panel visible';
    panel.innerHTML = `
      <label style="font-size:12px;color:#111">Overlay</label>
      <input id="dbg-alpha" type="range" min="0" max="1" step="0.05" value="${Number(params.get('alpha')||0.4)}" />
      <input id="dbg-scale" type="number" step="0.01" min="0.1" value="${Number(params.get('scale')||1)}" style="width:64px" />
      <select id="dbg-blend">
        <option value="normal">normal</option>
        <option value="multiply">multiply</option>
        <option value="screen">screen</option>
        <option value="overlay">overlay</option>
        <option value="difference">difference</option>
        <option value="exclusion">exclusion</option>
      </select>
      <button id="dbg-toggle" type="button" class="btn btn--sm">ON/OFF</button>
    `;
    document.body.append(panel);
    document.body.append(img);

    // init blend
    const blendSel = panel.querySelector('#dbg-blend');
    blendSel.value = params.get('blend') || 'normal';

    // Controls
    panel.querySelector('#dbg-alpha').addEventListener('input', (e)=>{
      const v = e.target.value;
      document.documentElement.style.setProperty('--overlay-alpha', String(v));
    });
    panel.querySelector('#dbg-scale').addEventListener('input', (e)=>{
      const v = e.target.value || '1';
      document.documentElement.style.setProperty('--overlay-scale', String(v));
    });
    blendSel.addEventListener('change', (e)=>{
      const v = e.target.value || 'normal';
      document.documentElement.style.setProperty('--overlay-blend', String(v));
    });
    panel.querySelector('#dbg-toggle').addEventListener('click', ()=>{
      img.style.display = (img.style.display === 'none') ? 'block' : 'none';
    });

    // Keyboard shortcuts
    window.addEventListener('keydown', (e)=>{
      if (e.key === '[' || e.key === ']'){
        const cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--overlay-alpha')) || 0.4;
        const next = Math.min(1, Math.max(0, cur + (e.key === ']' ? 0.05 : -0.05)));
        document.documentElement.style.setProperty('--overlay-alpha', String(next));
        const slider = panel.querySelector('#dbg-alpha');
        slider.value = String(next);
      }
      if (e.key === '-' || e.key === '+'){
        const cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--overlay-scale')) || 1;
        const next = Math.max(0.1, cur + (e.key === '+' ? 0.01 : -0.01));
        document.documentElement.style.setProperty('--overlay-scale', String(next.toFixed(2)));
        const input = panel.querySelector('#dbg-scale');
        input.value = String(next.toFixed(2));
      }
      if (e.key.toLowerCase() === 'o'){
        img.style.display = (img.style.display === 'none') ? 'block' : 'none';
      }
    });
  }
});
