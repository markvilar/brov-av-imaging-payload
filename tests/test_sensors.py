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
    QuantumEfficiencyPoints,
    SensorModel,
    ShutterType,
    SignalMetrics,
)
from camsel.sensors import (
    ALVIUM_1800_C_040M,
    ALVIUM_1800_C_507C,
    ALVIUM_1800_C_507M,
    CSI2_CAMERAS,
    IMX264,
    IMX287,
)


def test_every_record_constructs() -> None:
    """The candidate table: 23 monochrome models plus two colour records.

    Constructing at import means every record has already passed the geometry,
    chroma and (where published) EMVA checks.
    """
    assert len(CSI2_CAMERAS) == 25
    mono = [c for c in CSI2_CAMERAS if c.sensor.chroma is Chroma.MONO]
    colour = [c for c in CSI2_CAMERAS if c.sensor.chroma is Chroma.COLOR]
    assert len(mono) == 23
    assert len(colour) == 2  # the rest are deferred to #13


def test_models_without_a_published_emva_block() -> None:
    """Allied Vision do not publish the block for every model.

    These are structurally complete but cannot be ranked on the photon budget.
    Kept in the table rather than excluded, so the trade study can say why a
    candidate was not evaluated instead of it silently not appearing.
    """
    missing = {c.model_label for c in CSI2_CAMERAS if c.sensor.signal_metrics is None}
    assert missing == {
        "1800 C-203m",
        "1800 C-234m",
        "1800 C-235m",
        "1800 C-321m",
        "1800 C-895m",
        "1800 C-507 Polm",
        "1800 C-508 Polm",
    }


def test_the_c321_is_partial_but_present() -> None:
    """No datasheet exists for it, so three fields are unpublished.

    A missing document is not a reason to drop a candidate: everything the user
    guide carries is recorded, and the gaps are visible rather than implied by
    the row's absence.
    """
    c321 = next(c for c in CSI2_CAMERAS if c.model_label == "1800 C-321m")
    assert c321.sensor.signal_metrics is None
    assert c321.adc_bits is None
    assert c321.lens_mounts is None
    # Everything the user guide does publish is there.
    assert c321.sensor.pixel_size == 2.25
    assert c321.max_frame_rate == 111
    assert c321.power_consumption == 1.9
    assert c321.vendor_discrepancies


def test_rankable_records_have_the_budget_inputs() -> None:
    """Anything with an EMVA block has what the photon budget needs."""
    for camera in CSI2_CAMERAS:
        if camera.sensor.signal_metrics is None:
            continue
        assert camera.sensor.signal_metrics.saturation_capacity > 0
        assert camera.sensor.signal_metrics.temporal_dark_noise > 0
        assert camera.sensor.pixel_area > 0


def test_every_candidate_is_global_shutter() -> None:
    """Selection is restricted to global shutter — see CAM-1's consequences."""
    assert all(c.satisfies_cam1_unconditionally for c in CSI2_CAMERAS)


class TestEmvaRedundancy:
    def test_fires_on_a_corrupted_saturation_capacity(self) -> None:
        """The C-040's real failure: saturation capacity 10x too high.

        This is the datasheet's published figure, and it is why the record
        stores 20800 instead.
        """
        assert IMX287.signal_metrics is not None
        with pytest.raises(ValueError, match="dynamic range derived"):
            replace(IMX287.signal_metrics, saturation_capacity=208000)

    def test_fires_on_a_corrupted_dynamic_range(self) -> None:
        assert IMX264.signal_metrics is not None
        with pytest.raises(ValueError, match="dynamic range derived"):
            replace(IMX264.signal_metrics, dynamic_range=90)

    def test_tolerates_the_vendors_rounding(self) -> None:
        """Published figures are rounded to whole dB and must still pass."""
        for sensor in (IMX264, IMX287):
            assert sensor.signal_metrics is not None
            assert sensor.signal_metrics.dynamic_range is not None

    def test_skipped_for_colour(self) -> None:
        """Colour has neither field, so there is nothing to check."""
        colour = ALVIUM_1800_C_507C.sensor
        assert colour.signal_metrics is not None
        assert colour.signal_metrics.dynamic_range is None
        assert colour.signal_metrics.absolute_sensitivity_threshold is None


class TestSensorGeometry:
    def test_fires_on_the_datasheets_c2050_resolution(self) -> None:
        """The check against the real C-2050 error, kept after its exclusion.

        The C-2050 is no longer a candidate (global shutter only), so it has no
        record. The error is real and worth reporting to Allied Vision, and this
        is the evidence that the geometry check catches it: their datasheet
        V1.3.2 states 5376 px where the user guide states 5496 px, which implies
        a 12.90 mm sensor against a published 13.1 mm.
        """
        imx183_as_the_datasheet_has_it = dict(
            model_label="Sony IMX183",
            chroma=Chroma.MONO,
            shutter_modes=frozenset({ShutterType.ROLLING, ShutterType.GLOBAL_RESET}),
            resolution_v=3672,
            pixel_size=2.4,
            size_format="Type 1",
            width=13.1,
            height=8.8,
            diagonal=15.9,
            quantum_efficiency_points=QuantumEfficiencyPoints(
                (QuantumEfficiencyPoint(Channel.MONO, 529.0, 0.80),)
            ),
            signal_metrics=SignalMetrics(
                temporal_dark_noise=6.0,
                saturation_capacity=14600,
                absolute_sensitivity_threshold=7.9,
                dynamic_range=65,
            ),
        )
        SensorModel(resolution_h=5496, **imx183_as_the_datasheet_has_it)  # user guide
        with pytest.raises(ValueError, match="derived width"):
            SensorModel(resolution_h=5376, **imx183_as_the_datasheet_has_it)

    def test_fires_on_a_corrupted_pixel_size(self) -> None:
        with pytest.raises(ValueError, match="derived width"):
            replace(IMX264, pixel_size=3.75)

    def test_published_dimensions_reproduce(self) -> None:
        for sensor in (IMX264, IMX287):
            width = sensor.resolution_h * sensor.pixel_size / 1000
            assert width == pytest.approx(sensor.width, abs=0.15)


