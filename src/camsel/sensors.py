"""The Alvium MIPI CSI-2 camera records.

The primary source for every structural field is the Alvium CSI-2 Cameras User
Guide, "Alvium 1800 C model specifications" (from p. 108), committed at
``vendors/allied-vision/alvium-csi2-user-guide.pdf``. The EMVA 1288 block comes
from the per-model datasheets, which the user guide does not carry at all; those
are cited by URL from ``vendors/allied-vision/README.md``.

The types these are built from live in :mod:`camsel.models`, and validate every
record on construction.

See issue #10 for the design, #11 for the full candidate table.
"""

from camsel.models import (
    CameraModel,
    Channel,
    Chroma,
    Interface,
    LensMount,
    QuantumEfficiencyPoint,
    SensorModel,
    ShutterType,
)
from dataclasses import replace

#: Source of every structural field. Constant across all records, so it is not
#: a field. Datasheet versions vary per model and are named per record in
#: :attr:`camsel.models.CameraModel.vendor_discrepancies` only where they
#: disagree.
USER_GUIDE_VERSION = "V4.2.0"

#: Allied Vision quote quantum efficiency here across the Alvium range.
QE_WAVELENGTH_NM = 529.0


def _mono(value: float) -> tuple[QuantumEfficiencyPoint, ...]:
    return (QuantumEfficiencyPoint(Channel.MONO, QE_WAVELENGTH_NM, value),)


IMX264 = SensorModel(
    model_label="Sony IMX264",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2464,
    resolution_v=2056,
    pixel_size_um=3.45,
    sensor_format="Type 2/3",
    sensor_width_mm=8.5,
    sensor_height_mm=7.1,
    sensor_diagonal_mm=11.1,
    quantum_efficiency=_mono(0.64),
    temporal_dark_noise_e=2.1,
    saturation_capacity_e=10400,
    absolute_sensitivity_threshold_e=2.7,
    dynamic_range_db=72,
)
IMX264_COLOR = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)

IMX287 = SensorModel(
    model_label="Sony IMX287",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=728,
    resolution_v=544,
    pixel_size_um=6.9,
    sensor_format="Type 1/2.9",
    sensor_width_mm=5.0,
    sensor_height_mm=3.8,
    sensor_diagonal_mm=6.3,
    quantum_efficiency=_mono(0.64),
    temporal_dark_noise_e=3.2,
    # The datasheet states 208000 e-, 10x too high. See the discrepancy
    # recorded on ALVIUM_1800_C_040M.
    saturation_capacity_e=20800,
    absolute_sensitivity_threshold_e=4.0,
    dynamic_range_db=74,
)
IMX287_COLOR = SensorModel.as_color(IMX287, green=0.58, blue=0.15, red=0.03)

C_040_SATURATION_DISCREPANCY = (
    "Datasheet V1.3.0 states saturation capacity 208000 e-, which fails the "
    "dynamic-range check by 20 dB: 20*log10(208000/4.0) = 94.3 dB against a "
    "published 74 dB. Stored as 20800 e-, the published figure / 10, which "
    "checks out at 74.3 dB. Physically corroborated: 6.9 um pixels have 4x the "
    "area of 3.45 um pixels, so ~2x the well depth is plausible and 20x is not."
)

ALVIUM_1800_C_507M = CameraModel(
    model_label="1800 C-507m",
    series="Alvium 1800 C",
    sensor=IMX264,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=34,
    exposure_min_ns=28_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=1.9,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)
ALVIUM_1800_C_507C = replace(
    ALVIUM_1800_C_507M, model_label="1800 C-507c", sensor=IMX264_COLOR
)

ALVIUM_1800_C_040M = CameraModel(
    model_label="1800 C-040m",
    series="Alvium 1800 C",
    sensor=IMX287,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=494,
    exposure_min_ns=28_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS, LensMount.S}),
    power_consumption_w=1.7,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
    vendor_discrepancies=(C_040_SATURATION_DISCREPANCY,),
)
ALVIUM_1800_C_040C = replace(
    ALVIUM_1800_C_040M, model_label="1800 C-040c", sensor=IMX287_COLOR
)

#: The proving subset, not the full candidate table — see issue #11.
#:
#: Global shutter only. The rolling-shutter models are excluded by decision, not
#: by CAM-1: the C-1240 and C-2050 offer global reset shutter, which satisfies
#: CAM-1 in a dark scene, but only through GenICam for CSI-2 Access — a
#: dependency on the Jetson-side capture stack, which is developed elsewhere.
#: See requirements/camera-requirements.md.
CSI2_CAMERAS: tuple[CameraModel, ...] = (
    ALVIUM_1800_C_040M,
    ALVIUM_1800_C_040C,
    ALVIUM_1800_C_507M,
    ALVIUM_1800_C_507C,
)
