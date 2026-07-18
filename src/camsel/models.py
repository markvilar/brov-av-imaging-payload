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

    Channel matters as much as wavelength: a colour record's QE is read off the
    *green* curve, and without the channel it is indistinguishable from a
    monochrome measurement.

    Attributes:
        channel: Which colour channel the measurement is for.
        wavelength: Wavelength of the measurement, in nanometres.
        value: Quantum efficiency as a fraction in [0.0, 1.0].
    """

    channel: Channel
    wavelength: float
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"quantum efficiency is a fraction, got {self.value}")


@dataclass(frozen=True)
class QuantumEfficiencyPoints:
    """QE sampled at one wavelength, one point per channel.

    A monochrome sensor holds a single `MONO` point; a colour sensor holds
    `RED`/`GREEN`/`BLUE`. Whether the channels are consistent with the sensor's
    chroma is checked on :class:`SensorModel`, which is what knows the chroma.

    Attributes:
        points: One :class:`QuantumEfficiencyPoint` per channel, no duplicates.
    """

    points: tuple[QuantumEfficiencyPoint, ...]

    def __post_init__(self) -> None:
        channels = [p.channel for p in self.points]
        if len(set(channels)) != len(channels):
            raise ValueError(f"duplicate QE channel in {channels}")

    @property
    def channels(self) -> frozenset[Channel]:
        return frozenset(p.channel for p in self.points)

    def for_channel(self, channel: Channel) -> QuantumEfficiencyPoint:
        for point in self.points:
            if point.channel is channel:
                return point
        raise KeyError(f"no {channel} measurement")


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

    def at(self, wavelength: float) -> float:
        """Linearly interpolate this channel's QE at an arbitrary wavelength."""
        ordered = sorted(self.points, key=lambda p: p.wavelength)
        xs = [p.wavelength for p in ordered]
        ys = [p.value for p in ordered]
        if not xs or not xs[0] <= wavelength <= xs[-1]:
            raise ValueError(f"{wavelength} nm is outside the sampled range")
        for i in range(1, len(xs)):
            if wavelength <= xs[i]:
                span = xs[i] - xs[i - 1]
                if span == 0:
                    return ys[i]
                fraction = (wavelength - xs[i - 1]) / span
                return ys[i - 1] + fraction * (ys[i] - ys[i - 1])
        return ys[-1]


@dataclass(frozen=True)
class QuantumEfficiencyCurves:
    """QE sampled across wavelength, one curve per channel.

    Populated only for shortlist finalists; digitising every family is
    disproportionate. Needed to evaluate QE at a strobe wavelength other than the
    529 nm Allied Vision quote.

    Attributes:
        curves: One :class:`QuantumEfficiencyCurve` per channel, no duplicates.
    """

    curves: tuple[QuantumEfficiencyCurve, ...]

    def __post_init__(self) -> None:
        channels = [c.channel for c in self.curves]
        if len(set(channels)) != len(channels):
            raise ValueError(f"duplicate QE curve channel in {channels}")

    def for_channel(self, channel: Channel) -> QuantumEfficiencyCurve:
        for curve in self.curves:
            if curve.channel is channel:
                return curve
        raise KeyError(f"no {channel} curve")


@dataclass(frozen=True)
class SignalMetrics:
    """The achromatic signal figures from a model's EMVA 1288 datasheet block:
    the noise floor, the full-well ceiling, and the dynamic range between them.

    Quantum efficiency — the one *chromatic* figure in the EMVA block — lives
    separately, in :class:`QuantumEfficiencyPoints` on the sensor. Everything
    here is colour-independent: dark noise and full-well are properties of the
    photodiode and readout chain, unchanged by a colour filter array, which is
    why a colour record inherits them from its monochrome sibling.

    Measurements, not specifications. Allied Vision state these are "typical
    values for monochrome models measured without optical filter" — typical, not
    guaranteed. Optional on a sensor because Allied Vision do not publish them for
    every model: some datasheets have no Imaging performance section at all.

    Attributes:
        temporal_dark_noise: Read noise, the noise floor, in electrons (e⁻).
        saturation_capacity: Full-well capacity, the ceiling, in electrons (e⁻).
        absolute_sensitivity_threshold: Darkest detectable signal (SNR = 1), in
            electrons (e⁻). Noise-derived. None for colour, where the QE it
            depends on is not published per channel.
        dynamic_range: Saturation capacity over threshold, in decibels (dB).
            Noise-dependent through the threshold. None for colour, as above.
    """

    temporal_dark_noise: float
    saturation_capacity: float
    absolute_sensitivity_threshold: float | None
    dynamic_range: float | None

    def __post_init__(self) -> None:
        """Dynamic range must follow from saturation capacity and threshold.

        Skipped where either is absent, i.e. colour. This is the redundancy that
        surfaced the C-040, whose datasheet states a saturation capacity 10x too
        high.
        """
        if self.dynamic_range is None or self.absolute_sensitivity_threshold is None:
            return
        derived = 20 * math.log10(
            self.saturation_capacity / self.absolute_sensitivity_threshold
        )
        if abs(derived - self.dynamic_range) > DYNAMIC_RANGE_TOLERANCE_DB:
            raise ValueError(
                f"dynamic range derived from saturation capacity and threshold "
                f"is {derived:.1f} dB, but {self.dynamic_range} dB is published"
            )


