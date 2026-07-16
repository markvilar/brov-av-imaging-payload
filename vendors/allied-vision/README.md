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
| `alvium-1800-c-040-datasheet.pdf` | Alvium 1800 C-040 Datasheet | V1.3.0 (2025-Jun-17) | 2026-07-16 |

The first four are generic to the Alvium family rather than tied to one part
number. The C-040 datasheet is committed as an exception — see below.

When adding a document, record its version and download date in the table above;
both are on the PDF cover page.

## Camera-specific datasheets

The user guide is the primary source for camera specifications and carries a
per-model table for every current model. The datasheets are needed for one thing
it omits entirely: the **EMVA 1288 block** — quantum efficiency, temporal dark
noise, saturation capacity, dynamic range, absolute sensitivity threshold. They
are cited here rather than committed, since only the selected model's datasheet
becomes part of the durable record.

They follow a URL pattern, `<model>` being the number with no separator
(`507`, `2050`, `507_Pol`):

```
https://www.alliedvision.com/assets/support/Camera-Documentation/Allied-Vision/
  Cameras/Alvium/Alvium-CSI2/Data-Sheets/Alvium-1800-C/Alvium_1800_C-<model>_DataSheet_en.pdf
```

Cited by `src/camsel/sensors.py`:

| Model | Version | Notes |
| --- | --- | --- |
| [Alvium 1800 C-040](https://www.alliedvision.com/assets/support/Camera-Documentation/Allied-Vision/Cameras/Alvium/Alvium-CSI2/Data-Sheets/Alvium-1800-C/Alvium_1800_C-040_DataSheet_en.pdf) | V1.3.0 (2025-Jun-17) | **Committed.** States saturation capacity `208000 e⁻`, which is 10× too high — see below. |
| [Alvium 1800 C-507](https://www.alliedvision.com/assets/support/Camera-Documentation/Allied-Vision/Cameras/Alvium/Alvium-CSI2/Data-Sheets/Alvium-1800-C/Alvium_1800_C-507_DataSheet_en.pdf) | V1.3.1 (2025-Jun-17) | Clean. |
| [Alvium 1800 C-2050](https://www.alliedvision.com/assets/support/Camera-Documentation/Allied-Vision/Cameras/Alvium/Alvium-CSI2/Data-Sheets/Alvium-1800-C/Alvium_1800_C-2050_DataSheet_en.pdf) | V1.3.2 (2025-Jun-17) | States resolution `5376 × 3672` where the user guide states `5496 × 3672`. The user guide is taken. |

### Why the C-040 datasheet is committed

Allied Vision revise documents in place and serve only the current version, so a
document we merely *read* can be re-fetched, but a document we make a *claim
about* cannot. `src/camsel/sensors.py` records that the C-040's published
saturation capacity is wrong by a factor of ten. If Allied Vision correct it, the
URL above will serve the corrected figure and the claim becomes unverifiable, so
the copy carrying the error is the only thing that keeps it auditable.
