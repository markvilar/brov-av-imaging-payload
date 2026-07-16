"""Tests for the camera and sensor records.

The point of these records is that they validate vendor data, so most of what
follows deliberately corrupts a good record and asserts the check fires.
"""

from dataclasses import replace

import pytest

from camsel.models import (
    Channel,
    Chroma,
    LensMount,
    QuantumEfficiencyCurve,
    QuantumEfficiencyPoint,
    SensorModel,
    ShutterType,
)
from camsel.sensors import (
    ALVIUM_1800_C_040M,
    ALVIUM_1800_C_507C,
    ALVIUM_1800_C_507M,
    ALVIUM_1800_C_2050M,
    CSI2_CAMERAS,
    IMX183,
    IMX264,
    IMX287,
)


def test_every_record_constructs() -> None:
    """All six proving-subset records pass every check."""
    assert len(CSI2_CAMERAS) == 6
    assert {c.model_label for c in CSI2_CAMERAS} == {
        "1800 C-040m",
        "1800 C-040c",
        "1800 C-507m",
        "1800 C-507c",
        "1800 C-2050m",
        "1800 C-2050c",
    }


class TestEmvaRedundancy:
    def test_fires_on_a_corrupted_saturation_capacity(self) -> None:
        """The C-040's real failure: saturation capacity 10x too high.

        This is the datasheet's published figure, and it is why the record
        stores 20800 instead.
        """
        with pytest.raises(ValueError, match="dynamic range derived"):
            replace(IMX287, saturation_capacity_e=208000)

    def test_fires_on_a_corrupted_dynamic_range(self) -> None:
        with pytest.raises(ValueError, match="dynamic range derived"):
            replace(IMX264, dynamic_range_db=90)

    def test_tolerates_the_vendors_rounding(self) -> None:
        """Published figures are rounded to whole dB and must still pass."""
        for sensor in (IMX264, IMX287, IMX183):
            assert sensor.dynamic_range_db is not None

    def test_skipped_for_colour(self) -> None:
        """Colour has neither field, so there is nothing to check."""
        colour = ALVIUM_1800_C_507C.sensor
        assert colour.dynamic_range_db is None
        assert colour.absolute_sensitivity_threshold_e is None


class TestSensorGeometry:
    def test_fires_on_the_datasheets_c2050_resolution(self) -> None:
        """The C-2050 datasheet states 5376 where the user guide says 5496."""
        with pytest.raises(ValueError, match="derived width"):
            replace(IMX183, resolution_h=5376)

    def test_fires_on_a_corrupted_pixel_size(self) -> None:
        with pytest.raises(ValueError, match="derived width"):
            replace(IMX264, pixel_size_um=3.75)

    def test_published_dimensions_reproduce(self) -> None:
        for sensor in (IMX264, IMX287, IMX183):
            width = sensor.resolution_h * sensor.pixel_size_um / 1000
            assert width == pytest.approx(sensor.sensor_width_mm, abs=0.15)


class TestChromaChannels:
    def test_mono_record_carries_one_mono_point(self) -> None:
        assert IMX264.chroma is Chroma.MONO
        (point,) = IMX264.quantum_efficiency
        assert point.channel is Channel.MONO

    def test_colour_record_carries_rgb_and_no_mono(self) -> None:
        colour = ALVIUM_1800_C_507C.sensor
        assert colour.chroma is Chroma.COLOR
        assert {p.channel for p in colour.quantum_efficiency} == {
            Channel.RED,
            Channel.GREEN,
            Channel.BLUE,
        }

    def test_fires_when_mono_carries_a_colour_channel(self) -> None:
        with pytest.raises(ValueError, match="monochrome but carries"):
            replace(
                IMX264,
                quantum_efficiency=(
                    QuantumEfficiencyPoint(Channel.GREEN, 529.0, 0.57),
                ),
            )

    def test_fires_when_colour_carries_a_mono_channel(self) -> None:
        with pytest.raises(ValueError, match="colour but carries"):
            replace(
                ALVIUM_1800_C_507C.sensor,
                quantum_efficiency=(QuantumEfficiencyPoint(Channel.MONO, 529.0, 0.64),),
            )


