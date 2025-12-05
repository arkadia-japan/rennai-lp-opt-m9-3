document.addEventListener('DOMContentLoaded', () => {
  // --- Buildless content loader from ./contents.md ---
  const decodeText = async (resp) => {
    const buf = await resp.arrayBuffer();
    try {
      // Prefer Shift_JIS if available
      const td = new TextDecoder('shift_jis');
      return td.decode(buf);
    } catch (e) {
      return new TextDecoder('utf-8').decode(buf);
    }
  };

  const el = {
    heroTitle: document.querySelector('.hero__title'),
    heroLead: document.querySelector('.hero__lead'),
    md: document.getElementById('md-content'),
    headerCta: document.querySelector('[data-cta="header"]'),
    stickyCta: document.querySelector('[data-cta="sticky"]'),
  };

  const candidatesHero = ['assets/hero.webp','assets/hero.png','assets/hero.jpg','assets/hero.jpeg'];
  const tryHero = () => {
    const root = document.documentElement;
    const apply = (src) => root.style.setProperty('--hero-bg', `url('${src.replace(/'/g,'%27')}')`);
    const load = (i=0) => {
      if (i >= candidatesHero.length) return;
      const img = new Image();
      // Preload hint to improve LCP if hero exists
      const link = document.createElement('link');
      link.rel = 'preload'; link.as = 'image'; link.href = candidatesHero[i];
      document.head.appendChild(link);
      img.onload = () => apply(candidatesHero[i]);
      img.onerror = () => load(i+1);
      img.src = candidatesHero[i];
    };
    load();
  };
  tryHero();

  const htmlEscape = (s) => s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;').replaceAll("'",'&#39;');

  // Build form HTML from spec
  const buildFormHtml = (formId, spec, buttonText) => {
    const emailLabel = 'メールアドレス';
    const nameField = !!(spec && spec.fields && spec.fields.name);
    const nameRequired = !!(spec && spec.fields && spec.fields.name && spec.fields.name.required);
    const consentSpec = spec && spec.consent_checkbox;
    const hiddenFromUrl = (spec && spec.hidden_from_url) || [];
    const endpoint = spec && spec.endpoint ? ` data-endpoint="${spec.endpoint}"` : '';
    const method = spec && spec.method ? ` data-method="${spec.method}"` : '';
    const nameLabel = 'お名前';
    let html = `<form class="lead-form lead-form--lg" id="${formId}"${endpoint}${method}>`;
    if (nameField) {
      html += `<label class="sr-only" for="name-${formId}">${nameLabel}</label>`;
      html += `<input id="name-${formId}" name="name" type="text" inputmode="text" placeholder="${nameLabel}"${nameRequired? ' required':''} />`;
    }
    html += `<label class="sr-only" for="email-${formId}">${emailLabel}</label>`;
    html += `<input id="email-${formId}" name="email" type="email" inputmode="email" enterkeyhint="go" autocomplete="email" autocapitalize="off" autocorrect="off" placeholder="${emailLabel}" required />`;
    if (consentSpec) {
      const cid = consentSpec.id || 'consent';
      const clabel = consentSpec.label || 'プライバシーポリシーに同意します';
      html += `<label class="consent-row"><input id="${cid}-${formId}" name="${cid}" type="checkbox" required /> <span>${htmlEscape(clabel)}</span></label>`;
    }
    hiddenFromUrl.forEach(k => { html += `<input type="hidden" name="${k}" data-from-url="1" />`; });
    html += `<button type="submit" class="btn btn--primary btn--xl" data-cta="dynamic">${htmlEscape(buttonText || '送信')}</button>`;
    html += `</form>`;
    return html;
  };

  const renderMd = (md, spec) => {
    const lines = md.split(/\r?\n/);
    const skip = new Set();
    let heroTitle = '';
    let heroLead = '';
    let globalCtaLabel = '送信';
    // Prefer explicit hero section
    for (let i=0;i<lines.length;i++){
      const line = lines[i];
      if (/^##\s*CTA\d+/.test(line)) continue;
      const mHero = /^##\s*(ヒーロー|ﾋｰﾛｰ|ファーストビュー|ﾌｧｰｽﾄﾋﾞｭｰ|HERO)\b/.exec(line);
      if (mHero){
        for (let j=i+1;j<lines.length;j++){
          const nxt = lines[j];
          if (/^\s*$/.test(nxt)) continue;
          if (/^#/.test(nxt)) break;
          if (!heroTitle){ heroTitle = nxt.trim(); skip.add(j); continue; }
          if (!heroLead){ heroLead = nxt.trim(); skip.add(j); break; }
        }
        skip.add(i);
        break;
      }
    }
    if (!heroTitle){
      for (let i=0;i<lines.length;i++){
        const line = lines[i]; if (/^##\s*CTA\d+/.test(line)) continue;
        const m = /^##\s*(.+)$/.exec(line);
        if (m){ heroTitle = m[1].trim(); skip.add(i); for (let j=i+1;j<lines.length;j++){ const nxt=lines[j]; if (/^\s*$/.test(nxt)) continue; if (/^#/.test(nxt)) break; heroLead = nxt.trim(); skip.add(j); break;} break; }
      }
    }
    if (el.heroTitle) el.heroTitle.textContent = heroTitle;
    if (el.heroLead) el.heroLead.textContent = heroLead;

    // Body build
    let html = '';
    let inList = false;
    let inBenefits = false;
    let inFaq = false;
    let faqCount = 0;
    const closeList = ()=>{ if (inList){ html += '</ul>'; inList=false; } };

    for (let i=0;i<lines.length;i++){
      if (skip.has(i)) continue;
      const line = lines[i];

      // CTA blocks
      const mCta = /^##\s*CTA(\d+)/.exec(line);
      if (mCta){
        closeList(); if (inBenefits){ html+='</div>'; inBenefits=false;} if (inFaq){ html+='</div>'; inFaq=false; }
        const n = mCta[1]; const formId = `lead-form-cta${n}`;
        // Look ahead for button label
        let btnText = null;
        for (let k=i+1;k<lines.length;k++){
          const nxt = lines[k]; if (/^\s*$/.test(nxt)) continue; if (/^#/.test(nxt)) break;
          const mm = /^(CTA|ボタン)\s*[:：]\s*(.+)$/.exec(nxt);
          if (mm){ btnText = mm[2].trim(); skip.add(k); }
          break;
        }
        if (btnText && globalCtaLabel==='送信') globalCtaLabel = btnText;
        html += `<section class="section cta" aria-label="CTA${n}"${i>=lines.length-1? ' id="cta-bottom"':''}>`;
        html += `<div class="container">`;
        html += buildFormHtml(formId, SPEC || {}, btnText);
        html += `</div></section>`;
        continue;
      }

      // Headings
      let m;
      if ((m=/^##\s*(.+)$/.exec(line))){
        if (inBenefits){ html+='</div>'; inBenefits=false; }
        if (inFaq){ html+='</div>'; inFaq=false; }
        closeList();
        const h = m[1].trim();
        html += `<h2 class="section__title">${htmlEscape(h)}</h2>`;
        if (/(実績|ベネフィット|メリット|Benefit|Benefits)/.test(h)){ html += '<div class="benefits">'; inBenefits=true; continue; }
        if (/^(FAQ|よくある質問)$/.test(h)){ html += '<div class="faq">'; inFaq=true; faqCount=0; continue; }
        continue;
      }
      if ((m=/^###\s*(.+)$/.exec(line))){ closeList(); html += `<h3>${htmlEscape(m[1].trim())}</h3>`; continue; }

      // Markdown image (assets only)
      if ((m=/^!\[(.*?)\]\((.*?)\)/.exec(line))){
        const alt = htmlEscape(m[1]||''); let src = m[2].trim();
        if (!/^\.?\/?assets\//.test(src)){ html += '<div class="img-ph" aria-hidden="true"></div>'; }
        else { if (!/^\.\//.test(src)) src = './'+src; html += `<figure class="md-img"><img src="${src}" alt="${alt}" /></figure>`; }
        continue;
      }

      // FAQ Q:
      if (inFaq && (m=/^Q[：:\.．、]\s*(.+)$/.exec(line))){
        const q = htmlEscape(m[1].trim()); faqCount++; const pid = `faq-a-${faqCount}`;
        // collect answer
        let aHtml = '';
        for (let j=i+1;j<lines.length;j++){
          const n = lines[j]; if (/^\s*$/.test(n)){ skip.add(j); break; }
          if (/^#/.test(n) || /^Q[：:\.．、]/.test(n)) break;
          skip.add(j); aHtml += `<p>${htmlEscape(n.trim())}</p>`;
        }
        html += `<div class="faq-item"><button class="faq-q" type="button" data-faq-toggle aria-expanded="false" aria-controls="${pid}">${q} <span class="faq-icon">＋</span></button><div class="faq-a" id="${pid}" hidden>${aHtml}</div></div>`;
        continue;
      }

      // Bullets
      if ((m=/^(\-|\*|・)\s*(.+)$/.exec(line))){
        if (inFaq) closeList();
        if (inBenefits){ html += `<div class="benefit-item"><div class="benefit-bullet"></div><div class="benefit-text">${htmlEscape(m[2].trim())}</div></div>`; continue; }
        if (!inList){ html += '<ul>'; inList=true; }
        html += `<li>${htmlEscape(m[2].trim())}</li>`; continue;
      }

      // Blank
      if (/^\s*$/.test(line)){ closeList(); continue; }

      // Paragraph
      html += `<p>${htmlEscape(line.trim())}</p>`;
    }
    if (inList) html += '</ul>';
    if (inBenefits) html += '</div>';
    if (inFaq) html += '</div>';

    if (el.md) el.md.innerHTML = html;
    // Enhance images for performance
    optimizeImages(el.md);
    // Apply CTA label to header/sticky
    const applyCtaLabel = (t) => { if (t){ if (el.headerCta) el.headerCta.textContent = t; if (el.stickyCta) el.stickyCta.textContent = t; } };
    applyCtaLabel(globalCtaLabel);
  };

  // Optimize images: lazy, decoding, sizes, width/height, srcset when variants exist
  const optimizeImages = (scope=document) => {
    const imgs = Array.from(scope.querySelectorAll('#md-content img'));
    const checkExists = async (url) => {
      try { const r = await fetch(url, { method: 'HEAD', cache: 'force-cache' }); return r.ok; } catch { return false; }
    };
    imgs.forEach(async (img) => {
      img.loading = 'lazy';
      img.decoding = 'async';
      img.setAttribute('fetchpriority','low');
      img.referrerPolicy = 'no-referrer';
      // Sizes suited to our container and breakpoints
      img.sizes = '(max-width: 640px) 100vw, (max-width: 960px) 50vw, 720px';

      // Add width/height to reduce CLS
      const setDims = () => {
        if (img.naturalWidth && img.naturalHeight) {
          if (!img.getAttribute('width')) img.setAttribute('width', String(img.naturalWidth));
          if (!img.getAttribute('height')) img.setAttribute('height', String(img.naturalHeight));
          img.style.aspectRatio = `${img.naturalWidth} / ${img.naturalHeight}`;
        }
      };
      if (img.complete) setDims(); else img.addEventListener('load', setDims, { once: true });

      // Attempt to construct a srcset from naming conventions
      const src = img.getAttribute('src') || '';
      const m = src.match(/^(.*)\.([a-zA-Z0-9]+)$/);
      if (m) {
        const base = m[1], ext = m[2];
        const candidates = [
          { url: `${base}-640w.${ext}`, w: 640 },
          { url: `${base}-960w.${ext}`, w: 960 },
          { url: `${base}-1280w.${ext}`, w: 1280 },
          { url: `${base}-1920w.${ext}`, w: 1920 },
        ];
        const found = [];
        for (const c of candidates) {
          if (await checkExists(c.url)) found.push(`${c.url} ${c.w}w`);
        }
        // @2x device-pixel-ratio variant (e.g., image@2x.jpg)
        const dpr2 = `${base}@2x.${ext}`;
        if (await checkExists(dpr2)) found.push(`${dpr2} 2x`);
        if (found.length) img.srcset = found.join(', ');
      }
    });
  };

  const loadContents = async () => {
    try {
      const resp = await fetch('./contents.md');
      if (!resp.ok) throw new Error('Failed to load contents.md');
      const text = await decodeText(resp);
      renderMd(text, SPEC || {});
      bindForms();
    } catch (e) {
      console.warn('contents.md を読み込めませんでした。HTTP配信でアクセスしてください。', e);
    }
  };

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
  let SPEC = window.FORM_SPEC || null;
  const forms = () => Array.from(document.querySelectorAll('form.lead-form'));

  const fetchFormSpec = async () => {
    if (SPEC) return;
    try {
      const r = await fetch('./form_spec.json', { cache: 'no-store' });
      if (r.ok) SPEC = await r.json();
    } catch (e) { /* ignore */ }
  };

  // Form view when focusing email
  const bindForms = () => forms().forEach(form => {
    const email = form.querySelector('input[type="email"]');
    if (email) {
      email.addEventListener('focus', () => sendEvent('form_view', { form_id: form.id }));
    }
  });

  // Submit
  const attachSubmit = () => forms().forEach(form => {
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
  const prefillHidden = () => forms().forEach(form => {
    Array.from(form.querySelectorAll('input[type="hidden"][data-from-url]')).forEach(inp => {
      const k = inp.name; if (params.get(k)) inp.value = params.get(k);
    });
  });

  // Initialize in buildless mode
  (async () => {
    await fetchFormSpec();
    await loadContents();
    bindForms();
    attachSubmit();
    prefillHidden();
  })();

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
