# Self-hosted fonts (currently not in use — see Rubric E.1)

This was the original plan: keep the site off third-party font CDNs
(Rubric A.9 / Core Web Vitals) by self-hosting Barlow Condensed and Inter.
The `.woff2` files were never actually added, so `base.css` was silently
firing two 404 font requests on every page load in production. As of the
Step 3 refactor, the `@font-face` rules have been removed and
`--font-heading` / `--font-body` name the system font stack directly —
that's the real, currently-shipping typography, not a fallback.

To restore true Barlow Condensed / Inter branding:

1. Download the two free, open-license families from Google Fonts
   (`google-webfonts-helper` can export the exact `.woff2` files needed):
   - **Barlow Condensed**, weight 700 (Bold) → save as `BarlowCondensed-Bold.woff2`
   - **Inter**, weight 400 (Regular) → save as `Inter-Regular.woff2`
2. Drop both files in this directory.
3. Re-add the two `@font-face` blocks in `static/css/base.css` and point
   `--font-heading` / `--font-body` back at `"Barlow Condensed"` / `"Inter"`
   with the system stack as their fallback.
