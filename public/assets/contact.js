'use strict';
(() => {
  const form = document.getElementById('contact-form');
  if (!form) return;
  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = new FormData(form);
    const body = `Name: ${data.get('name').trim()}\nEmail: ${data.get('email').trim()}\n\n${data.get('body').trim()}`;
    window.location.href = `mailto:mark@gaultneymanagement.com?subject=${encodeURIComponent(data.get('subject').trim())}&body=${encodeURIComponent(body)}`;
  });
})();
