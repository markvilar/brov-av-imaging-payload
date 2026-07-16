"""The Alvium MIPI CSI-2 camera records.

The primary source for every structural field is the Alvium CSI-2 Cameras User
Guide, "Alvium 1800 C model specifications" (from p. 108), committed at
``vendors/allied-vision/alvium-csi2-user-guide.pdf``. The EMVA 1288 block comes
from the per-model datasheets, which the user guide does not carry at all; those
are cited by URL from ``vendors/allied-vision/README.md``.

The types these are built from live in :mod:`camsel.models`, and validate every
record on construction.

See issue #11 for the table's scope and #13 for the deferred colour records.
"""

from dataclasses import replace

from camsel.models import (
    CameraModel,
    Channel,
    Chroma,
    EmvaMeasurements,
    Interface,
    LensMount,
    QuantumEfficiencyPoint,
    SensorModel,
    ShutterType,
)

#: Source of every structural field. Constant across all records, so it is not
#: a field. Datasheet versions vary per model and are named per record in
#: :attr:`camsel.models.CameraModel.vendor_discrepancies` only where they
#: disagree.
USER_GUIDE_VERSION = "V4.2.0"

#: Allied Vision quote quantum efficiency here across the Alvium range.
QE_WAVELENGTH_NM = 529.0

C_291_DIAGONAL_DISCREPANCY = (
    "User guide V4.2.0 states the IMX421 sensor size as "
    "'Type 2/3; 8.8 mm x 6.6 mm; 10.8 mm diagonal'. The diagonal does not follow "
    "from its own width and height: sqrt(8.8^2 + 6.6^2) = 11.0 mm, not 10.8 mm. "
    "Nor from the resolution: 1944 x 4.5 um = 8.748 mm and 1472 x 4.5 um = "
    "6.624 mm give 10.97 mm. Width and height are self-consistent with the "
    "resolution and are taken as published; the diagonal is stored as the "
    "derived 10.97 mm. Unlike the C-040 and C-2050 there is no second source to "
    "arbitrate — the figure simply contradicts its own row."
)

C_040_SATURATION_DISCREPANCY = (
    "Datasheet V1.3.0 states saturation capacity 208000 e-, which fails the "
    "dynamic-range check by 20 dB: 20*log10(208000/4.0) = 94.3 dB against a "
    "published 74 dB. Stored as 20800 e-, the published figure / 10, which "
    "checks out at 74.3 dB. Physically corroborated: 6.9 um pixels have 4x the "
    "area of 3.45 um pixels, so ~2x the well depth is plausible and 20x is not."
)


def _mono(value: float) -> tuple[QuantumEfficiencyPoint, ...]:
    return (QuantumEfficiencyPoint(Channel.MONO, QE_WAVELENGTH_NM, value),)


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
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=3.2,
        # Datasheet V1.3.0 states 208000 e-, 10x too high. See the discrepancy
        # recorded on ALVIUM_1800_C_040M.
        saturation_capacity_e=20800,
        absolute_sensitivity_threshold_e=4.0,
        dynamic_range_db=74,
    ),
)

IMX426 = SensorModel(
    model_label="Sony IMX426",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=816,
    resolution_v=624,
    pixel_size_um=9.0,
    sensor_format="Type 1/1.7",
    sensor_width_mm=7.3,
    sensor_height_mm=5.6,
    sensor_diagonal_mm=9.2,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.73),
        temporal_dark_noise_e=21.8,
        saturation_capacity_e=100000,
        absolute_sensitivity_threshold_e=23.7,
        dynamic_range_db=73,
    ),
)

IMX273 = SensorModel(
    model_label="Sony IMX273",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=1456,
    resolution_v=1088,
    pixel_size_um=3.45,
    sensor_format="Type 1/2.9",
    sensor_width_mm=5.0,
    sensor_height_mm=3.8,
    sensor_diagonal_mm=6.3,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=2.1,
        saturation_capacity_e=10400,
        absolute_sensitivity_threshold_e=2.7,
        dynamic_range_db=72,
    ),
)

# Allied Vision publish no EMVA block for the C-203: its datasheet
# (V1.3.1) has no Imaging performance section. Structurally
# complete, but not rankable on the photon budget.
IMX422 = SensorModel(
    model_label="Sony IMX422",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=1632,
    resolution_v=1248,
    pixel_size_um=4.5,
    sensor_format="Type 1/1.7",
    sensor_width_mm=7.3,
    sensor_height_mm=5.6,
    sensor_diagonal_mm=9.2,
    emva=None,
)