class TestChromaChannels:
    def test_mono_record_carries_one_mono_point(self) -> None:
        assert IMX264.chroma is Chroma.MONO
        assert IMX264.quantum_efficiency_points is not None
        (point,) = IMX264.quantum_efficiency_points.points
        assert point.channel is Channel.MONO

    def test_colour_record_carries_rgb_and_no_mono(self) -> None:
        colour = ALVIUM_1800_C_507C.sensor
        assert colour.chroma is Chroma.COLOR
        assert colour.quantum_efficiency_points is not None
        assert colour.quantum_efficiency_points.channels == {
            Channel.RED,
            Channel.GREEN,
            Channel.BLUE,
        }

    def test_fires_when_mono_carries_a_colour_channel(self) -> None:
        with pytest.raises(ValueError, match="monochrome but carries"):
            replace(
                IMX264,
                quantum_efficiency_points=QuantumEfficiencyPoints(
                    (QuantumEfficiencyPoint(Channel.GREEN, 529.0, 0.57),)
                ),
            )

    def test_fires_when_colour_carries_a_mono_channel(self) -> None:
        colour = ALVIUM_1800_C_507C.sensor
        with pytest.raises(ValueError, match="colour but carries"):
            replace(
                colour,
                quantum_efficiency_points=QuantumEfficiencyPoints(
                    (QuantumEfficiencyPoint(Channel.MONO, 529.0, 0.64),)
                ),
            )


class TestAsColor:
    def test_inherits_saturation_and_dark_noise(self) -> None:
        """The CFA sits above the photodiode: well depth and readout are the same."""
        colour = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)
        assert colour.signal_metrics is not None and IMX264.signal_metrics is not None
        assert (
            colour.signal_metrics.saturation_capacity
            == IMX264.signal_metrics.saturation_capacity
        )
        assert (
            colour.signal_metrics.temporal_dark_noise
            == IMX264.signal_metrics.temporal_dark_noise
        )

    def test_drops_threshold_and_dynamic_range(self) -> None:
        """Both depend on QE, which AV never publish per channel."""
        colour = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)
        assert colour.signal_metrics is not None
        assert colour.signal_metrics.absolute_sensitivity_threshold is None
        assert colour.signal_metrics.dynamic_range is None

    def test_reads_qe_at_the_vendors_wavelength(self) -> None:
        colour = SensorModel.as_color(IMX264, green=0.57, blue=0.10, red=0.03)
        green = colour.quantum_efficiency_for(Channel.GREEN)
        assert green.wavelength == 529.0
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
        """Global reset shutter satisfies CAM-1, but only via GenICam.

        No candidate has it — the rolling-shutter models are excluded — so this
        builds one. The predicate must stay honest about the distinction, since
        the exclusion is a decision that could be revisited.
        """
        grs = replace(
            IMX264,
            shutter_modes=frozenset({ShutterType.ROLLING, ShutterType.GLOBAL_RESET}),
        )
        camera = replace(ALVIUM_1800_C_507M, sensor=grs)
        assert not camera.satisfies_cam1_unconditionally

    def test_readout_time_is_inferred_from_frame_rate(self) -> None:
        """CAM-1 needs readout time; max frame rate is the only handle on it."""
        assert ALVIUM_1800_C_507M.readout_time == pytest.approx(29_411_765, rel=1e-6)

    def test_exposure_ceiling_exceeds_readout(self) -> None:
        """A GRS strobe area exists only if exposure can outlast readout."""
        for camera in CSI2_CAMERAS:
            assert camera.exposure_max > camera.readout_time


class TestCameraModel:
    def test_rejects_an_empty_exposure_range(self) -> None:
        with pytest.raises(ValueError, match="exposure range"):
            replace(ALVIUM_1800_C_507M, exposure_min=10_000_000_001)

    def test_discrepancies_are_enumerable(self) -> None:
        """#11 needs the vendor-error set to report to Allied Vision."""
        flagged = {c.model_label for c in CSI2_CAMERAS if c.vendor_discrepancies}
        assert flagged == {
            "1800 C-040m",
            "1800 C-040c",
            "1800 C-291m",
            "1800 C-321m",
        }

    def test_clean_records_carry_no_discrepancies(self) -> None:
        assert ALVIUM_1800_C_507M.vendor_discrepancies == ()

    def test_lens_mounts_are_an_availability_set(self) -> None:
        assert ALVIUM_1800_C_507M.lens_mounts == frozenset({LensMount.C, LensMount.CS})
        # None is distinct from empty: unpublished, not "bare board".
        c321 = next(c for c in CSI2_CAMERAS if c.model_label == "1800 C-321m")
        assert c321.lens_mounts is None
        assert LensMount.S in ALVIUM_1800_C_040M.lens_mounts

    def test_records_are_frozen(self) -> None:
        with pytest.raises(AttributeError):
            ALVIUM_1800_C_507M.adc_bits = 10  # type: ignore[misc]
