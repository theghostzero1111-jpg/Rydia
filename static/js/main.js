/* ============================================================
   Site interactions: navbar, mobile menu, counters,
   scroll-reveal, service pre-select.
   ============================================================ */
(function () {
  'use strict';

  // ---- Sticky navbar ----
  var navbar = document.getElementById('navbar');
  function onScroll() {
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 40);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ---- Mobile menu ----
  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('open');
    });
    links.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('open');
      });
    });
  }

  // ---- Animated stat counters ----
  function animateCount(el) {
    var target = parseFloat(el.getAttribute('data-count') || el.getAttribute('data-decimal') || '0');
    var isDecimal = el.hasAttribute('data-decimal');
    var duration = 1600;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = target * eased;
      el.textContent = isDecimal
        ? value.toFixed(1)
        : Math.round(value).toLocaleString();
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // ---- Scroll reveal + counters via IntersectionObserver ----
  var revealTargets = document.querySelectorAll(
    '.service-card, .testimonial-card, .order-form, .order-card, .contact-form, .about-text, .about-image-wrap'
  );
  revealTargets.forEach(function (el) { el.classList.add('reveal'); });

  var counted = false;
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('visible');
      if (!counted && entry.target.classList.contains('stat-number')) {
        counted = true;
        document.querySelectorAll('.stat-number').forEach(animateCount);
      }
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.15 });

  revealTargets.forEach(function (el) { observer.observe(el); });
  document.querySelectorAll('.stat-number').forEach(function (el) { observer.observe(el); });

  // ---- Pre-select a service from service-card "Order this" links ----
  var serviceSelect = document.getElementById('service');
  document.querySelectorAll('.service-link').forEach(function (link) {
    link.addEventListener('click', function () {
      var key = link.getAttribute('data-service');
      if (serviceSelect && key) serviceSelect.value = key;
    });
  });
})();