class TestAsColor:
    def test_inherits_saturation_and_dark_noise(self) -> None:
        """The CFA sits above the photodiode: well depth and readout are the same."""
        colour = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)
        assert colour.saturation_capacity_e == IMX264.saturation_capacity_e
        assert colour.temporal_dark_noise_e == IMX264.temporal_dark_noise_e

    def test_drops_threshold_and_dynamic_range(self) -> None:
        """Both depend on QE, which AV never publish per channel."""
        colour = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)
        assert colour.absolute_sensitivity_threshold_e is None
        assert colour.dynamic_range_db is None

    def test_reads_qe_at_the_vendors_wavelength(self) -> None:
        colour = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)
        green = colour.quantum_efficiency_for(Channel.GREEN)
        assert green.wavelength_nm == 529.0
        assert green.value == 0.57

    def test_rejects_a_colour_source(self) -> None:
        colour = ALVIUM_1800_C_507C.sensor
        with pytest.raises(ValueError, match="not a monochrome record"):
            SensorModel.as_color(colour, green=0.57, blue=0.10, red=0.03)

    def test_green_is_below_mono(self) -> None:
        """The Bayer penalty: a green pixel sees less than an unfiltered one."""
        for mono, colour in (
            (IMX264, ALVIUM_1800_C_507C.sensor),
            (IMX287, SensorModel.as_color(IMX287, green=0.58, blue=0.15, red=0.03)),
            (IMX183, SensorModel.as_color(IMX183, green=0.69, blue=0.22, red=0.03)),
        ):
            mono_qe = mono.quantum_efficiency_for(Channel.MONO).value
            green_qe = colour.quantum_efficiency_for(Channel.GREEN).value
            assert green_qe < mono_qe


class TestQuantumEfficiency:
    def test_rejects_a_value_outside_zero_to_one(self) -> None:
        with pytest.raises(ValueError, match="is a fraction"):
            QuantumEfficiencyPoint(Channel.MONO, 529.0, 64)

    def test_curve_rejects_a_foreign_channel(self) -> None:
        with pytest.raises(ValueError, match="foreign channels"):
            QuantumEfficiencyCurve(
                channel=Channel.GREEN,
                points=(QuantumEfficiencyPoint(Channel.BLUE, 450.0, 0.48),),
            )

    def test_curve_interpolates(self) -> None:
        curve = QuantumEfficiencyCurve(
            channel=Channel.MONO,
            points=(
                QuantumEfficiencyPoint(Channel.MONO, 500.0, 0.60),
                QuantumEfficiencyPoint(Channel.MONO, 600.0, 0.50),
            ),
        )
        assert curve.at(550.0) == pytest.approx(0.55)

    def test_curve_refuses_to_extrapolate(self) -> None:
        curve = QuantumEfficiencyCurve(
            channel=Channel.MONO,
            points=(QuantumEfficiencyPoint(Channel.MONO, 500.0, 0.60),),
        )
        with pytest.raises(ValueError, match="outside the sampled range"):
            curve.at(700.0)


class TestCam1:
    """requirements/camera-requirements.md — simultaneous line exposure."""

    def test_global_shutter_satisfies_unconditionally(self) -> None:
        assert ALVIUM_1800_C_507M.satisfies_cam1_unconditionally
        assert ALVIUM_1800_C_040M.satisfies_cam1_unconditionally

    def test_global_reset_does_not_satisfy_unconditionally(self) -> None:
        """The C-2050 needs GenICam for CSI-2 Access, an open question."""
        assert not ALVIUM_1800_C_2050M.satisfies_cam1_unconditionally
        assert ShutterType.GLOBAL_RESET in ALVIUM_1800_C_2050M.sensor.shutter_modes

    def test_readout_time_is_inferred_from_frame_rate(self) -> None:
        """CAM-1 needs readout time; max frame rate is the only handle on it."""
        assert ALVIUM_1800_C_2050M.readout_time_ns == pytest.approx(
            38_461_538, rel=1e-6
        )

    def test_exposure_ceiling_exceeds_readout(self) -> None:
        """A GRS strobe area exists only if exposure can outlast readout."""
        for camera in CSI2_CAMERAS:
            assert camera.exposure_max_ns > camera.readout_time_ns


class TestCameraModel:
    def test_rejects_an_empty_exposure_range(self) -> None:
        with pytest.raises(ValueError, match="exposure range"):
            replace(ALVIUM_1800_C_507M, exposure_min_ns=10_000_000_001)

    def test_discrepancies_are_enumerable(self) -> None:
        """#11 needs the vendor-error set to report to Allied Vision."""
        flagged = {c.model_label for c in CSI2_CAMERAS if c.vendor_discrepancies}
        assert flagged == {
            "1800 C-040m",
            "1800 C-040c",
            "1800 C-2050m",
            "1800 C-2050c",
        }

    def test_clean_records_carry_no_discrepancies(self) -> None:
        assert ALVIUM_1800_C_507M.vendor_discrepancies == ()

    def test_lens_mounts_are_an_availability_set(self) -> None:
        assert ALVIUM_1800_C_2050M.lens_mounts == frozenset({LensMount.C})
        assert LensMount.S in ALVIUM_1800_C_040M.lens_mounts

    def test_records_are_frozen(self) -> None:
        with pytest.raises(AttributeError):
            ALVIUM_1800_C_507M.adc_bits = 10  # type: ignore[misc]
