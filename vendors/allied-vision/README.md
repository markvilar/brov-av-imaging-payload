# Allied Vision

Documentation for the Alvium MIPI CSI-2 camera family and the Jetson adapter
boards. Only the documents we actually reference are committed here; anything
else can be fetched from the sources below.

## Sources

- [Alvium CSI-2 documentation](https://www.alliedvision.com/en/support/camera-documentation/area-scan-cameras-documentation/alvium-csi-2-documentation)
  — user guides, features and register references, and the camera-specific
  datasheets. This is where the PDFs below came from.
- [Alvium STEP file downloads](https://www.alliedvision.com/en/support/camera-documentation/area-scan-cameras-documentation/alvium-step-file-downloads)
  — CAD models, configured per camera by module, mount, and housing. Needed for
  the pressure-housing and lens-port mechanical fit.

Allied Vision revises these documents in place and the portal serves only the
current version, so the version and download date below are what make the local
copies auditable — an older revision is generally not retrievable from the site.

## Committed documents

| File | Document | Version | Downloaded |
| --- | --- | --- | --- |
| `alvium-csi2-user-guide.pdf` | Alvium CSI-2 Cameras User Guide | V4.2.0 (2026-Apr-23) | 2026-07-16 |
| `alvium-csi2-register-controls-reference.pdf` | Alvium MIPI CSI-2 Cameras Direct Register Access Controls Reference | V2.6.0 (2026-Apr-23) | 2026-07-16 |
| `alvium-features-reference.pdf` | Alvium Features Reference | V3.6.0 (2026-May-20) | 2026-07-16 |
| `jetson-adapter-22558-user-guide.pdf` | Adapter Board for NVIDIA Jetson Nano and Jetson Xavier NX Developer Kit User Guide (part 22558) | V1.1.4 (2025-Jul-11) | 2026-07-16 |

All four are generic to the Alvium family rather than tied to one part number.
Camera-specific datasheets and STEP files get added once the sensor and mount
are selected.

When adding a document, record its version and download date in the table above;
both are on the PDF cover page.
