# Gaultney Management

Hand-authored static HTML, CSS and JavaScript for Mark Gaultney's consulting and rental-property pages. No frontend packages, CDN code, site generator or build step.

- `public/index.html`: consulting homepage and rental link.
- `public/apply/`: rentals, photo galleries, rental application and maintenance form.
- `server/airtable_sync.py`: read-only, periodic Airtable-view synchronizer. No web application server or admin login.
- `ops/`: server configuration and hourly sync units, not a deployment pipeline.

Serve **only `public/`**, never the repository root. The Airtable token and generated availability snapshot stay outside Git. Caddy exposes only the snapshot at `GET /api/visibility`. Existing application/maintenance forms are hosted by Airtable; no extra scripts or libraries are loaded by this site.

See [OPERATIONS.md](OPERATIONS.md) for the direct-pull workflow and security boundary.

## Tests

```sh
python3 -W error::ResourceWarning -m unittest discover -s tests -v
node --check public/assets/gallery.js
node --check public/assets/contact.js
node --check public/assets/visibility.js
```

Tests are development checks, not an automatic deployment requirement. Normal static-site updates are a manual `git pull` on the VPS. Availability changes come from the Airtable view automatically, without a Git pull.

The review branch must not merge into `main` until Eli approves its preview.