@dataclass(frozen=True)
class SensorModel:
    """Silicon-level facts, split from the camera so that features needing only
    sensor attributes need not carry a camera.

    These are *not* shared between models in practice: the 23 CSI-2 candidates
    use 23 distinct sensors. The STEP *file* is shared across a sensor family;
    the silicon never is.

    Attributes:
        model_label: Sensor part number, e.g. "Sony IMX264".
        chroma: Monochrome or colour variant.
        shutter_modes: Every shutter mode the sensor supports (an availability
            set; mode is selectable at runtime, not an order-time variant).
        resolution_h: Horizontal active pixels.
        resolution_v: Vertical active pixels.
        pixel_size: Pixel pitch, in micrometres (µm), assumed square.
        size_format: Optical format label, e.g. "Type 2/3". A size class, not a
            true dimension — see width/height/diagonal for those.
        width: Active-area width, in millimetres (mm).
        height: Active-area height, in millimetres (mm).
        diagonal: Active-area diagonal, in millimetres (mm).
        quantum_efficiency_points: QE at 529 nm, one point per channel, or None
            where the datasheet publishes no EMVA block.
        quantum_efficiency_curves: QE across wavelength, one curve per channel,
            or None until digitised for a shortlist finalist.
        signal_metrics: Achromatic noise/dynamic-range figures, or None where
            unpublished. These three fields are the pieces of the datasheet's
            EMVA block, split by meaning: QE is chromatic, the metrics are not.
    """

    model_label: str  # "Sony IMX264"
    chroma: Chroma

    # Availability set: the user guide lists every mode the sensor supports
    # (the IMX183 reads "Rolling shutter (RS), Global reset shutter (GRS)").
    # Mode is selectable at runtime, not an order-time variant.
    shutter_modes: frozenset[ShutterType]

    resolution_h: int
    resolution_v: int
    pixel_size: float

    # Published active area, from the user guide's `Sensor size` row. Redundant
    # against resolution x pixel size — stored *because* that redundancy is the
    # check, the same reasoning that keeps the EMVA block whole.
    size_format: str  # "Type 2/3"
    width: float
    height: float
    diagonal: float

    # The datasheet's EMVA 1288 block, split by meaning into three optional
    # pieces. All three come from the same table and are absent together for the
    # six candidates whose datasheets have no Imaging performance section — but
    # they are separate so provenance can diverge later (e.g. taking a sensor
    # maker's QE for a model Allied Vision never characterised).
    quantum_efficiency_points: QuantumEfficiencyPoints | None = None
    quantum_efficiency_curves: QuantumEfficiencyCurves | None = None
    signal_metrics: SignalMetrics | None = None

    def __post_init__(self) -> None:
        self._check_chroma_channels()
        self._check_sensor_geometry()

    @property
    def pixel_area(self) -> float:
        """Photon-collecting area per pixel, in µm². Drives the low-light budget."""
        return self.pixel_size**2

    def quantum_efficiency_for(self, channel: Channel) -> QuantumEfficiencyPoint:
        if self.quantum_efficiency_points is None:
            raise KeyError(f"{self.model_label} has no QE measurements")
        try:
            return self.quantum_efficiency_points.for_channel(channel)
        except KeyError:
            raise KeyError(f"{self.model_label} has no {channel} measurement") from None

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
        the datasheet's chart at the same wavelength Allied Vision quote for
        monochrome. They state the QE measurement uncertainty is +/-10%, and that
        colour curves are measured with an IR cut filter where the monochrome
        ones are not.

        Deriving colour through this constructor rather than by hand is what
        makes "which values are inferred?" answerable: everything but the three
        QE values came from a monochrome record that was itself checked.
        """
        if mono.chroma is not Chroma.MONO:
            raise ValueError(f"{mono.model_label} is not a monochrome record")
        if mono.quantum_efficiency_points is None or mono.signal_metrics is None:
            raise ValueError(
                f"{mono.model_label} has no measurements to inherit; "
                f"Allied Vision publish no EMVA block for it"
            )
        wavelength = mono.quantum_efficiency_for(Channel.MONO).wavelength
        return replace(
            mono,
            chroma=Chroma.COLOR,
            quantum_efficiency_points=QuantumEfficiencyPoints(
                (
                    QuantumEfficiencyPoint(Channel.RED, wavelength, red),
                    QuantumEfficiencyPoint(Channel.GREEN, wavelength, green),
                    QuantumEfficiencyPoint(Channel.BLUE, wavelength, blue),
                )
            ),
            signal_metrics=SignalMetrics(
                temporal_dark_noise=mono.signal_metrics.temporal_dark_noise,
                saturation_capacity=mono.signal_metrics.saturation_capacity,
                absolute_sensitivity_threshold=None,
                dynamic_range=None,
            ),
            quantum_efficiency_curves=None,
        )

    def _check_chroma_channels(self) -> None:
        """The QE channels must agree with the sensor's chroma.

        Vacuous where no QE is published: there are no measurements to disagree
        with the chroma. Duplicate-channel checks live on the QE containers; this
        is the cross-check the containers cannot do, since only the sensor knows
        its chroma.
        """
        if self.quantum_efficiency_points is None:
            return
        channels = self.quantum_efficiency_points.channels
        if self.chroma is Chroma.MONO:
            if channels != {Channel.MONO}:
                raise ValueError(
                    f"{self.model_label} is monochrome but carries {set(channels)}"
                )
        elif not channels or not channels <= {Channel.RED, Channel.GREEN, Channel.BLUE}:
            raise ValueError(
                f"{self.model_label} is colour but carries {set(channels)}"
            )

    def _check_sensor_geometry(self) -> None:
        """resolution x pixel size must reproduce the published dimensions.

        Guards transcription of resolution, pixel size and sensor size against
        each other. This is the redundancy that corroborated the C-2050, whose
        datasheet states a resolution 120 px narrower than the user guide.
        """
        width = self.resolution_h * self.pixel_size / 1000
        height = self.resolution_v * self.pixel_size / 1000
        diagonal = math.hypot(width, height)
        for name, derived, published in (
            ("width", width, self.width),
            ("height", height, self.height),
            ("diagonal", diagonal, self.diagonal),
        ):
            if abs(derived - published) > SENSOR_SIZE_TOLERANCE_MM:
                raise ValueError(
                    f"{self.model_label}: derived {name} {derived:.2f} mm "
                    f"disagrees with published {published} mm"
                )


@dataclass(frozen=True)
class LensModel:
    """A fixed focal length lens, from a vendor's approved-lens datasheet.

    Stores only the two intrinsic optical facts the imaging geometry needs —
    focal length and image circle — plus the aperture and catalogue metadata.
    Field of view is deliberately *not* stored: it is a property of the
    lens+sensor pair, not the lens, so it is derived against a
    :class:`SensorModel` via :meth:`angular_field_of_view`. This mirrors
    :class:`SensorModel`, which stores raw facts and derives ``readout_time``.

    See issue #15.

    Attributes:
        model_label: Vendor model designation, e.g. "C-8-F2.4-10MP-T2-3".
        vendor: Manufacturer, e.g. "Allied Vision".
        product_code: Vendor order code, e.g. "17870".
        mount: Lens mount.
        focal_length: Focal length, in millimetres (mm).
        image_circle: Maximum image circle the lens covers, in millimetres (mm).
            The coverage handle: a lens images a sensor cleanly only where this
            reaches the sensor diagonal — see :meth:`covers`.
        fstop: Widest aperture (lowest f-number). The AV lenses have an
            adjustable aperture published as a range (e.g. F2.4–F16); this stores
            the wide-open end, the low-light-relevant one. See issue #15.
        max_format: Largest sensor format the lens is rated for, e.g. "Type 2/3".
        min_focus_distance: Closest focus, object to front element, in metres (m).
        mass: Mass, in grams (g).
    """

    model_label: str
    vendor: str
    product_code: str
    mount: LensMount
    focal_length: float
    image_circle: float
    fstop: float
    max_format: str
    min_focus_distance: float
    mass: float

    def __post_init__(self) -> None:
        if self.fstop <= 0:
            raise ValueError(f"{self.model_label}: f-stop must be positive")
        if self.focal_length <= 0:
            raise ValueError(f"{self.model_label}: focal length must be positive")
        if self.image_circle <= 0:
            raise ValueError(f"{self.model_label}: image circle must be positive")
        if self.min_focus_distance <= 0:
            raise ValueError(f"{self.model_label}: min focus distance must be positive")
        if self.mass <= 0:
            raise ValueError(f"{self.model_label}: mass must be positive")

    @property
    def relative_illumination(self) -> float:
        """Relative light-gathering, ``1 / fstop**2``.

        Derived from the aperture, so nothing is transcribed. This is a
        relative-aperture figure and is *not* the datasheet's like-named
        "Relative illumination" row, which is a measured corner-vs-centre falloff
        and is not stored. See issue #15.
        """
        return 1.0 / self.fstop**2

    def angular_field_of_view(self, dimension: float) -> float:
        """Angular field of view, in degrees, subtended by a sensor dimension.

        ``dimension`` is a sensor extent in millimetres — pass the active width,
        height, or diagonal to get the corresponding FOV. Rectilinear lens
        focused at infinity: ``2 * atan(dimension / (2 * focal_length))``. Valid
        only where the lens :meth:`covers` the sensor; beyond the image circle the
        true FOV is clipped by the optics, not the sensor.
        """
        return math.degrees(2 * math.atan(dimension / (2 * self.focal_length)))

    def covers(self, sensor: SensorModel) -> bool:
        """Whether the image circle reaches the sensor's diagonal.

        False means the sensor corners fall outside the projected image and
        vignette — the case the C-6 hits on a full Type 2/3 sensor.
        """
        return self.image_circle >= sensor.diagonal


@dataclass(frozen=True)
class CameraModel:
    """An orderable Alvium model. This is what an ADR and a purchase order name.

    Attributes:
        model_label: Model designation with the vendor's chroma suffix, e.g.
            "1800 C-507m" (mono) / "1800 C-507c" (colour).
        series: Product series, e.g. "Alvium 1800 C".
        sensor: The image sensor this model is built on.
        interface: Host interface (CSI-2 for every candidate).
        adc_bits: ADC converter depth, in bits. None where Allied Vision publish
            only the selectable output depth, not the converter depth — the user
            guide labels the two identically and the datasheet disambiguates, so
            a model with no datasheet has no published value.
        max_frame_rate: Maximum frame rate at full resolution, in frames per
            second. Kept for its timing role, not its rate: readout time ≈
            1 / max_frame_rate is the only published handle on scan-out time,
            which CAM-1's global-reset condition needs.
        exposure_min: Minimum exposure time, in nanoseconds.
        exposure_max: Maximum exposure time, in nanoseconds. Nanoseconds because
            the sync subsystem reasons in ns; the vendor publishes µs and s.
        lens_mounts: Orderable mounts (an availability set). Empty means a
            bare-board variant with no mount; None means unpublished — mounts
            appear only in datasheets, never the user guide's per-model table.
        power_consumption: Typical power consumption, in watts (W).
        mass: Mass, in grams (g).
        operating_temp_min: Minimum operating temperature, in degrees Celsius.
        operating_temp_max: Maximum operating temperature, in degrees Celsius.
        vendor_discrepancies: Recorded source errors or disagreements; empty for
            a clean record.
    """

    model_label: str
    series: str
    sensor: SensorModel
    interface: Interface
    adc_bits: int | None
    max_frame_rate: float
    exposure_min: int
    exposure_max: int
    lens_mounts: frozenset[LensMount] | None
    power_consumption: float
    mass: float
    operating_temp_min: float
    operating_temp_max: float

    # Where a source is known to be wrong, or two disagree, the disagreement is
    # recorded rather than silently resolved. Empty for a clean record. This is
    # not a systematic diff of every datasheet against the user guide — it is
    # what has been found so far, which makes the vendor-error set enumerable.
    vendor_discrepancies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.exposure_min >= self.exposure_max:
            raise ValueError(
                f"{self.model_label}: exposure range "
                f"{self.exposure_min}-{self.exposure_max} ns is empty"
            )

    @property
    def readout_time(self) -> int:
        """Time to scan out a full frame, in nanoseconds, inferred from the
        maximum frame rate.

        CAM-1 needs this: with global reset shutter the strobe must fire before
        the first line reads out, and with plain rolling shutter a common
        integration window exists only where exposure exceeds this.
        """
        return round(1e9 / self.max_frame_rate)

    @property
    def satisfies_cam1_unconditionally(self) -> bool:
        """True where a global shutter makes the strobe timing trivial.

        Global reset shutter also satisfies CAM-1, but only in a dark scene and
        only through GenICam for CSI-2 Access, which is an open question in
        CONTEXT.md. See requirements/camera-requirements.md.
        """
        return ShutterType.GLOBAL in self.sensor.shutter_modes
