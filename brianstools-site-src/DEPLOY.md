# brianstools.net — build & deploy

## What's where
- `brianstools-site/` — the finished site. Its *contents* are the root of the GitHub repo **briandean/brianstools-site**.
- `brianstools-site-src/` — the generator (keep it out of the Pages repo). It expects the brand kit folder `brians-tools-brand/` next to it.

## First deploy (GitHub Pages)
1. Create the repo `briandean/brianstools-site` (public).
2. Upload everything inside `brianstools-site/` to the repo root, including the hidden `.nojekyll` and `CNAME` files.
   ```bash
   cd brianstools-site
   git init -b main && git add -A && git commit -m "brianstools.net"
   git remote add origin https://github.com/briandean/brianstools-site.git
   git push -u origin main
   ```
3. Repo → Settings → Pages → Deploy from a branch → `main` / `(root)`. Custom domain: `brianstools.net`.
4. DNS for brianstools.net (at your registrar, e.g. Squarespace Domains):
   - `A` @ → 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
   - `AAAA` @ → 2606:50c0:8000::153, 2606:50c0:8001::153, 2606:50c0:8002::153, 2606:50c0:8003::153 (optional)
   - `CNAME` www → `briandean.github.io`
   - remove the registrar's old `A`/`CNAME` records for `@` and `www`
5. When the certificate is issued, tick **Enforce HTTPS**. Optionally verify the domain under your GitHub account → Settings → Pages.

## Downloads
The buttons link straight to the GitHub release assets on the `pre-release` tag of briandean/brianstools:
`BriansTools_Win.zip`, `BriansTools_Mac.zip`, `BriansTools_Linux.zip`.
To point at a new release, change `REL_BASE` / `RELEASE_PAGE` (or the `DL` entries) in `build_site.py` and rebuild.

## Updating for a new app release
1. Copy `README.md`, `help.md` and `version.py` from the app repo into `brianstools-site-src/`.
2. `pip install markdown-it-py cairosvg fonttools brotli` (once), then `python3 build_site.py`.
   The version, help page, details page and tool links all update from those three files.
3. Commit the regenerated `brianstools-site/` (real screenshots in assets/img/screenshots/ are kept; placeholders are only drawn for missing screenshots).
