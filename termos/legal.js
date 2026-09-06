// LittleVitor — comportamento compartilhado das páginas legais
document.addEventListener('DOMContentLoaded', function () {
  var tocLinks = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  var sections = tocLinks
    .map(function (link) {
      var id = link.getAttribute('href').replace('#', '');
      return document.getElementById(id);
    })
    .filter(Boolean);

  if ('IntersectionObserver' in window && sections.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var id = entry.target.getAttribute('id');
            tocLinks.forEach(function (link) {
              link.classList.toggle('active', link.getAttribute('href') === '#' + id);
            });
          }
        });
      },
      { rootMargin: '-20% 0px -70% 0px', threshold: 0 }
    );
    sections.forEach(function (section) { observer.observe(section); });
  }

  var toggle = document.querySelector('.toc-mobile-toggle');
  var list = document.querySelector('.toc ol');
  if (toggle && list) {
    toggle.addEventListener('click', function () {
      var isOpen = list.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }
});
