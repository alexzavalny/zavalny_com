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
  });
})();

