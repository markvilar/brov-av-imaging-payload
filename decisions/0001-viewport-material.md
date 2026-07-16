# 0001 — Viewport material

**Status:** Accepted (2026-07-16)

## Context

The camera housing needs an optical viewport between the sensor and the water.
The payload operates at 100–300 m and images a strobe-lit scene in otherwise
total darkness, for photogrammetry.

The viewport material is load-bearing in two independent ways:

- **Optically**, it sets the short-wavelength bound of what the payload can
  sense. Whatever the sensor's quantum efficiency below that bound, no light
  reaches it.
- **Structurally**, it is a pressure boundary, and its stiffness and creep
  behaviour drive thickness and port geometry.

This record covers the material only. Port *geometry* — flat versus dome — is a
separate question, deferred to the lens and port trade study, though the two
interact (see Consequences).

## Options considered

No formal trade study was run. The decision was made on cost and availability,
and is recorded here because its optical consequence constrains camera selection
(#9, #10, #11) and would otherwise look like an unexplained bound.

| Option | Short-λ transmission | Notes |
| --- | --- | --- |
| **Acrylic (PMMA)** | falls off sharply below ~380 nm | Cheap, widely stocked in ROV-standard flats and domes, forgiving to machine, crazes rather than shatters. Soft and scratch-prone. Creeps under sustained load. |
| Borosilicate glass | ~300 nm | Harder and stiffer, more brittle, more expensive, less commonly stocked in ROV port sizes. |
| Sapphire | deep UV | Excellent transmission and extremely scratch-resistant. Expensive, and practical sizes are small. |

## Decision

**Acrylic.**

Cost and ease of acquisition. Acrylic ports in the sizes and depth ratings this
payload needs are a commodity; the alternatives are not, and neither buys
anything the payload can use — their advantage is transmission below ~380 nm,
which is outside the usable window for a different reason (see below).

## Consequences

- **Short-wavelength bound of ~380 nm.** Together with water's absorption above
  ~700 nm, this fixes the payload's spectral window at **380–700 nm**. See
  `CONTEXT.md`, "Spectral window".
- **UV sensing is unavailable.** No light below ~380 nm reaches the sensor, so
  UV camera variants (Alvium 1800 C-812 UV / IMX487UV) are excluded regardless
  of their quantum efficiency.
- **The 380 nm bound is contingent on this decision, not on physics.** Seawater
  transmits well into the UV. Superseding this record with borosilicate or
  sapphire would move the bound and reopen UV options. Nothing else in camera
  selection depends on the port material.
- **Creep under sustained load.** Acrylic deforms under long-duration pressure
  at 100–300 m, which drives thickness and interacts with port geometry — a
  thick flat port worsens the refraction penalty already noted for the lens
  trade study, while a dome's curvature changes the structural picture entirely.
  This couples the material choice to the deferred flat-versus-dome question and
  wants a mechanical review before the housing is designed.
- **Scratch susceptibility.** Acrylic marks easily; handling, cleaning, and
  field maintenance need to account for it. A scratched port degrades image
  quality directly, which matters more for photogrammetry than for inspection
  imagery.
