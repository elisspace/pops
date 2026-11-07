# Pops: direct Git hosting

## Intended workflow

- Canonical editable checkout on Ito: `/home/eli/git/pops`.
- Upstream: `git@github.com:elisspace/pops.git` (currently public; never commit credentials).
- Gitea: `ssh://git@git.dontoucha.us:2222/codex-admin/pops.git`, read-only pull mirror of GitHub, normally every eight hours.
- Review branch: `feat/static-rentals-preview`. Do **not merge until Eli approves** the `https://pops.elis.space/` preview.
- HHI checkout target: `/srv/platform/migration-managed/pops-repo`.
- Caddy serves only its `public/` subdirectory. `.git`, Python service code, tests and ops files are outside the public root.
- Once wired, `cd /srv/platform/migration-managed/pops-repo && git pull --ff-only` updates static pages. No builder, publish hook, timer or deploy command.
- Public rental page: `/apply/`; application: `/apply/app.html`; maintenance: `/apply/maintenance.html`.
- `gaultneymanagement.com` stays on its current migrated static copy until a separate approved production cutover. Preview replaces the older `pops.elis.space` only.

## Visibility administration

- `/admin/` is protected by Caddy's established bcrypt Basic Authentication over HTTPS. Save its long random password in a password manager; browsers display the native login prompt. There is no self-registration or reset endpoint.
- The only mutation is a boolean visibility flag for one fixed property ID. No editing HTML, URLs, paths, commands or arbitrary content.
- Public `GET /api/visibility`; protected `PUT /api/admin/visibility` additionally requires the exact configured Origin, JSON content type, custom request header, strict schema and current revision.
- Visibility controls the available-properties listing, **not confidentiality of photos or direct property links**. Photos remain public; no applicant/private documents belong in this repository.
- A private Unix socket links Caddy to the restricted Python standard-library service, `platform-pops-visibility.service`. The service cannot write the source checkout or server config.
- Persistent state: `/srv/platform/migration-managed/pops-private/state`, outside Git. Pulls never replace Dad's selections.
- Credential hash include: `/srv/platform/migration-managed/pops-private/admin-users.caddy`, outside Git and publicly served roots. Plaintext handoff is private and not part of source.
- Static HTML/CSS/JS edits appear on pull. Changes to the small Python server require `systemctl restart platform-pops-visibility`; this is not needed for photos, text, layout or visibility changes.
- No new frontend libraries, remote fonts or CDN code. Existing Airtable-hosted application and maintenance forms remain an external service, embedded without its JavaScript helper and with direct fallback links. No form submissions are generated during testing.

## Recovery and backup

The existing authenticated HHI daily backup captured `2026-11-07T03:20:04Z` covers both old served sites and Caddy configuration; exact receipt binding and archive members were checked before maintenance. Use regular backups, not additional retained tree copies. The new checkout, credential hash and visibility state stay under `migration-managed`, included by the current HHI backup adapter; the service uses the captured `platform-` unit naming convention. New data is protected when the next regular capture completes, not retroactively by the pre-change backup.

## Current checkpoint

Static frontend and Unix-socket backend are implemented on the review branch. Parent verification: 25 Python tests pass; four JavaScript syntax checks pass; credential-pattern scan has no findings. A local integration using the VPS's exact Caddy 2.6.2 binary and a disposable trusted test certificate proved unauthenticated admin/API rejection, authenticated save/public readback/restore, cross-origin write rejection, and source/Git path denial. Browser checks confirmed the two default listings, mobile layout and photo dialog. Test servers were stopped. Independent review found no concrete security vulnerability and one queued-read failure-handling defect; the defect was reproduced by a failing regression and fixed, with the full suite passing. Additional Caddy tests rejected all tested encoded/repeated-slash/dot-segment admin variants anonymously. VPS read-only deploy key generated on HHI; Gitea enrollment is pending authenticated access. No public route changed yet. No merge approved.
