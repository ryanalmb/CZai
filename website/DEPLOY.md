# Deploying the CZ.AI Website (Static)

This `website/` folder contains a lightweight static site (HTML/CSS) for CZ.AI — bilingual (EN + 简体中文), optimistic, and clearly “Launching on BNB Chain”.

Free hosting options
- Render Static Site: connect your repo, set root directory to `website/`, build command: none, publish directory: `website/`.
- GitHub Pages: host from `website/` using a GitHub Action or by moving files to a `/docs` folder.
- Cloudflare Pages: new project → connect repo → set `Build command` empty, `Output directory` to `website`.

Recommended structure
- `index.html`: Landing page (features, use cases, BNB Chain positioning)
- `about.html`: About CZ.AI
- `terms.html`: Terms of Use
- `privacy.html`: Privacy Policy
- `styles.css`: Site styling
- `assets/`: Logo, favicon, social image (og.png placeholder)

Notes
- Replace `assets/og.png` with a real social card image (1200×630 recommended).
- Update copy as needed; all text is non‑technical and user‑friendly.
- This site is static, so it’s easy to cache and fast to load.
