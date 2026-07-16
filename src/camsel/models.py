"""Record types for Allied Vision Alvium cameras and their sensors.

The types only; the concrete records live in :mod:`camsel.sensors`.

These records validate themselves on construction. Two published quantities are
redundant against others, and that redundancy is kept deliberately rather than
normalised away: it is what catches a transcription slip across ~50 records.

See issue #10.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from enum import StrEnum, auto

#: Allied Vision round dynamic range to whole dB.
DYNAMIC_RANGE_TOLERANCE_DB = 1.0

#: Allied Vision round the sensor dimensions to 0.1 mm.
SENSOR_SIZE_TOLERANCE_MM = 0.15


class Chroma(StrEnum):
    """What you order — a monochrome or a colour variant of a model."""

    MONO = auto()
    COLOR = auto()


class Channel(StrEnum):
    """What was measured.

    Distinct from :class:`Chroma`: a colour sensor is one orderable variant but
    yields three measured channels.
    """

    MONO = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()


class ShutterType(StrEnum):
    """Shutter modes a sensor can be operated in.

    ``GLOBAL_RESET`` matters disproportionately here: it lets a rolling-shutter
    sensor produce a globally consistent image in a dark scene, because all rows
    begin integrating together and the strobe fires into the common window. See
    ``requirements/camera-requirements.md`` (CAM-1).
    """

    GLOBAL = auto()
    ROLLING = auto()
    GLOBAL_RESET = auto()


class Interface(StrEnum):
    """Host interface of an Alvium product line.

    "Flex" is deliberately absent: it is a form factor, not a bus, and ships in
    both CSI-2 and USB variants.
    """

    CSI2 = auto()
    USB3 = auto()
    GIGE = auto()


class LensMount(StrEnum):
    """Mount options a model can be ordered with."""

    C = auto()
    CS = auto()
    S = auto()  # M12


@dataclass(frozen=True)
class QuantumEfficiencyPoint:
    """QE of one channel at one wavelength.

    Both conditions travel with the measurement rather than being baked into a
    field name, so a point states what it is. Channel matters as much as
    wavelength: a colour record's QE is read off the *green* curve, and without
    the channel it is indistinguishable from a monochrome measurement.
    """

    channel: Channel
    wavelength_nm: float
    value: float  # fraction, 0.0-1.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"quantum efficiency is a fraction, got {self.value}")


@dataclass(frozen=True)
class QuantumEfficiencyCurve:
    """One channel's QE sampled across wavelength, digitised from the chart.

    One channel per curve: interpolating across mixed channels is meaningless.
    """

    channel: Channel
    points: tuple[QuantumEfficiencyPoint, ...]

    def __post_init__(self) -> None:
        if any(p.channel is not self.channel for p in self.points):
            raise ValueError(f"curve for {self.channel} holds foreign channels")

    def at(self, wavelength_nm: float) -> float:
        """Linearly interpolate this channel's QE at an arbitrary wavelength."""
        ordered = sorted(self.points, key=lambda p: p.wavelength_nm)
        xs = [p.wavelength_nm for p in ordered]
        ys = [p.value for p in ordered]
        if not xs or not xs[0] <= wavelength_nm <= xs[-1]:
            raise ValueError(f"{wavelength_nm} nm is outside the sampled range")
        for i in range(1, len(xs)):
            if wavelength_nm <= xs[i]:
                span = xs[i] - xs[i - 1]
                if span == 0:
                    return ys[i]
                fraction = (wavelength_nm - xs[i - 1]) / span
                return ys[i - 1] + fraction * (ys[i] - ys[i - 1])
        return ys[-1]


