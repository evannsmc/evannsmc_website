---
name: publish-with-push-script
description: Publish evannsmc.com changes with ./push (full quarto render, then commit+push), not a partial render + manual git push
metadata:
  type: feedback
---

Publish site changes by running `./push -m "<descriptive message>"` from the repo root instead of rendering one page and pushing with git by hand.

**Why:** The user wants the whole site built before every push. `./push` runs a full `quarto render` into `docs/` (served by GitHub Pages at www.evannsmc.com), then `git add -A`, commit, push. Rendering a single `.qmd` can leave other generated files (search.json, listings, sitemap) stale.

**How to apply:** After editing sources, run `./push -m "..."` instead of `quarto render <file>` + `git commit`/`git push`. Because it does `git add -A`, check `git status` first so nothing unintended is staged. After pushing, confirm the GitHub Pages build (`gh api repos/evannsmc/evannsmc_website/pages/builds/latest`) and the live URL on www.evannsmc.com.
