/* Core bootstrapping: load contents.md and form_spec.json, render, wire interactions */
(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const dataLayer = (window.dataLayer = window.dataLayer || []);

  function pushEvent(evt) {
    try { window.dataLayer.push({ ts: Date.now(), ...evt }); } catch(_) {}
    try {
      const { event, ...params } = evt || {};
      if (window.gtag) {
        if (event === 'lp_view') {
          window.gtag('event','page_view', { page_location: location.href, ...params });
        } else if (event === 'form_success') {
          window.gtag('event','generate_lead', params);
        } else if (event === 'cta_click') {
          window.gtag('event','select_content', { content_type:'cta', item_id: params.id });
        } else if (event) {
          window.gtag('event', event, params);
        }
      }
      if (window.fbq) {
        if (event === 'form_success') {
          window.fbq('track','Lead');
        } else if (event === 'lp_view') {
          // PageView already fired on init; also send custom for consistency
          window.fbq('trackCustom','lp_view', params);
        } else if (event) {
          window.fbq('trackCustom', event, params);
        }
      }
    } catch(_) {}
  }

  // RFC 5322 (approx.) email regex (ASCII). Covers quoted local-part and domain-literals.
  const RFC5322_EMAIL = /^(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+))$/i;
  const isValidEmailRFC = (v) => RFC5322_EMAIL.test(String(v || ''));

  // Encoding-robust fetch of Markdown
  async function fetchTextSmart(url) {
    const res = await fetch(url, { cache: 'no-cache' });
    if (!res.ok) throw new Error('Failed to load ' + url);
    const buf = await res.arrayBuffer();
    // Try UTF-8 first
    try {
      const utf8 = new TextDecoder('utf-8', { fatal: true }).decode(buf);
      return utf8;
    } catch(_) {
      // Fallback to Shift_JIS
      try { return new TextDecoder('shift_jis').decode(buf); } catch(e) { return new TextDecoder().decode(buf); }
    }
  }

  async function fetchTextSmartCandidates(paths){
    let lastErr;
    for (const p of paths){
      try { return await fetchTextSmart(p); } catch(e){ lastErr = e; }
    }
    throw lastErr || new Error('Failed to load any candidate: '+paths.join(', '));
  }

  // Minimal Markdown section parser tailored to our conventions
  function parseContents(md) {
    const lines = md.replace(/\r\n?/g, '\n').split('\n');
    const doc = { sections: {}, order: [] };
    let current = null;
    for (const raw of lines) {
      const line = raw.trimEnd();
      if (/^#{2,3} /.test(line)) {
        const level = line.startsWith('###') ? 3 : 2;
        const title = line.replace(/^#{2,3}\s+/, '').trim();
        current = { level, title, lines: [] };
        doc.order.push(title);
        doc.sections[title] = current;
        continue;
      }
      if (current) current.lines.push(raw);
    }
    return doc;
  }

  function getSection(doc, namePrefix) {
    const key = Object.keys(doc.sections).find(k => k.startsWith(namePrefix));
    return key ? doc.sections[key] : null;
  }

  function getSectionByPrefixes(doc, prefixes) {
    for (const p of prefixes) {
      const s = getSection(doc, p);
      if (s) return s;
    }
    return null;
  }

  function linesToParagraphs(lines) {
    const text = lines.join('\n').trim();
    return text.split(/\n{2,}/).map(t => t.trim()).filter(Boolean);
  }

  function linesToList(lines) {
    return lines.map(l => l.trim()).filter(Boolean).map(l => l.replace(/^[-・\*]\s?/, '').trim());
  }

  function createEl(tag, cls, text){ const el = document.createElement(tag); if (cls) el.className = cls; if (text) el.textContent = text; return el; }

  function mountHero(doc){
    const hero = getSection(doc, 'ファーストビュー');
    if (!hero) return;
    // Assume first non-empty line as H1, second as sub, rest as bullets
    const filtered = hero.lines.filter(l => l.trim() !== '');
    const title = filtered[0] || '';
    const sub = filtered[1] || '';
    const bullets = filtered.slice(2).map(l => l.replace(/^[-・\*]\s?/, '').trim()).filter(Boolean);
    $('#hero-title').textContent = title.replace(/^"|"$/g,'');
    $('#hero-sub').textContent = sub;
    const ul = $('#hero-bullets'); ul.innerHTML = '';
    bullets.forEach(b => ul.appendChild(createEl('li','', b)));
  }

  function mountLead(doc){
    const sec = getSection(doc, 'リード文');
    if (!sec) return;
    const h = document.getElementById('lead-title'); if (h) h.textContent = sec.title;
    const pList = linesToParagraphs(sec.lines);
    const mount = $('#lead-text'); mount.innerHTML = '';
    pList.forEach(p => mount.appendChild(createEl('p','',p)));
  }

  function mountBenefits(doc){
    const sec = getSectionByPrefixes(doc, ['実績', '実績ベネフィット', '手段']);
    if (!sec) return;
    const h = document.getElementById('benefits-title'); if (h) h.textContent = sec.title;
    const items = linesToList(sec.lines);
    const ul = $('#benefit-list'); ul.innerHTML = '';
    items.forEach(i => ul.appendChild(createEl('li','', i)));
  }

  function mountLessons(doc){
    const wrap = $('#lessons'); wrap.innerHTML = '';
    // Set H2 from first lesson title to keep semantic hierarchy (visually hidden)
    const firstLessonKey = doc.order.find(k => /^第\d+話/.test(k));
    const h = document.getElementById('curriculum-title'); if (h && firstLessonKey) h.textContent = firstLessonKey;
    doc.order.forEach(key => {
      if (!/^第\d+話/.test(key)) return;
      const sec = doc.sections[key];
      const box = createEl('div','lesson');
      box.appendChild(createEl('h3','', key));
      const ul = createEl('ul','');
      linesToList(sec.lines).forEach(i => ul.appendChild(createEl('li','', i)));
      box.appendChild(ul);
      wrap.appendChild(box);
    });
  }

  function mountProfile(doc){
    const sec = getSection(doc, 'プロフィール');
    if (!sec) return;
    const h = document.getElementById('profile-title'); if (h) h.textContent = sec.title;
    const mount = $('#profile-content'); mount.innerHTML = '';
    linesToParagraphs(sec.lines).forEach(p => mount.appendChild(createEl('p','', p)));
  }

  function mountFAQ(doc){
    const sec = getSection(doc, 'FAQ');
    if (!sec) return;
    const h = document.getElementById('faq-title'); if (h) h.textContent = sec.title;
    const mount = $('#faq-list'); mount.innerHTML = '';
    const lines = sec.lines.map(l => l.trim()).filter(Boolean);
    for (let i=0;i<lines.length;i++){
      const l = lines[i];
      if (/^Q[:：]/.test(l)){
        const q = l.replace(/^Q[:：]\s?/, '');
        const aRaw = (i+1<lines.length && /^A[:：]/.test(lines[i+1])) ? lines[++i] : '';
        const a = aRaw.replace(/^A[:：]\s?/, '');
        const item = createEl('div','faq-item');
        item.appendChild(createEl('div','faq-q','Q. '+q));
        item.appendChild(createEl('div','faq-a', a));
        mount.appendChild(item);
      }
    }
  }

  function extractFormLabels(doc){
    const sec = getSection(doc, 'フォーム');
    const labels = { email:'', name:'', consent:'', button:'' };
    if (!sec) return labels;
    const parseKV = (key) => {
      const m = sec.lines.find(l => l.trim().startsWith(key+':'));
      return m ? m.split(':').slice(1).join(':').trim() : null;
    };
    labels.email = parseKV('メールラベル') || labels.email;
    labels.name = parseKV('名前ラベル') || labels.name;
    labels.consent = parseKV('同意ラベル') || labels.consent;
    labels.button = parseKV('ボタン文言') || labels.button;
    return labels;
  }

  function extractFormMessages(doc){
    const sec = getSection(doc, 'フォーム');
    const msgs = { emailRequired:'', emailFormat:'', consentRequired:'', submitting:'', submitError:'' };
    if (!sec) return msgs;
    const get = (k) => {
      const m = sec.lines.find(l => l.trim().startsWith(k+':'));
      return m ? m.split(':').slice(1).join(':').trim() : '';
    };
    msgs.emailRequired = get('メールエラー必須');
    msgs.emailFormat = get('メールエラー形式');
    msgs.consentRequired = get('同意エラー');
    msgs.submitting = get('送信中');
    msgs.submitError = get('送信失敗汎用');
    return msgs;
  }

  function extractPrivacyURL(doc){
    const sec = getSection(doc, 'フォーム');
    if (!sec) return '';
    const m = sec.lines.find(l => l.trim().startsWith('プライバシーURL:'));
    return m ? m.split(':').slice(1).join(':').trim() : '';
  }

  function extractCTA(doc, name){
    const sec = getSection(doc, name);
    if (!sec) return { label:'', note:'' };
    const lines = sec.lines.map(l => l.trim()).filter(Boolean);
    return { label: lines[0] || '', note: (lines.slice(1).join('\n')) };
  }

  async function loadFormSpec(){
    const tryPaths = ['form_spec.json','../form_spec.json'];
    let lastErr; for (const p of tryPaths){
      try {
        const res = await fetch(p, { cache: 'no-cache' }); if (!res.ok) throw new Error('not ok');
        return await res.json();
      } catch(e){ lastErr = e; }
    }
    throw lastErr || new Error('form_spec.json not found');
  }

  function parseUTM(){
    const params = new URLSearchParams(location.search);
    const obj = {};
    params.forEach((v,k) => obj[k] = v);
    return obj;
  }

  function persistAttribution(hiddenKeys){
    const storeKey = 'lp_attribution_v1';
    const urlParams = parseUTM();
    // Only save if contains any of hiddenKeys
    if (hiddenKeys.some(k => urlParams[k])) {
      localStorage.setItem(storeKey, JSON.stringify({ ts: Date.now(), params: urlParams }));
    }
    const saved = localStorage.getItem(storeKey);
    if (saved) return JSON.parse(saved).params || {};
    return {};
  }

  async function mountForm(doc){
    const mount = $('#form-mount');
    mount.innerHTML = '';
    const labels = extractFormLabels(doc);
    const msgs = extractFormMessages(doc);
    const privacyURL = extractPrivacyURL(doc);
    const spec = await loadFormSpec();
    const fieldsSpec = spec.fields || {};
    const hiddenKeys = Array.isArray(spec.hidden_from_url) ? spec.hidden_from_url : [];
    const attrib = persistAttribution(hiddenKeys);

    const form = createEl('form','lead-form');
    form.setAttribute('novalidate','');
    form.setAttribute('aria-describedby','form-error');
    const formError = createEl('div','error','');
    formError.id = 'form-error';
    formError.setAttribute('role','status');
    formError.setAttribute('aria-live','polite');
    form.appendChild(formError);

    // Dynamic fields based on spec.fields (email, name, and any additional fields)
    const order = [];
    if (fieldsSpec.email) order.push('email');
    if (fieldsSpec.name) order.push('name');
    Object.keys(fieldsSpec).forEach(k => { if (!order.includes(k)) order.push(k); });

    let ie = null; // reference to email input for validation

    const addField = (key, fSpec) => {
      const row = createEl('div','form-row');
      const id = key;
      const labelText = key === 'email' ? (labels.email || 'email') : key === 'name' ? (labels.name || 'name') : key;
      const lab = createEl('label','label', labelText); lab.setAttribute('for', id);
      let input;
      if (fSpec.type === 'checkbox'){
        input = createEl('input',''); input.type='checkbox';
      } else {
        input = createEl('input','input');
        if (fSpec.type === 'email') input.type='email';
        else if (fSpec.type === 'tel') input.type='tel';
        else if (fSpec.type === 'number') input.type='number';
        else input.type='text';
      }
      input.id = id; input.name = key; input.required = Boolean(fSpec.required === true);
      if (key === 'email'){ input.autocomplete='email'; input.inputMode='email'; input.placeholder='you@example.com'; }
      if (key === 'name'){ input.autocomplete='name'; }
      const err = createEl('div','error',''); err.id = `${id}-error`; err.setAttribute('role','status'); err.setAttribute('aria-live','polite');
      input.setAttribute('aria-describedby', err.id);
      row.append(lab, input, err);
      form.appendChild(row);
      return input;
    };

    order.forEach(k => {
      const f = fieldsSpec[k];
      const input = addField(k, f);
      if (k === 'email') ie = input;
    });

    // Consent
    const rc = createEl('div','form-row consent-row');
    const consentId = (spec.consent_checkbox && spec.consent_checkbox.id) ? String(spec.consent_checkbox.id) : 'consent';
    const cb = createEl('input',''); cb.type='checkbox'; cb.id=consentId; cb.name=consentId; cb.required=true;
    const cl = createEl('label',''); cl.setAttribute('for', consentId);
    // Build consent label with optional privacy link
    const spanText = createEl('span','', labels.consent || '');
    cl.appendChild(spanText);
    if (privacyURL){
      cl.appendChild(document.createTextNode(' '));
      const a = createEl('a','', 'プライバシーポリシー');
      a.href = privacyURL; a.target = '_blank'; a.rel = 'noopener noreferrer';
      a.setAttribute('aria-label','プライバシーポリシー（新しいタブで開きます）');
      cl.appendChild(a);
    }
    const errConsent = createEl('div','error',''); errConsent.id = 'consent-error'; errConsent.setAttribute('role','status'); errConsent.setAttribute('aria-live','polite');
    cb.setAttribute('aria-describedby', errConsent.id);
    rc.append(cb, cl, errConsent);
    form.appendChild(rc);

    // Hidden fields for attribution
    hiddenKeys.forEach(k => {
      const h = createEl('input',''); h.type='hidden'; h.name=k; h.value = attrib[k] || '';
      form.appendChild(h);
    });

    // Button
    const rb = createEl('div','form-row');
    const btn = createEl('button','btn btn--primary btn--block', labels.button);
    btn.type='submit';
    rb.appendChild(btn);
    form.appendChild(rb);

    // Validation UX
    function setError(input, message){
      const row = input.closest('.form-row');
      const el = row && row.querySelector('.error');
      if (el) el.textContent = message || '';
      if (message){ input.setAttribute('aria-invalid','true'); }
      else { input.removeAttribute('aria-invalid'); }
    }
    if (ie){
      ['input','blur'].forEach(ev => ie.addEventListener(ev, ()=>{
        if (ie.validity.valueMissing){ setError(ie, msgs.emailRequired); return; }
        if (!isValidEmailRFC(ie.value)){ setError(ie, msgs.emailFormat); return; }
        setError(ie, '');
      }));
      ie.addEventListener('focus', ()=> pushEvent({ event:'input_start', field:'email' }), { once:true });
    }

    let submitting = false;
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (submitting) return;
      submitting = true;
      form.setAttribute('aria-busy','true');
      pushEvent({ event:'form_submit', method: spec.method || 'POST' });
      try { window.dispatchEvent(new CustomEvent('form:submit', { detail: { method: (spec.method || 'POST'), ts: Date.now() }, bubbles: true })); } catch(_) {}
      if (ie){
        if (!ie.value){ setError(ie, msgs.emailRequired); return; }
        if (!isValidEmailRFC(ie.value)){ setError(ie, msgs.emailFormat); return; }
      }
      const consentEl = document.getElementById((spec.consent_checkbox && spec.consent_checkbox.id) ? String(spec.consent_checkbox.id) : 'consent');
      if (!(consentEl && consentEl.checked)){
        const m = msgs.consentRequired || '同意が必要です';
        const el = document.getElementById('consent-error'); if (el) el.textContent = m;
        cb.setAttribute('aria-invalid','true');
        submitting = false; form.removeAttribute('aria-busy');
        return;
      } else { cb.removeAttribute('aria-invalid'); const el = document.getElementById('consent-error'); if (el) el.textContent = ''; }
      btn.disabled = true; if (msgs.submitting) btn.textContent = msgs.submitting;
      try {
        const payload = {};
        const fd = new FormData(form);
        fd.forEach((v,k) => { payload[k] = v; });
        const res = await fetch(spec.endpoint, {
          method: (spec.method || 'POST').toUpperCase(),
          headers: { 'Content-Type':'application/json' },
          body: JSON.stringify(payload),
          mode: 'cors',
          credentials: 'omit'
        });
        if (res.ok){
          pushEvent({ event:'form_success' });
          try { window.dispatchEvent(new CustomEvent('form:success', { detail: { ts: Date.now() }, bubbles: true })); } catch(_) {}
          const to = spec.success_redirect || '/thanks.html';
          location.assign(to);
        } else {
          const msg = (await res.text()) || msgs.submitError;
          pushEvent({ event:'form_error', code: res.status, message: msg });
          try { window.dispatchEvent(new CustomEvent('form:error', { detail: { code: res.status, message: msg, ts: Date.now() }, bubbles: true })); } catch(_) {}
          if (spec.error_behavior === 'inline'){
            if (ie) setError(ie, msg);
            formError.textContent = msg;
          } else { if (msg) alert(msg); }
        }
      } catch(err){
        pushEvent({ event:'form_error', code: 'NETWORK', message: String(err) });
        try { window.dispatchEvent(new CustomEvent('form:error', { detail: { code: 'NETWORK', message: String(err), ts: Date.now() }, bubbles: true })); } catch(_) {}
        if (spec.error_behavior === 'inline'){
          if (ie) setError(ie, msgs.submitError || '');
          formError.textContent = msgs.submitError || '';
        } else if (msgs.submitError) alert(msgs.submitError);
      } finally {
        btn.disabled = false; if (labels.button) btn.textContent = labels.button;
        submitting = false; form.removeAttribute('aria-busy');
      }
    });

    mount.appendChild(form);
  }

  function mountCTAs(doc){
    const c1 = extractCTA(doc, 'CTA1');
    const c2 = extractCTA(doc, 'CTA2');
    const c3 = extractCTA(doc, 'CTA3');
    const sec2 = getSection(doc, 'CTA2'); const h2 = document.getElementById('cta2-title'); if (h2 && sec2) h2.textContent = sec2.title;
    const sec3 = getSection(doc, 'CTA3'); const h3 = document.getElementById('cta3-title'); if (h3 && sec3) h3.textContent = sec3.title;
    const sbtn = $('#sticky-cta-btn');
    const hbtn = $('.header-cta .btn');
    function apply(btn, data){ if (btn) btn.textContent = data.label || ''; }
    apply($('#cta2-btn'), c2); $('#cta2-note').textContent = c2.note || '';
    apply($('#cta3-btn'), c3); $('#cta3-note').textContent = c3.note || '';
    apply(sbtn, c1); apply(hbtn, c1);
    // Click tracking + smooth scroll to primary form
    const toForm = () => { document.getElementById('cta-primary')?.scrollIntoView({ behavior:'smooth', block:'start' }); };
    $$('#cta2 button, #cta3 button, .header-cta .btn, #sticky-cta-btn').forEach(b => {
      b.addEventListener('click', (e) => {
        const id = b.getAttribute('data-cta-id') || 'btn';
        pushEvent({ event:'cta_click', id });
        try { window.dispatchEvent(new CustomEvent('cta:click', { detail: { id, ts: Date.now() }, bubbles: true })); } catch(_) {}
        e.preventDefault(); toForm();
      });
    });
  }

  function setupStickyCTA(){
    const sticky = $('#sticky-cta');
    const hero = $('#hero');
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { sticky.style.display = e.isIntersecting ? 'none' : 'block'; });
    }, { threshold: 0.2 });
    io.observe(hero);
  }

  function setupHeroImpression(){
    const hero = $('#hero');
    const io = new IntersectionObserver(entries => {
      if (entries.some(e => e.isIntersecting)){
        pushEvent({ event: 'fv_impression' }); io.disconnect();
      }
    }, { threshold: 0.5 });
    io.observe(hero);
  }

  function setupWebVitals(){
    // LCP
    try {
      const poL = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const last = entries[entries.length-1];
        if (last) pushEvent({ event:'web_vitals', name:'LCP', value: Math.round(last.startTime), id: last.id || '', rating: last.startTime < 2500 ? 'good' : last.startTime < 4000 ? 'needs-improvement' : 'poor' });
      });
      poL.observe({ type:'largest-contentful-paint', buffered:true });
    } catch(_){}
    // CLS
    try {
      let clsValue = 0;
      const poC = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) clsValue += entry.value;
        }
        pushEvent({ event:'web_vitals', name:'CLS', value: Math.round(clsValue*1000)/1000, id:'', rating: clsValue <= 0.1 ? 'good':'needs-improvement' });
      });
      poC.observe({ type:'layout-shift', buffered:true });
    } catch(_){}
  }

  function setupOverlay(){
    const params = new URLSearchParams(location.search);
    const enabled = params.get('overlay') === '1' || params.get('overlay') === 'true';
    if (!enabled) return;
    const src = params.get('overlaySrc') || 'ref/landing.png';
    const root = $('#overlay-root');
    root.classList.add('is-active');
    root.style.backgroundImage = `url('${src.replace(/'/g, '%27')}')`;
    document.addEventListener('keydown', (e)=>{ if (e.key.toLowerCase()==='o') root.classList.toggle('is-active'); });
  }

  function setupLogo(){
    const src = new URLSearchParams(location.search).get('logo');
    const img = document.getElementById('brandLogo');
    if (src){
      img.src = src;
      const alt = new URLSearchParams(location.search).get('logoAlt') || '';
      img.alt = alt;
      if (!alt) img.setAttribute('aria-hidden','true');
    } else {
      img.style.display = 'none';
    }
  }

  // Hero image wiring with srcset/sizes and CLS-safe dimensions.
  function setupHeroMedia(){
    const params = new URLSearchParams(location.search);
    const pEl = document.getElementById('hero-picture');
    const img = document.getElementById('hero-img');
    if (!pEl || !img) return;
    const avif2560 = params.get('hero2560_avif');
    const webp2560 = params.get('hero2560_webp');
    const webp1280 = params.get('hero1280_webp');
    const webp750  = params.get('hero750_webp');
    const jpg1280  = params.get('hero1280_jpg');
    const jpg750   = params.get('hero750_jpg');
    const single   = params.get('hero'); // fallback single image path
    const alt      = params.get('heroAlt') || '';
    const w        = parseInt(params.get('heroW') || '1280', 10);
    const h        = parseInt(params.get('heroH') || '720', 10);

    // If nothing provided, keep hidden.
    if (!(avif2560 || webp2560 || webp1280 || webp750 || jpg1280 || jpg750 || single)) return;

    // Set width/height to lock aspect ratio for CLS.
    if (w > 0 && h > 0) { img.width = w; img.height = h; }
    if (alt) img.alt = alt; else img.alt = '';

    const sAvif = document.getElementById('hero-src-avif');
    const sWebp = document.getElementById('hero-src-webp');
    const sizes = '(max-width: 1024px) 100vw, 1280px';

    // Build srcset strings if sources available.
    const avifSet = [];
    if (avif2560) avifSet.push(`${avif2560} 2560w`);
    if (avifSet.length) { sAvif.srcset = avifSet.join(', '); sAvif.sizes = sizes; }

    const webpSet = [];
    if (webp750)  webpSet.push(`${webp750} 750w`);
    if (webp1280) webpSet.push(`${webp1280} 1280w`);
    if (webp2560) webpSet.push(`${webp2560} 2560w`);
    if (webpSet.length) { sWebp.srcset = webpSet.join(', '); sWebp.sizes = sizes; }

    const jpgSet = [];
    if (jpg750)   jpgSet.push(`${jpg750} 750w`);
    if (jpg1280)  jpgSet.push(`${jpg1280} 1280w`);
    if (jpgSet.length) { img.srcset = jpgSet.join(', '); img.sizes = sizes; }

    // Fallback single src or the 1280 jpg/webp
    img.src = single || webp1280 || jpg1280 || webp750 || jpg750 || webp2560 || avif2560 || '';

    pEl.hidden = false;
  }

  function setDocumentTitle(doc){
    const hero = getSection(doc, 'ファーストビュー');
    if (!hero) return;
    const first = hero.lines.find(l => l.trim());
    if (first) document.title = first.replace(/["#]/g,'').trim();
  }

  function upsertMeta(selector, attr, value){
    let el = document.head.querySelector(selector);
    if (!el){
      el = document.createElement('meta');
      if (selector.startsWith('meta[name="')){
        el.setAttribute('name', selector.match(/meta\[name="([^"]+)"/)[1]);
      } else if (selector.startsWith('meta[property="')){
        el.setAttribute('property', selector.match(/meta\[property="([^"]+)"/)[1]);
      }
      document.head.appendChild(el);
    }
    el.setAttribute(attr, value);
  }

  function applySEO(doc){
    // Title from hero; description from lead first paragraph
    const hero = getSection(doc, 'ファーストビュー');
    const lead = getSection(doc, 'リード文');
    const title = hero && hero.lines.find(l => l.trim()) ? hero.lines.find(l => l.trim()).replace(/["#]/g,'').trim() : document.title;
    const leadParas = lead ? linesToParagraphs(lead.lines) : [];
    let desc = leadParas[0] || '';
    if (desc.length > 160) desc = desc.slice(0, 157) + '…';
    const url = location.origin + location.pathname;
    // Basic
    upsertMeta('meta[name="description"]','content', desc);
    const linkCanonical = document.querySelector('link[rel="canonical"]');
    if (linkCanonical) linkCanonical.setAttribute('href', url);
    // OGP/Twitter
    upsertMeta('meta[property="og:title"]','content', title);
    upsertMeta('meta[property="og:description"]','content', desc);
    upsertMeta('meta[property="og:url"]','content', url);
    upsertMeta('meta[name="twitter:title"]','content', title);
    upsertMeta('meta[name="twitter:description"]','content', desc);
  }

  async function boot(){
    pushEvent({ event:'lp_view', path: location.pathname, utm: parseUTM() });
    setupOverlay();
    setupLogo();
    setupHeroMedia();
    setupStickyCTA();
    setupHeroImpression();
    setupWebVitals();
    try {
      const md = await fetchTextSmartCandidates(['contents.md','../contents.md']);
      const doc = parseContents(md);
      setDocumentTitle(doc);
      applySEO(doc);
      mountHero(doc);
      mountLead(doc);
      mountBenefits(doc);
      mountLessons(doc);
      mountProfile(doc);
      mountFAQ(doc);
      mountCTAs(doc);
      await mountForm(doc);
    } catch(err){
      console.error(err);
      $('#lead-text').textContent = 'コンテンツの読み込みに失敗しました。ファイル形式（UTF-8推奨）をご確認ください。';
    }
  }

  window.addEventListener('DOMContentLoaded', boot);
})();