@dataclass(frozen=True)
class SensorModel:
    """Silicon-level facts, split from the camera so that features needing only
    sensor attributes need not carry a camera.

    These are *not* shared between models in practice: the 26 CSI-2 candidates
    use 26 distinct sensors. The STEP *file* is shared across a sensor family;
    the silicon never is.
    """

    model_label: str  # "Sony IMX264"
    chroma: Chroma

    # Availability set: the user guide lists every mode the sensor supports
    # (the IMX183 reads "Rolling shutter (RS), Global reset shutter (GRS)").
    # Mode is selectable at runtime, not an order-time variant.
    shutter_modes: frozenset[ShutterType]

    resolution_h: int
    resolution_v: int
    pixel_size_um: float

    # Published active area, from the user guide's `Sensor size` row. Redundant
    # against resolution x pixel size — stored *because* that redundancy is the
    # check, the same reasoning that keeps the EMVA block whole.
    sensor_format: str  # "Type 2/3"
    sensor_width_mm: float
    sensor_height_mm: float
    sensor_diagonal_mm: float

    # EMVA 1288 Release 3.1 block, from the datasheet. Published as "typical
    # values for monochrome models measured without optical filter", so a
    # colour record cannot take these as published — see `as_color`.
    quantum_efficiency: tuple[QuantumEfficiencyPoint, ...]
    temporal_dark_noise_e: float
    saturation_capacity_e: float

    # None for colour: both depend on QE, and Allied Vision publish neither per
    # channel, in the datasheets or the user guide. Nothing in the ranking
    # consumes them — they are stored because their redundancy against
    # saturation capacity is the transcription check.
    absolute_sensitivity_threshold_e: float | None
    dynamic_range_db: float | None

    # One curve per channel. Populated only for shortlist finalists; digitising
    # every family is disproportionate. Needed to evaluate QE at a strobe
    # wavelength other than the 529 nm Allied Vision quote.
    quantum_efficiency_curves: tuple[QuantumEfficiencyCurve, ...] = ()

    def __post_init__(self) -> None:
        self._check_chroma_channels()
        self._check_sensor_geometry()
        self._check_emva_redundancy()

    @property
    def pixel_area_um2(self) -> float:
        """Photon-collecting area per pixel. Drives the low-light budget."""
        return self.pixel_size_um**2

    def quantum_efficiency_for(self, channel: Channel) -> QuantumEfficiencyPoint:
        for point in self.quantum_efficiency:
            if point.channel is channel:
                return point
        raise KeyError(f"{self.model_label} has no {channel} measurement")

    @classmethod
    def as_color(
        cls, mono: SensorModel, green: float, blue: float, red: float
    ) -> SensorModel:
        """Build the colour variant from its monochrome sibling.

        Allied Vision publish no EMVA block for colour, so a colour record is
        derived, not transcribed. Saturation capacity and temporal dark noise
        carry over — the colour filter array is a dye layer above the photodiode
        and changes neither well depth nor the readout chain — while the
        sensitivity threshold and dynamic range become None, because both depend
        on a QE that is never published per channel.

        The three QE values are the only genuinely new numbers, read by eye off
        the datasheet's QE chart at the same wavelength Allied Vision quote for
        monochrome. They state the QE measurement uncertainty is +/-10%, and that
        colour curves are measured with an IR cut filter where the monochrome
        ones are not.

        Deriving colour through this constructor rather than by hand is what
        makes "which values are inferred?" answerable: everything but the three
        QE values came from a monochrome record that was itself checked.
        """
        if mono.chroma is not Chroma.MONO:
            raise ValueError(f"{mono.model_label} is not a monochrome record")
        wavelength = mono.quantum_efficiency_for(Channel.MONO).wavelength_nm
        return replace(
            mono,
            chroma=Chroma.COLOR,
            quantum_efficiency=(
                QuantumEfficiencyPoint(Channel.RED, wavelength, red),
                QuantumEfficiencyPoint(Channel.GREEN, wavelength, green),
                QuantumEfficiencyPoint(Channel.BLUE, wavelength, blue),
            ),
            absolute_sensitivity_threshold_e=None,
            dynamic_range_db=None,
            quantum_efficiency_curves=(),
        )

    def _check_chroma_channels(self) -> None:
        """Chroma and channel must agree."""
        channels = {p.channel for p in self.quantum_efficiency}
        if len(channels) != len(self.quantum_efficiency):
            raise ValueError(f"{self.model_label} repeats a QE channel")
        if self.chroma is Chroma.MONO:
            if channels != {Channel.MONO}:
                raise ValueError(
                    f"{self.model_label} is monochrome but carries {channels}"
                )
        elif not channels or not channels <= {Channel.RED, Channel.GREEN, Channel.BLUE}:
            raise ValueError(f"{self.model_label} is colour but carries {channels}")
        curve_channels = [c.channel for c in self.quantum_efficiency_curves]
        if len(set(curve_channels)) != len(curve_channels):
            raise ValueError(f"{self.model_label} repeats a QE curve channel")

    def _check_sensor_geometry(self) -> None:
        """resolution x pixel size must reproduce the published dimensions.

        Guards transcription of resolution, pixel size and sensor size against
        each other. This is the redundancy that corroborated the C-2050, whose
        datasheet states a resolution 120 px narrower than the user guide.
        """
        width = self.resolution_h * self.pixel_size_um / 1000
        height = self.resolution_v * self.pixel_size_um / 1000
        diagonal = math.hypot(width, height)
        for name, derived, published in (
            ("width", width, self.sensor_width_mm),
            ("height", height, self.sensor_height_mm),
            ("diagonal", diagonal, self.sensor_diagonal_mm),
        ):
            if abs(derived - published) > SENSOR_SIZE_TOLERANCE_MM:
                raise ValueError(
                    f"{self.model_label}: derived {name} {derived:.2f} mm "
                    f"disagrees with published {published} mm"
                )

    def _check_emva_redundancy(self) -> None:
        """Dynamic range must follow from saturation capacity and threshold.

        Skipped for colour records, which have neither. This is the redundancy
        that surfaced the C-040, whose datasheet states a saturation capacity
        10x too high.
        """
        if (
            self.dynamic_range_db is None
            or self.absolute_sensitivity_threshold_e is None
        ):
            return
        derived = 20 * math.log10(
            self.saturation_capacity_e / self.absolute_sensitivity_threshold_e
        )
        if abs(derived - self.dynamic_range_db) > DYNAMIC_RANGE_TOLERANCE_DB:
            raise ValueError(
                f"{self.model_label}: dynamic range derived from saturation "
                f"capacity and threshold is {derived:.1f} dB, but "
                f"{self.dynamic_range_db} dB is published"
            )


