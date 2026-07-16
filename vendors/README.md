# Vendors

Third-party vendor documentation — datasheets, manuals, application notes, CAD
models, quotes — kept for reference. Predominantly datasheets, but not limited
to them. Grouped by vendor, the one axis here that is stable regardless of how
the subsystems are decomposed.

PDFs are committed directly to the repo (they are typically small), so the
design record stays self-contained.

Name files `<product-scope>-<document-kind>.pdf`, lowercase kebab-case, with the
product scope first so a listing groups a family together — e.g.
`alvium-csi2-user-guide.pdf`, `alvium-1800-c-500-datasheet.pdf`,
`jetson-adapter-22558-user-guide.pdf`. The scope is whatever the document
actually covers: a product family, or a part number where the document is
specific to one. Hyphens separate tokens, so drop them from within a token
(`csi2`, not `csi-2`).

Leave the document version out of the filename. Decisions, trade studies, and
issues cite these paths, and a version in the name breaks every citation on each
revision and turns an update into a delete-plus-add in git rather than a
modification. The per-vendor README records the version instead, and the file's
git history is then its revision history.

Each vendor directory carries a `README.md` with the vendor's documentation
source URLs and an index of the committed files, giving each document's version
and download date. Vendors revise documents in place and usually serve only the
current version, so that is what ties a local copy back to a retrievable
original.

- `allied-vision/` — camera datasheets and manuals (generic + camera-specific).

Add further vendor/component subdirectories (e.g. LED emitters, connectors,
penetrators, housings) as those vendors are selected.
