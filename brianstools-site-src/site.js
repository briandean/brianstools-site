// Brian's Tools — small progressive enhancements; the site works without JS.
(function () {
  // mobile menu
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (btn && nav) btn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });

  // highlight the visitor's OS in the download section and point the hero button at it
  var ua = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || navigator.userAgent || '';
  var os = /win/i.test(ua) ? 'windows' : /mac|iphone|ipad/i.test(ua) ? 'macos' : /linux|x11|cros/i.test(ua) ? 'linux' : null;
  var names = { windows: 'Windows', macos: 'macOS', linux: 'Linux' };
  if (os) {
    var card = document.querySelector('.dl-card[data-os="' + os + '"]');
    var hero = document.getElementById('primary-dl');
    if (card) {
      card.classList.add('is-you');
      if (hero) {
        hero.textContent = 'Download for ' + names[os];
        hero.href = card.querySelector('a.btn').href;
      }
    }
  }

  // details page: highlight the current section in the table of contents
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  if (links.length && 'IntersectionObserver' in window) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting && byId[e.target.id]) {
          links.forEach(function (a) { a.classList.remove('on'); });
          byId[e.target.id].classList.add('on');
        }
      });
    }, { rootMargin: '-90px 0px -70% 0px' });
    Object.keys(byId).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
  }

  // contact form → opens the visitor's mail client (no server involved)
  var form = document.getElementById('contact-form');
  if (form) form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var msg = form.elements.message;
    if (!msg.value.trim()) { msg.classList.add('err'); msg.focus(); return; }
    msg.classList.remove('err');
    var name = form.elements.name.value.trim();
    var subject = "Brian's Tools: " + form.elements.topic.value;
    var body = msg.value + (name ? '\n\n— ' + name : '');
    location.href = 'mailto:__EMAIL__?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
})();