# Allied Vision publish no EMVA block for the C-234: its datasheet
# (V1.3.1) has no Imaging performance section. Structurally
# complete, but not rankable on the photon budget.
IMX249 = SensorModel(
    model_label="Sony IMX249",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=1936,
    resolution_v=1216,
    pixel_size_um=5.86,
    sensor_format="Type 1/1.2",
    sensor_width_mm=11.3,
    sensor_height_mm=7.1,
    sensor_diagonal_mm=13.4,
    emva=None,
)

# Allied Vision publish no EMVA block for the C-235: its datasheet
# (V1.3.0) has no Imaging performance section. Structurally
# complete, but not rankable on the photon budget.
IMX174 = SensorModel(
    model_label="Sony IMX174",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=1936,
    resolution_v=1216,
    pixel_size_um=5.86,
    sensor_format="Type 1/1.2",
    sensor_width_mm=11.3,
    sensor_height_mm=7.1,
    sensor_diagonal_mm=13.4,
    emva=None,
)

IMX392 = SensorModel(
    model_label="Sony IMX392",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=1936,
    resolution_v=1216,
    pixel_size_um=3.45,
    sensor_format="Type 1/2.3",
    sensor_width_mm=6.7,
    sensor_height_mm=4.2,
    sensor_diagonal_mm=7.9,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=2.1,
        saturation_capacity_e=10400,
        absolute_sensitivity_threshold_e=2.7,
        dynamic_range_db=72,
    ),
)

IMX421 = SensorModel(
    model_label="Sony IMX421",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=1944,
    resolution_v=1472,
    pixel_size_um=4.5,
    sensor_format="Type 2/3",
    sensor_width_mm=8.8,
    sensor_height_mm=6.6,
    # Published as 10.8 mm, which contradicts the published width and height.
    # See the discrepancy recorded on ALVIUM_1800_C_291M.
    sensor_diagonal_mm=10.97,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.73),
        temporal_dark_noise_e=5.4,
        saturation_capacity_e=25000,
        absolute_sensitivity_threshold_e=6.2,
        dynamic_range_db=72,
    ),
)

IMX265 = SensorModel(
    model_label="Sony IMX265",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2064,
    resolution_v=1544,
    pixel_size_um=3.45,
    sensor_format="Type 1/1.8",
    sensor_width_mm=7.1,
    sensor_height_mm=5.3,
    sensor_diagonal_mm=8.9,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=2.1,
        saturation_capacity_e=10400,
        absolute_sensitivity_threshold_e=2.7,
        dynamic_range_db=72,
    ),
)

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
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=2.1,
        saturation_capacity_e=10400,
        absolute_sensitivity_threshold_e=2.7,
        dynamic_range_db=72,
    ),
)

IMX250 = SensorModel(
    model_label="Sony IMX250",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2464,
    resolution_v=2056,
    pixel_size_um=3.45,
    sensor_format="Type 2/3",
    sensor_width_mm=8.5,
    sensor_height_mm=7.1,
    sensor_diagonal_mm=11.1,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=2.1,
        saturation_capacity_e=10400,
        absolute_sensitivity_threshold_e=2.7,
        dynamic_range_db=72,
    ),
)

