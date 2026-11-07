'use strict';
(() => {
  const links = [...document.querySelectorAll('a[data-photo]')];
  const dialog = document.querySelector('dialog.lightbox');
  // Native links remain fully functional without JS or native dialog support.
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const image = dialog.querySelector('.viewer-image');
  const count = document.getElementById('photo-count');
  let index = 0;
  let opener = null;
  function show(next) {
    index = (next + links.length) % links.length;
    image.src = links[index].href;
    image.alt = links[index].querySelector('img').alt;
    count.textContent = `Photo ${index + 1} of ${links.length}`;
  }
  links.forEach((link, current) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    show(current);
    dialog.showModal();
  }));
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-prev]').addEventListener('click', () => show(index - 1));
  dialog.querySelector('[data-next]').addEventListener('click', () => show(index + 1));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      show(index + (event.key === 'ArrowLeft' ? -1 : 1));
    }
    // Escape, focus trapping, and focus inertness are native dialog behaviors.
  });
  dialog.addEventListener('close', () => { if (opener) opener.focus(); });
})();
