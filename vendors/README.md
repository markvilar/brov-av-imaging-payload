# Vendors

Third-party vendor documentation — datasheets, manuals, application notes, CAD
models, quotes — kept for reference. Predominantly datasheets, but not limited
to them. Grouped by vendor, the one axis here that is stable regardless of how
the subsystems are decomposed.

PDFs are committed directly to the repo (they are typically small), so the
design record stays self-contained. Name part-specific files with the vendor
part number and, where useful, a revision (e.g.
`alvium-1800-u-500-datasheet-v3.pdf`); documents generic to a product family
keep the vendor's own filename, since there is no part number to key on.

Each vendor directory carries a `README.md` with the vendor's documentation
source URLs and an index of the committed files, giving each document's version
and download date. Vendors revise documents in place and usually serve only the
current version, so that is what ties a local copy back to a retrievable
original.

- `allied-vision/` — camera datasheets and manuals (generic + camera-specific).

Add further vendor/component subdirectories (e.g. LED emitters, connectors,
penetrators, housings) as those vendors are selected.
