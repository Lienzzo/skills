/* Enmascara datos personales en la pestaña antes de capturar el «antes» (skill ux-top-tier).
   Solo cambia lo que se ve en esta pestaña: no guarda nada en el servidor y al recargar vuelve todo.

   Uso (en Claude in Chrome, con javascript_tool): pega este archivo entero y después llama a
     uxMask({ blur: ['td:nth-child(2)', '.avatar', 'img[alt*="foto"]'], text: ['Juan Pérez', 'Calle Mayor 3'] })
   - Siempre: correos, teléfonos, IBAN, tarjetas y DNI/NIE en textos y campos.
   - blur: selectores de lo que identifica a alguien (columna de nombres, avatares, direcciones).
   - text: nombres u otros textos concretos que aparezcan sueltos; se cambian por «Persona 1», «Persona 2»…
   Se vuelve a aplicar sola si la app repinta la página. Mira siempre la captura: si algo se escapa,
   añádelo a blur o text y vuelve a capturar. */
(() => {
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE']);
  const phone = (m) => {
    const digits = m.replace(/\D/g, '').length;
    if (digits < 9 || digits > 15 || /^\s*\d{4}-\d{2}-\d{2}/.test(m)) return m;
    return m.replace(/\d/g, '0');
  };
  const RULES = [
    [/[\w.+-]+@[\w-]+(?:\.[\w-]+)+/g, () => 'correo@ejemplo.com'],
    [/\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,4})?\b/g, () => 'ES00 0000 0000 0000 0000'],
    [/\b(?:\d[ -]?){12,18}\d\b/g, () => '0000 0000 0000 0000'],
    [/\b[XYZxyz]?\d{7,8}[- ]?[A-Za-z]\b/g, () => '00000000X'],
    [/(?:\+\d{1,3}[\s.-]?)?\(?\d{2,4}\)?(?:[\s.-]?\d{2,4}){2,4}/g, phone]
  ];
  const fake = new Map();

  function maskString(s, names) {
    let out = s;
    names.forEach((name) => {
      if (!name || !out.includes(name)) return;
      if (!fake.has(name)) fake.set(name, 'Persona ' + (fake.size + 1));
      out = out.split(name).join(fake.get(name));
    });
    RULES.forEach(([re, fn]) => { out = out.replace(re, fn); });
    return out;
  }

  function apply(opts) {
    let changed = 0;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      if (!n.parentElement || SKIP.has(n.parentElement.tagName) || !n.nodeValue.trim()) continue;
      const v = maskString(n.nodeValue, opts.text);
      if (v !== n.nodeValue) { n.nodeValue = v; changed++; }
    }
    document.querySelectorAll('input, textarea').forEach((el) => {
      if (!el.value) return;
      const v = maskString(el.value, opts.text);
      if (v !== el.value) { el.value = v; changed++; }
    });
    return changed;
  }

  window.uxMask = function uxMask(options) {
    const opts = { blur: [], text: [], ...options };
    let style = document.getElementById('ux-mask-style');
    if (!style) {
      style = document.createElement('style');
      style.id = 'ux-mask-style';
      document.head.appendChild(style);
    }
    style.textContent = opts.blur.length ? opts.blur.join(',') + '{filter:blur(5px) !important}' : '';
    if (window.__uxMaskObserver) window.__uxMaskObserver.disconnect();
    const changed = apply(opts);
    let queued = false;
    const observer = new MutationObserver(() => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { queued = false; apply(opts); });
    });
    observer.observe(document.body, { subtree: true, childList: true, characterData: true });
    window.__uxMaskObserver = observer;
    return { textos: changed, difuminados: opts.blur.length ? document.querySelectorAll(opts.blur.join(',')).length : 0, nombres: fake.size };
  };
})();
