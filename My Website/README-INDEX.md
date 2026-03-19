# Important: which `index.html` is live?

**Netlify (and this repo) deploy from the repository root.** The site serves:

- **`/index.html`** → `Shakespeare-Variorum/index.html` (root)

The file here **`My Website/index.html`** is a **symlink** to `../index.html`.

**Always edit the root `index.html`** at the top level of the project. Changes under `My Website/` that are not the symlink will not match production.
