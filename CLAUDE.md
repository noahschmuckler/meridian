# Meridian — Claude Code Context

## What this is
Clinical decision-support tool for controlled substances prescribing. Static site on Cloudflare Pages. All logic in `index-rendered.html` (single-file app with inline CSS/JS). Content in `modules/*.json`.

## Architecture
- **No backend** — everything runs client-side in the browser
- **Content pipeline**: Word (DOCX) → upload via mammoth.js → JSON → webapp / PDF / PPTX
- **CDN deps**: PptxGenJS 3.12.0, Mammoth.js 1.8.0 (both with SRI hashes)
- **Fonts**: IBM Plex Sans/Mono via Google Fonts
- **Mobile-first**: 480px max-width constraint

## Key files
- `index-rendered.html` — the entire app (~3700 lines: CSS + HTML + JS inline)
- `modules/index.json` — module registry
- `modules/*.json` — clinical content (adhd, benzos, opiates, ckd, anemia)
- `templates/*.docx` — pre-generated Word templates
- `presentations/*.pptx` — pre-generated PowerPoint decks
- `_headers` — Cloudflare Pages security headers (CSP, X-Frame-Options, etc.)
- `manifest.json` — PWA manifest

## Deployment
- **Production**: https://meridian-3x6.pages.dev/index-rendered.html
- **Deploy**: `npx wrangler pages deploy . --project-name=meridian --branch=main --commit-dirty=true`
- **Preview**: `npx wrangler pages deploy . --project-name=meridian --branch=<name> --commit-dirty=true`
- **Preview URL**: `https://<branch-name>.meridian-3x6.pages.dev`
- **GitHub**: noahschmuckler/meridian

## Production readiness status (2026-04-05)
### Done
- Fetch error handling with graceful partial load
- SRI integrity hashes on CDN scripts
- DOCX upload HTML sanitization (script/style/event handler stripping)
- CSP + security headers via `_headers`
- Accessibility: ARIA roles, keyboard support on checkboxes and accordions
- Global error handler (window.error + unhandledrejection)
- PWA manifest start_url fix

### Remaining
- Clinical content peer review (second clinician)
- Cross-browser testing (iPhone Safari, Android Chrome, iPad, Windows Edge)
- Playwright smoke tests
- Deploy script with safety checks
- Module version display in JSON + footer
