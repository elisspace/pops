'use strict';
// The fixed set is deliberately not derived from arbitrary server keys.
window.PopsVisibility = (() => {
  const ids = Object.freeze(['b', 'barn', 'cottage', 'cotton', 'd', 'e', 'firethorn', 'rocksprings-a', 'rocksprings-b', 'shankle']);
  function validate(data) {
    if (!data || !Number.isSafeInteger(data.revision) || data.revision < 0 || !data.visibility || typeof data.visibility !== 'object' || Array.isArray(data.visibility) || ids.some(id => typeof data.visibility[id] !== 'boolean')) {
      throw new Error('The server returned an invalid visibility response.');
    }
    return data;
  }
  async function load() {
    const response = await fetch('/api/visibility', {credentials: 'same-origin', cache: 'no-store', signal: AbortSignal.timeout(12000)});
    if (!response.ok) throw new Error(`Could not load visibility (${response.status}).`);
    return validate(await response.json());
  }
  return Object.freeze({ids, validate, load});
})();

(() => {
  const status = document.getElementById('availability-status');
  if (!status) return;
  const retry = document.getElementById('availability-retry');
  const cards = [...document.querySelectorAll('[data-property]')];
  async function refresh() {
    // Fail closed, including while a retry is in progress.
    cards.forEach(card => { card.hidden = true; });
    retry.hidden = true;
    status.textContent = 'Checking current listings…';
    try {
      const data = await window.PopsVisibility.load();
      let shown = 0;
      cards.forEach(card => {
        card.hidden = data.visibility[card.dataset.property] !== true;
        if (!card.hidden) shown++;
      });
      status.textContent = shown ? `${shown} ${shown === 1 ? 'property is' : 'properties are'} currently listed. Explore the photos below.` : 'No properties are currently listed. You can still open the rental application above.';
    } catch (error) {
      cards.forEach(card => { card.hidden = true; });
      status.textContent = 'Availability temporarily unavailable. Please try again, or use the rental application link above.';
      retry.hidden = false;
    }
  }
  retry.addEventListener('click', refresh);
  refresh();
})();
