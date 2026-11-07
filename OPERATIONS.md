# Pops: direct Git hosting

## Source and manual updates

- Editable checkout on Ito: `/home/eli/git/pops`.
- Upstream: `git@github.com:elisspace/pops.git` (public; never commit credentials).
- Gitea: `ssh://git@git.dontoucha.us:2222/codex-admin/pops.git`, read-only GitHub pull mirror, normally every eight hours.
- Review branch: `feat/static-rentals-preview`. **Do not merge until Eli approves** the `https://pops.elis.space/` preview.
- HHI checkout: `/srv/platform/migration-managed/pops-repo`; Caddy serves only `public/`.
- Static page/photo updates: `cd /srv/platform/migration-managed/pops-repo && git pull`. Fast-forward only; no build, deploy command or validation gate. The repository-scoped read-only deploy key stays on HHI under `pops-private/git/`.
- Preview root redirects to `/apply/`; Dad's profile is `/index.html`; footer links use this root-relative path.
- Application: `/apply/app.html`; maintenance: `/apply/maintenance.html`. Existing Airtable form destinations remain unchanged.
- `gaultneymanagement.com` remains on its previous migrated static copy until a separately approved production cutover.

## Availability: Airtable is authoritative

The exact view is https://airtable.com/appSUPtDVGlCyTitK/tblxo4bMBslwsHb6F/viwAl6iMsxqvAxg8w?blocks=hide . A mapped unit present in that view is visible as available; an absent unit is hidden. View membership is authoritative, rather than interpreting another status independently.

`server/airtable_sync.py` makes read-only requests, paginates and validates the complete result, and atomically publishes only `{revision, visibility}`. Fixed record IDs map to the ten existing property pages; no Airtable text, notes, applicant data or record IDs reach the public JSON. Renaming a unit does not break its mapping. A valid empty view hides all units. An unknown record entering the view causes sync failure rather than silently losing a property; add its explicit page mapping after review.

- Scheduler: `platform-pops-airtable-sync.timer`, hourly with up to 30 seconds of jitter and persistent catch-up. Hourly polling limits ordinary single-page API use to roughly one request per hour, rather than high-frequency polling that can exhaust a small Airtable plan.
- Worker: `platform-pops-airtable-sync.service`, a hardened unprivileged oneshot; **no listening socket, public mutation API, password or login**.
- Token source: `/srv/platform/migration-managed/pops-private/airtable-token`, root-owned mode `0600`, outside Git and served roots. systemd `LoadCredential` supplies a private per-execution copy. Caddy must not be able to read it. Use a PAT with only `data.records:read` and access restricted to this base; the synchronizer never sends writes.
- Snapshot: `/srv/platform/migration-managed/pops-private/availability/visibility.json`. The worker can write only this dedicated directory; Caddy can read it.
- Caddy exposes the **exact** `/api/visibility` route for GET/HEAD only and disables caching. Other API paths return 404. The site has no reverse proxy, admin page, authentication middleware or admin JavaScript.
- On a network, HTTP, validation or mapping failure, leave the last successful snapshot in place. The failed systemd execution is visible in the journal; there is no automatic email/Signal alert. The next hourly execution retries. After a prolonged outage the displayed list can therefore be stale; it is not falsely refreshed on failed requests.
- Inspect: `systemctl status platform-pops-airtable-sync.timer`, `systemctl status platform-pops-airtable-sync.service`, `journalctl -u platform-pops-airtable-sync.service`.
- Immediate refresh after an Airtable change: `systemctl start platform-pops-airtable-sync.service` on HHI.
- Git pulls never overwrite the token or generated snapshot. Sync source changes are used on its next execution; no backend restart is needed. Service/timer/Caddy template changes still require explicit operational installation, not merely a Git pull.

Hidden listing status is not confidentiality: direct property pages and photos remain public. No private applicant data belongs in the repository. Frontend remains library-free and the existing forms use only Airtable-hosted embeds and direct fallback links.

## Removed administration

The previous `/admin/` page, its JavaScript, mutable visibility server, Unix socket service and Basic Auth configuration are removed. Retired live login hashes and plaintext handoff are deleted after successful cutover. Historical regular backups and Git history remain unchanged; the old password no longer authenticates any route.

## Recovery

Use the existing authenticated HHI regular backup and its actual capture/coverage receipt, not extra retained rollback archives. The checkout, private configuration/state and Caddy configuration are under `migration-managed`; `platform-` service/timer definitions are covered by the existing adapter. The normal backup was refreshed before this cutover: capture `2026-11-07T16:42:06Z`, authenticated `trusted-signature` receipt, with actual archive members verified for predecessor source, Caddy route/include, old service, visibility state and authentication hash. New Airtable credentials/snapshot receive protection with the next regular capture, not retroactively. Keep only sanitized cutover evidence under `pops-private`; transient transaction preimages are removed after verification.