@dataclass(frozen=True)
class CameraModel:
    """An orderable Alvium model. This is what an ADR and a purchase order name."""

    # Carries the chroma suffix, matching the vendor: the user guide names the
    # variants "1800 C-508m (monochrome)" and "1800 C-508c (color)".
    model_label: str  # "1800 C-507m" / "1800 C-507c"
    series: str  # "Alvium 1800 C"
    sensor: SensorModel

    interface: Interface
    adc_bits: int

    # Kept for its timing role, not its frame rate: readout time ~ 1 / max_fps
    # is the only published handle on how long a frame takes to scan out, and
    # CAM-1's global-reset condition needs it — the strobe area is bounded by
    # the first line's readout.
    max_frame_rate_fps: float

    # Nanoseconds because the sync subsystem reasons in ns (trigger jitter,
    # flash duration) and integer ns avoids float rounding across that boundary.
    # The vendor publishes us and s.
    exposure_min_ns: int
    exposure_max_ns: int

    # Availability set, not a value. Empty for bare-board variants.
    lens_mounts: frozenset[LensMount]

    power_consumption_w: float
    mass_g: float
    operating_temp_min_c: float
    operating_temp_max_c: float

    # Where a source is known to be wrong, or two disagree, the disagreement is
    # recorded rather than silently resolved. Empty for a clean record. This is
    # not a systematic diff of every datasheet against the user guide — it is
    # what has been found so far, which makes the vendor-error set enumerable.
    vendor_discrepancies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.exposure_min_ns >= self.exposure_max_ns:
            raise ValueError(
                f"{self.model_label}: exposure range "
                f"{self.exposure_min_ns}-{self.exposure_max_ns} ns is empty"
            )

    @property
    def readout_time_ns(self) -> int:
        """Time to scan out a full frame, inferred from the maximum frame rate.

        CAM-1 needs this: with global reset shutter the strobe must fire before
        the first line reads out, and with plain rolling shutter a common
        integration window exists only where exposure exceeds this.
        """
        return round(1e9 / self.max_frame_rate_fps)

    @property
    def satisfies_cam1_unconditionally(self) -> bool:
        """True where a global shutter makes the strobe timing trivial.

        Global reset shutter also satisfies CAM-1, but only in a dark scene and
        only through GenICam for CSI-2 Access, which is an open question in
        CONTEXT.md. See requirements/camera-requirements.md.
        """
        return ShutterType.GLOBAL in self.sensor.shutter_modes
