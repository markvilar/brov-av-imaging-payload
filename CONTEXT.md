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
| Camera vendor        | Allied Vision                                               |
| Camera interface     | MIPI CSI-2                                                   |
| Host carrier         | NVIDIA Jetson                                                |
| Strobe energy source | Onboard capacitor bank, recharged between frames            |
| Housing layout       | Separate camera and strobe housings                         |
| Host vehicle         | Platform-agnostic (both tethered ROV and autonomous AUV)    |
| Project stage        | Concept / camera selection                                  |

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
  penetration or sensor sensitivity. To be resolved by trade study.
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
