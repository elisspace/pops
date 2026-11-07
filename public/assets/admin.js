'use strict';
(() => {
  const status = document.getElementById('admin-status');
  const refreshButton = document.getElementById('admin-refresh');
  const buttons = [...document.querySelectorAll('button[data-property]')];
  let saved = null;
  let busy = false;
  const labels = new Map(buttons.map(button => [button.dataset.property, button.closest('li').querySelector('h2').textContent]));
  function render() {
    buttons.forEach(button => {
      const id = button.dataset.property;
      const visible = saved ? saved.visibility[id] : false;
      button.disabled = busy || !saved;
      button.setAttribute('aria-pressed', String(visible));
      button.textContent = saved ? `${labels.get(id)}: ${visible ? 'Shown — click to hide' : 'Hidden — click to show'}` : `${labels.get(id)}: Not loaded`;
    });
    refreshButton.disabled = busy;
  }
  async function refresh() {
    if (busy) return;
    busy = true;
    saved = null;
    render();
    status.textContent = 'Loading saved visibility…';
    try {
      saved = await window.PopsVisibility.load();
      status.textContent = `Saved visibility loaded (revision ${saved.revision}). Select a property to show or hide it.`;
    } catch (error) {
      status.textContent = 'Could not load saved visibility. Check your connection and browser authentication, then select Refresh saved visibility. No changes were made.';
    } finally {
      busy = false;
      render();
    }
  }
  async function toggle(id) {
    if (busy || !saved || !window.PopsVisibility.ids.includes(id)) return;
    busy = true;
    const desired = !saved.visibility[id];
    render();
    status.textContent = `Saving ${labels.get(id)}…`;
    try {
      const response = await fetch('/api/admin/visibility', {
        method: 'PUT',
        credentials: 'same-origin',
        cache: 'no-store',
        headers: {'Content-Type': 'application/json', 'X-Pops-Admin': '1'},
        body: JSON.stringify({revision: saved.revision, property: id, visible: desired}),
        signal: AbortSignal.timeout(12000)
      });
      if (response.status === 409) {
        // Never automatically replay a stale user's write against a new revision.
        saved = null;
        try {
          saved = await window.PopsVisibility.load();
          status.textContent = 'Another change was saved first. The latest settings are now shown. Review them and click the property again to retry your change. Your earlier change was not saved.';
        } catch (error) {
          status.textContent = 'Another change was saved first. Could not refresh the latest settings. Select Refresh saved visibility, review the settings, then retry. Your earlier change was not saved.';
        }
        return;
      }
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After');
        const guidance = retryAfter && /^\d+$/.test(retryAfter)
          ? `Wait ${retryAfter} seconds. `
          : retryAfter ? `Wait until ${retryAfter}. ` : 'Wait a minute before trying again. ';
        status.textContent = `Too many changes. ${guidance}Select Refresh saved visibility before retrying. Your change was not saved.`;
        saved = null;
        return;
      }
      if (!response.ok) throw new Error(`Save failed (${response.status}).`);
      const accepted = window.PopsVisibility.validate(await response.json());
      // Read back the target before claiming that it is saved.
      const confirmed = await window.PopsVisibility.load();
      saved = confirmed;
      if (confirmed.revision !== accepted.revision || confirmed.visibility[id] !== desired) {
        status.textContent = 'The server accepted your change, but settings changed again before verification. The latest settings are shown. Review them before making another change.';
      } else {
        status.textContent = `Saved and verified: ${labels.get(id)} is ${desired ? 'shown' : 'hidden'} (revision ${confirmed.revision}).`;
      }
    } catch (error) {
      // A lost response may follow a successful write, so do not claim failure or retry blindly.
      saved = null;
      status.textContent = 'Unable to confirm the saved setting. Check your connection or browser authentication, then select Refresh saved visibility before trying again. The change may have reached the server.';
    } finally {
      busy = false;
      render();
    }
  }
  buttons.forEach(button => button.addEventListener('click', () => toggle(button.dataset.property)));
  refreshButton.addEventListener('click', refresh);
  refresh();
})();
