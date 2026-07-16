# CONTEXT

Domain context for the underwater imaging payload. This is the single source of
truth for *what* we are building and *why*. Decisions that resolve open questions
are recorded as ADRs under `decisions/`.

## Purpose

Select, design, and document a custom **imaging payload for an underwater
robot**. The payload captures underwater **still imagery** in **low-light**
conditions at a **low rate** (typically ~1 frame per second), lit by
**LED strobes** whose firing is synchronized to the camera shutter so the
strobes illuminate the scene only while the shutter is open.

The primary imaging goal is **photogrammetry / 3D reconstruction**, so image
sharpness, consistent illumination, and precise camera↔strobe timing matter
more than frame rate.

## System overview

The payload is built around an **Allied Vision** camera and comprises three
tightly-coupled subsystems:

- **Camera subsystem** — an Allied Vision camera on a **MIPI CSI-2** interface,
  hosted by an **NVIDIA Jetson** carrier board.
- **Lighting subsystem** — **LED strobes** in their own housing(s), energized by
  an **onboard capacitor bank** (capacitor carriers) recharged between frames
  from vehicle power, which suits the ~1 fps cadence.
- **Triggering electronics** — the circuitry that synchronizes strobe firing
  with camera exposure so the strobes fire while the shutter is open.

Mechanically, the camera and strobes live in **separate housings** wired
together, allowing the lighting geometry to be adjusted independently of the
camera.

## Operating envelope & constraints

| Parameter            | Value / intent                                              |
|----------------------|-------------------------------------------------------------|
| Depth range          | 100–300 m                                                   |
| Capture rate         | ~1 fps (low rate)                                            |
| Lighting             | LED strobes, fired only during shutter-open                 |
| Light conditions     | Low-light / dark underwater                                 |
| Spectral window      | 380–700 nm (acrylic viewport → water absorption)            |
| Camera vendor        | Allied Vision                                               |
| Camera interface     | MIPI CSI-2                                                   |
| Host carrier         | NVIDIA Jetson                                                |
| Strobe energy source | Onboard capacitor bank, recharged between frames            |
| Housing layout       | Separate camera and strobe housings                         |
| Host vehicle         | Platform-agnostic (both tethered ROV and autonomous AUV)    |
| Project stage        | Concept / camera selection                                  |

### Spectral window

Useful sensing is bounded at **380–700 nm**. The two bounds have different
causes, and only one of them is physics.

**Upper bound, ~700 nm — water absorption.** Water absorbs strongly in the red
and near-infrared, and beyond ~700 nm no practical strobe energy recovers the
loss.

The relevant path length is **not the depth**. At 100–300 m there is no ambient
light — which is why the payload carries strobes at all — so every photon
reaching the sensor travels strobe → scene → sensor, a path of a few metres.
Over a ~3 m round trip in reasonably clear water, 650 nm red is attenuated to
roughly 10 %: lossy, but not extinguished. This is why strobe-lit colour imaging
works at close range even where ambient red is long gone. "Water kills red" is
true of ambient-lit scenes at depth, and only partly true of ours.

**Lower bound, ~380 nm — the acrylic viewport.** Acrylic transmission falls off
sharply below ~380 nm. This bound is a consequence of a *decision*
(`decisions/0001-viewport-material.md`), not of the water: seawater transmits
well into the UV. A borosilicate or sapphire port would move it.

**Consequences for camera selection.** Sensitivity outside the window is
unusable, so it excludes on principle rather than on preference:

- **UV variants** — no light below ~380 nm reaches the sensor.
- **SWIR / VSWIR variants** — water is effectively opaque at those wavelengths.
- **NIR-enhanced variants** — their added response lies above the window, and
  the deeper photodiodes that produce it tend to soften MTF through charge
  diffusion. That trades sharpness, which photogrammetry depends on, for a band
  the water removes.

**The optimum within the window is water-type dependent.** Clear ocean water
transmits best around 450–500 nm, while coastal and turbid water shifts the
optimum toward roughly 520–570 nm as dissolved organics absorb blue (Jerlov
water types). 380–700 nm is the hard bound; choosing a wavelength inside it is
the strobe-spectrum trade study, and that study needs an operating water type as
an input.

## Subsystem responsibilities

- **Camera + Jetson** — image capture and, on the Jetson, any onboard handling.
  Note: capture/control software is **not** developed in this repository (see
  Repository scope); the repo defines the camera and its interface requirements.
- **LED strobes** — deliver sufficient, uniform illumination for photogrammetry
  during the shutter-open window, within the platform power budget.
- **Capacitor carriers** — store and deliver the strobe energy per flash and
  recharge within the inter-frame interval.
- **Triggering electronics** — bridge camera exposure timing and strobe firing.

## Open questions / trade studies

These are the main unresolved decisions this repository exists to work through.
Each should graduate into an ADR in `decisions/` once decided.

- **Sync master** — is the *camera* the trigger master (its exposure-active /
  strobe-out line drives the strobe electronics) or is there a *dedicated
  trigger controller* driving both camera and strobes? Currently undecided.
- **Sensor type** — **color vs. monochrome**. Color aids true-color
  photogrammetry and habitat interpretation; monochrome offers higher low-light
  sensitivity. To be resolved by trade study.
- **Camera model** — specific Allied Vision MIPI camera (sensor, resolution,
  shutter, sensitivity) not yet selected.
- **Strobe spectrum** — white/broad-spectrum vs. a wavelength tuned for water
  penetration or sensor sensitivity. Bounded to 380–700 nm (see Spectral
  window); the optimum inside that window depends on water type, so this study
  is blocked on the operating environment below. To be resolved by trade study.
- **Operating water type** — clear ocean vs. coastal/turbid shifts the
  transmission optimum by ~70 nm and changes the achievable working distance.
  Currently unspecified, and an input to both the strobe-spectrum study and the
  photon budget.
- **Power architecture details** — capacitor bank sizing, recharge budget, and
  how the platform-agnostic power interface is defined for ROV vs. AUV hosts.

## Repository scope

This repository holds:

- **Design documentation & decisions** — `requirements/`, `trade-studies/`, this
  `CONTEXT.md`, and ADRs under `decisions/`.
- **Vendor documentation** — `vendors/` (datasheets, manuals, application notes).
- **Test & validation reports** — `tests/`.
- **Electronics** — schematics / PCB for triggering electronics, capacitor
  carriers, and strobe driver boards.
- **Mechanical / CAD** — camera and strobe housings, mounts, and related
  pressure-vessel geometry.

Out of scope (developed elsewhere): the Jetson-side capture/control **firmware
and software**.

## Workflow

Work is orchestrated in **GitHub Projects** with **GitHub Issues** on
`markvilar/brov-av-imaging-payload`. Issues carry the workflow and discussion;
this repository carries the *durable record*. An issue's outcome is distilled
into a committed artifact — a resolved trade-off into `trade-studies/` plus an
ADR in `decisions/`, a validation task into `tests/`. Cross-link both ways: cite
the issue number in the artifact, and close the issue with a link to the commit.
Issues are categorized with `type:`, `area:`, and `priority:` labels (see
`CLAUDE.md`).
