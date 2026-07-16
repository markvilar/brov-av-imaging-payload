# Camera requirements

Requirements on the camera subsystem, derived from the payload architecture in
`CONTEXT.md`. These are *inputs* to the camera-model trade study, not the
selection itself — the selection is recorded in `trade-studies/` and
`decisions/`.

## CAM-1 — Simultaneous line exposure during the strobe flash

**Requirement.** The camera shall integrate all sensor lines simultaneously for
the full duration of the strobe flash.

**Rationale.** The payload lights the scene with LED strobes fired while the
shutter is open, in otherwise total darkness. Essentially all signal arrives
during the flash. A sensor whose lines do not share a common integration window
therefore records a flash on only a subset of lines, producing banding — the
illumination is uneven not because the light is uneven, but because the lines
were not listening at the same time.

This is a property of the shutter, not of the strobe, and no strobe design
compensates for it.

**Basis.** Allied Vision documents the three shutter behaviours in Table 157,
"Shutter types affecting image readout" (Alvium CSI-2 Cameras User Guide V4.2.0,
p. 317):

| Property | Rolling shutter (RS) | Global reset shutter (GRS) |
| --- | --- | --- |
| Line exposure start | Deferred from line to line | Common for all lines |
| Line exposure time | Common for all lines | Increases from line to line |
| Image brightness | Constant over the image | Varying over the image |
| Compensation | Use an additional mechanical shutter or use a strobe light | |

Global shutter is described separately: integration is common to all lines, and
readout follows from a shielded storage node.

Note the direction of the GRS entry. Its *documented defect* is that brightness
varies over the image, because line exposure time grows down the frame and later
lines accumulate more ambient light and dark current. Allied Vision's stated
compensation for that defect is **to use a strobe light**, and the accompanying
diagram labels a **"Strobe area"** — a window spanning all lines, bounded by the
common reset and the first line's readout. Firing inside it gives every line the
same flash.

**Satisfied by.**

| Shutter | Satisfies CAM-1 | Conditions |
| --- | --- | --- |
| Global shutter (GS) | Yes | Unconditional. Flash anywhere within `ExposureActive`. |
| Global reset shutter (GRS) | Conditional | (a) Scene is dark, so the per-line exposure-time gradient carries no signal — holds at 100–300 m. (b) Flash falls inside the "Strobe area". (c) Requires **GenICam for CSI-2 Access**; GRS is not exposed under plain V4L2. |
| Rolling shutter (RS) | No | No defined strobe area. A common window exists only if exposure exceeds total readout, which the vendor neither specifies nor guarantees. |

**Consequences for selection.**

- Plain-RS models are excluded. In the current CSI-2 line that is the
  **1800 C-500** (ON Semi AR0521SR), the only RS-without-GRS candidate.
- GRS models — **1800 C-1240** (IMX226) and **1800 C-2050** (IMX183) — remain
  candidates *conditionally*. Condition (c) is an external dependency on the
  Jetson-side capture stack, which this repository does not develop (see
  `CONTEXT.md`, Repository scope). It is tracked as an open question there.
- The remaining 23 candidates are global shutter and satisfy CAM-1 outright.

Whether to accept the GenICam dependency in exchange for the GRS models is not
decided here. It is an input to the camera-model trade study, where it presents
as a resolution-versus-sensitivity trade: the C-2050 is the only 20 MP candidate
and has the highest quantum efficiency in the set, but its 2.4 µm pixels collect
less light per pixel than the 3.45 µm alternatives.

**Verification.** Bench test: strobe-lit flat field at the operating exposure,
checked for row-wise uniformity across the frame. Reported in `tests/`.