IMX548 = SensorModel(
    model_label="Sony IMX548",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2464,
    resolution_v=2064,
    pixel_size_um=2.74,
    sensor_format="Type 1/1.8",
    sensor_width_mm=6.8,
    sensor_height_mm=5.7,
    sensor_diagonal_mm=8.8,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

IMX547 = SensorModel(
    model_label="Sony IMX547",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2464,
    resolution_v=2064,
    pixel_size_um=2.74,
    sensor_format="Type 1/1.8",
    sensor_width_mm=6.8,
    sensor_height_mm=5.7,
    sensor_diagonal_mm=8.8,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

IMX546 = SensorModel(
    model_label="Sony IMX546",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2848,
    resolution_v=2848,
    pixel_size_um=2.74,
    sensor_format="Type 2/3",
    sensor_width_mm=7.8,
    sensor_height_mm=7.8,
    sensor_diagonal_mm=11.0,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

# Allied Vision publish no EMVA block for the C-895: its datasheet
# (V1.2.3) has no Imaging performance section. Structurally
# complete, but not rankable on the photon budget.
IMX267 = SensorModel(
    model_label="Sony IMX267",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=4112,
    resolution_v=2176,
    pixel_size_um=3.45,
    sensor_format="Type 1",
    sensor_width_mm=14.2,
    sensor_height_mm=7.5,
    sensor_diagonal_mm=16.0,
    emva=None,
)

IMX304 = SensorModel(
    model_label="Sony IMX304",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=4112,
    resolution_v=3008,
    pixel_size_um=3.45,
    sensor_format="Type 1.1",
    sensor_width_mm=14.2,
    sensor_height_mm=10.4,
    sensor_diagonal_mm=17.6,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.64),
        temporal_dark_noise_e=2.1,
        saturation_capacity_e=10400,
        absolute_sensitivity_threshold_e=2.7,
        dynamic_range_db=72,
    ),
)

IMX545 = SensorModel(
    model_label="Sony IMX545",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=4128,
    resolution_v=3008,
    pixel_size_um=2.74,
    sensor_format="Type 1/1.1",
    sensor_width_mm=11.3,
    sensor_height_mm=8.2,
    sensor_diagonal_mm=14.0,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

IMX542 = SensorModel(
    model_label="Sony IMX542",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=5328,
    resolution_v=3040,
    pixel_size_um=2.74,
    sensor_format="Type 1.1",
    sensor_width_mm=14.6,
    sensor_height_mm=8.3,
    sensor_diagonal_mm=16.8,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

IMX541 = SensorModel(
    model_label="Sony IMX541",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=4512,
    resolution_v=4512,
    pixel_size_um=2.74,
    sensor_format="Type 1.1",
    sensor_width_mm=12.4,
    sensor_height_mm=12.4,
    sensor_diagonal_mm=17.5,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

IMX540 = SensorModel(
    model_label="Sony IMX540",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=5328,
    resolution_v=4608,
    pixel_size_um=2.74,
    sensor_format="Type 1.2",
    sensor_width_mm=14.6,
    sensor_height_mm=12.6,
    sensor_diagonal_mm=19.3,
    emva=EmvaMeasurements(
        quantum_efficiency=_mono(0.68),
        temporal_dark_noise_e=2.3,
        saturation_capacity_e=9400,
        absolute_sensitivity_threshold_e=2.9,
        dynamic_range_db=70,
    ),
)

# Allied Vision publish no EMVA block for the C-507_Pol: its datasheet
# (V1.0.1) has no Imaging performance section. Structurally
# complete, but not rankable on the photon budget.
IMX264MZR = SensorModel(
    model_label="Sony IMX264MZR",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2464,
    resolution_v=2056,
    pixel_size_um=3.45,
    sensor_format="Type 2/3",
    sensor_width_mm=8.5,
    sensor_height_mm=7.1,
    sensor_diagonal_mm=11.1,
    emva=None,
)

# Allied Vision publish no EMVA block for the C-508_Pol: its datasheet
# (V1.0.1) has no Imaging performance section. Structurally
# complete, but not rankable on the photon budget.
IMX250MZR = SensorModel(
    model_label="Sony IMX250MZR",
    chroma=Chroma.MONO,
    shutter_modes=frozenset({ShutterType.GLOBAL}),
    resolution_h=2464,
    resolution_v=2056,
    pixel_size_um=3.45,
    sensor_format="Type 2/3",
    sensor_width_mm=8.5,
    sensor_height_mm=7.1,
    sensor_diagonal_mm=11.1,
    emva=None,
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

ALVIUM_1800_C_052M = CameraModel(
    model_label="1800 C-052m",
    series="Alvium 1800 C",
    sensor=IMX426,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=689,
    exposure_min_ns=24_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_158M = CameraModel(
    model_label="1800 C-158m",
    series="Alvium 1800 C",
    sensor=IMX273,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=262,
    exposure_min_ns=28_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS, LensMount.S}),
    power_consumption_w=2.4,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_203M = CameraModel(
    model_label="1800 C-203m",
    series="Alvium 1800 C",
    sensor=IMX422,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=225,
    exposure_min_ns=18_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.1,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_234M = CameraModel(
    model_label="1800 C-234m",
    series="Alvium 1800 C",
    sensor=IMX249,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=40,
    exposure_min_ns=34_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=1.9,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_235M = CameraModel(
    model_label="1800 C-235m",
    series="Alvium 1800 C",
    sensor=IMX174,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=155,
    exposure_min_ns=19_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=1.9,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_240M = CameraModel(
    model_label="1800 C-240m",
    series="Alvium 1800 C",
    sensor=IMX392,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=192,
    exposure_min_ns=26_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS, LensMount.S}),
    power_consumption_w=2.7,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_291M = CameraModel(
    model_label="1800 C-291m",
    series="Alvium 1800 C",
    sensor=IMX421,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=166,
    exposure_min_ns=17_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
    vendor_discrepancies=(C_291_DIAGONAL_DISCREPANCY,),
)

ALVIUM_1800_C_319M = CameraModel(
    model_label="1800 C-319m",
    series="Alvium 1800 C",
    sensor=IMX265,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=54,
    exposure_min_ns=26_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS, LensMount.S}),
    power_consumption_w=1.9,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
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

ALVIUM_1800_C_508M = CameraModel(
    model_label="1800 C-508m",
    series="Alvium 1800 C",
    sensor=IMX250,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=95,
    exposure_min_ns=19_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=2.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_510M = CameraModel(
    model_label="1800 C-510m",
    series="Alvium 1800 C",
    sensor=IMX548,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=81,
    exposure_min_ns=8_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS, LensMount.S}),
    power_consumption_w=2.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_511M = CameraModel(
    model_label="1800 C-511m",
    series="Alvium 1800 C",
    sensor=IMX547,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=79,
    exposure_min_ns=8_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS, LensMount.S}),
    power_consumption_w=3.0,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_811M = CameraModel(
    model_label="1800 C-811m",
    series="Alvium 1800 C",
    sensor=IMX546,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=59,
    exposure_min_ns=8_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.1,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_895M = CameraModel(
    model_label="1800 C-895m",
    series="Alvium 1800 C",
    sensor=IMX267,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=31,
    exposure_min_ns=29_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=2.6,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_1236M = CameraModel(
    model_label="1800 C-1236m",
    series="Alvium 1800 C",
    sensor=IMX304,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=22,
    exposure_min_ns=29_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C}),
    power_consumption_w=2.6,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_1242M = CameraModel(
    model_label="1800 C-1242m",
    series="Alvium 1800 C",
    sensor=IMX545,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=40,
    exposure_min_ns=11_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.2,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_1620M = CameraModel(
    model_label="1800 C-1620m",
    series="Alvium 1800 C",
    sensor=IMX542,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=32,
    exposure_min_ns=13_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_2040M = CameraModel(
    model_label="1800 C-2040m",
    series="Alvium 1800 C",
    sensor=IMX541,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=25,
    exposure_min_ns=11_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.7,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_2460M = CameraModel(
    model_label="1800 C-2460m",
    series="Alvium 1800 C",
    sensor=IMX540,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=21,
    exposure_min_ns=13_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=3.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

ALVIUM_1800_C_507_POLM = CameraModel(
    model_label="1800 C-507 Polm",
    series="Alvium 1800 C",
    sensor=IMX264MZR,
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

ALVIUM_1800_C_508_POLM = CameraModel(
    model_label="1800 C-508 Polm",
    series="Alvium 1800 C",
    sensor=IMX250MZR,
    interface=Interface.CSI2,
    adc_bits=12,
    max_frame_rate_fps=95,
    exposure_min_ns=19_000,
    exposure_max_ns=10_000_000_000,
    lens_mounts=frozenset({LensMount.C, LensMount.CS}),
    power_consumption_w=2.8,
    mass_g=40,
    operating_temp_min_c=-20,
    operating_temp_max_c=65,
)

IMX287_COLOR = SensorModel.as_color(IMX287, green=0.58, blue=0.15, red=0.03)
IMX264_COLOR = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)

ALVIUM_1800_C_040C = replace(
    ALVIUM_1800_C_040M, model_label="1800 C-040c", sensor=IMX287_COLOR
)
ALVIUM_1800_C_507C = replace(
    ALVIUM_1800_C_507M, model_label="1800 C-507c", sensor=IMX264_COLOR
)


#: The candidate table: 22 monochrome models, plus the two colour records that
#: #10 built to prove `SensorModel.as_color`. The remaining colour records are
#: deferred to #13 — Allied Vision publish no EMVA block for colour, so each one
#: costs three QE values read by eye off a chart.
#:
#: Global shutter only, visible spectrum only. Six carry `emva=None`: Allied
#: Vision publish no EMVA block for them, so they are structurally complete but
#: cannot be ranked on the photon budget. See issue #11.
CSI2_CAMERAS: tuple[CameraModel, ...] = (
    ALVIUM_1800_C_040M,
    ALVIUM_1800_C_040C,
    ALVIUM_1800_C_052M,
    ALVIUM_1800_C_158M,
    ALVIUM_1800_C_203M,
    ALVIUM_1800_C_234M,
    ALVIUM_1800_C_235M,
    ALVIUM_1800_C_240M,
    ALVIUM_1800_C_291M,
    ALVIUM_1800_C_319M,
    ALVIUM_1800_C_507M,
    ALVIUM_1800_C_507C,
    ALVIUM_1800_C_508M,
    ALVIUM_1800_C_510M,
    ALVIUM_1800_C_511M,
    ALVIUM_1800_C_811M,
    ALVIUM_1800_C_895M,
    ALVIUM_1800_C_1236M,
    ALVIUM_1800_C_1242M,
    ALVIUM_1800_C_1620M,
    ALVIUM_1800_C_2040M,
    ALVIUM_1800_C_2460M,
    ALVIUM_1800_C_507_POLM,
    ALVIUM_1800_C_508_POLM,
)
