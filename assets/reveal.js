// Staggered page-load reveal — runs once, then hands off to IntersectionObserver for late content.
(function () {
  const onReady = (fn) => {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  };

  onReady(() => {
    // Wrap each split-line child for masking effect
    document.querySelectorAll('.split-line').forEach((el) => {
      if (!el.dataset.wrapped) {
        el.innerHTML = '<span>' + el.innerHTML + '</span>';
        el.dataset.wrapped = '1';
      }
    });

    // Initial above-the-fold reveals run on a small delay with stagger
    const items = Array.from(document.querySelectorAll('.reveal, .split-line'));
    const inView = items.filter((el) => {
      const r = el.getBoundingClientRect();
      return r.top < window.innerHeight + 80;
    });
    const offscreen = items.filter((el) => !inView.includes(el));

    inView.forEach((el, i) => {
      setTimeout(() => el.classList.add('in'), 80 + i * 55);
    });

    // Scroll-in for the rest
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            io.unobserve(entry.target);
          }
        });
      }, { rootMargin: '0px 0px -10% 0px' });
      offscreen.forEach((el) => io.observe(el));
    } else {
      offscreen.forEach((el) => el.classList.add('in'));
    }

    initTravelLightbox();
  });

  function initTravelLightbox() {
    const images = Array.from(document.querySelectorAll('.article-body img, .a-hero-image img'));
    if (!images.length) return;

    const overlay = document.createElement('div');
    overlay.className = 'lightbox';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Увеличенная фотография');
    overlay.innerHTML = `
      <button class="lightbox__close" type="button" aria-label="Закрыть">×</button>
      <button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Предыдущая фотография">‹</button>
      <figure class="lightbox__figure">
        <img class="lightbox__img" alt="">
        <figcaption class="lightbox__caption"></figcaption>
      </figure>
      <button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Следующая фотография">›</button>
    `;
    document.body.appendChild(overlay);

    const lightboxImg = overlay.querySelector('.lightbox__img');
    const caption = overlay.querySelector('.lightbox__caption');
    const closeBtn = overlay.querySelector('.lightbox__close');
    const prevBtn = overlay.querySelector('.lightbox__nav--prev');
    const nextBtn = overlay.querySelector('.lightbox__nav--next');
    let current = 0;
    let lastFocus = null;

    const setImage = (index) => {
      current = (index + images.length) % images.length;
      const img = images[current];
      const src = img.currentSrc || img.src;
      lightboxImg.src = src;
      lightboxImg.alt = img.alt || '';
      caption.textContent = img.alt ? `${current + 1} / ${images.length} · ${img.alt}` : `${current + 1} / ${images.length}`;
    };

    const open = (index) => {
      lastFocus = document.activeElement;
      setImage(index);
      overlay.classList.add('is-open');
      document.documentElement.classList.add('lightbox-open');
      closeBtn.focus({ preventScroll: true });
    };

    const close = () => {
      overlay.classList.remove('is-open');
      document.documentElement.classList.remove('lightbox-open');
      lightboxImg.removeAttribute('src');
      if (lastFocus && typeof lastFocus.focus === 'function') {
        lastFocus.focus({ preventScroll: true });
      }
    };

    images.forEach((img, index) => {
      img.classList.add('is-lightboxable');
      img.tabIndex = 0;
      img.setAttribute('role', 'button');
      img.setAttribute('aria-label', 'Открыть фотографию крупно');
      img.addEventListener('click', () => open(index));
      img.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open(index);
        }
      });
    });

    closeBtn.addEventListener('click', close);
    prevBtn.addEventListener('click', () => setImage(current - 1));
    nextBtn.addEventListener('click', () => setImage(current + 1));
    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) close();
    });
    document.addEventListener('keydown', (event) => {
      if (!overlay.classList.contains('is-open')) return;
      if (event.key === 'Escape') close();
      if (event.key === 'ArrowLeft') setImage(current - 1);
      if (event.key === 'ArrowRight') setImage(current + 1);
    });
  }
})();
