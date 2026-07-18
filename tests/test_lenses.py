"""Tests for the lens records.

Like the sensor tests, these both check the records are well-formed and
deliberately corrupt a good record to assert the validation fires. The field of
view derivation is cross-checked against the datasheet's published angle of view.
"""

from dataclasses import replace

import pytest

from camsel.lenses import (
    C_6_F2_8,
    C_8_F2_4,
    C_12_F2_0,
    C_MOUNT_LENSES,
)
from camsel.models import LensMount
from camsel.sensors import IMX287, IMX421

#: Datasheet diagonal angle of view (degrees) at each lens's reference format.
#: Kept here, not on the model: the model derives FOV per sensor and uses these
#: only to guard the focal-length / image-circle transcription. The agreement is
#: loose (real lenses deviate from the pinhole model), so this catches gross
#: errors, not sub-degree ones — the same role the sensor geometry check plays.
PUBLISHED_DIAGONAL_AOV = {
    "C-6-F2.8-6MP-T1-1.8": 75.0,
    "C-8-F2.4-10MP-T2-3": 68.3,
    "C-12-F2.0-10MP-T2-3": 48.0,
    "C-16-F1.8-10MP-T2-3": 36.8,
    "C-25-F1.8-10MP-T2-3": 22.8,
    "C-35-F2.0-10MP-T2-3": 16.0,
    "C-50-F2.8-10MP-T2-3": 10.8,
}


def test_every_record_constructs() -> None:
    """Constructing at import means every record passed validation."""
    assert len(C_MOUNT_LENSES) == 7


def test_all_are_c_mount() -> None:
    assert all(lens.mount is LensMount.C for lens in C_MOUNT_LENSES)


class TestCoverage:
    def test_c6_underccovers_a_type_2_3_sensor(self) -> None:
        """The C-6's ⌀9.5 mm image circle does not reach a Type 2/3 diagonal."""
        assert IMX421.diagonal > 9.5
        assert not C_6_F2_8.covers(IMX421)

    def test_type_2_3_lenses_cover_a_type_2_3_sensor(self) -> None:
        for lens in C_MOUNT_LENSES:
            if lens.max_format == "Type 2/3":
                assert lens.covers(IMX421)

    def test_c6_covers_a_smaller_sensor(self) -> None:
        assert IMX287.diagonal < 9.5
        assert C_6_F2_8.covers(IMX287)


class TestRelativeIllumination:
    def test_is_one_over_fstop_squared(self) -> None:
        assert C_12_F2_0.relative_illumination == pytest.approx(0.25)

    def test_a_faster_lens_gathers_more(self) -> None:
        assert C_12_F2_0.relative_illumination > C_8_F2_4.relative_illumination


class TestFieldOfView:
    def test_reproduces_published_diagonal_aov(self) -> None:
        for lens in C_MOUNT_LENSES:
            derived = lens.angular_field_of_view(lens.image_circle)
            published = PUBLISHED_DIAGONAL_AOV[lens.model_label]
            assert derived == pytest.approx(published, abs=2.5)

    def test_narrows_with_focal_length(self) -> None:
        """A longer lens sees a smaller angle for the same sensor dimension."""
        assert C_8_F2_4.angular_field_of_view(8.8) > C_12_F2_0.angular_field_of_view(8.8)

    def test_horizontal_uses_sensor_width(self) -> None:
        derived = C_8_F2_4.angular_field_of_view(IMX421.width)
        assert derived == pytest.approx(57.6, abs=1.0)


class TestValidation:
    def test_fires_on_a_nonpositive_fstop(self) -> None:
        with pytest.raises(ValueError, match="f-stop must be positive"):
            replace(C_8_F2_4, fstop=0.0)

    def test_fires_on_a_nonpositive_focal_length(self) -> None:
        with pytest.raises(ValueError, match="focal length must be positive"):
            replace(C_8_F2_4, focal_length=-1.0)

    def test_fires_on_a_nonpositive_image_circle(self) -> None:
        with pytest.raises(ValueError, match="image circle must be positive"):
            replace(C_8_F2_4, image_circle=0.0)

    def test_fires_on_a_nonpositive_min_focus_distance(self) -> None:
        with pytest.raises(ValueError, match="min focus distance must be positive"):
            replace(C_8_F2_4, min_focus_distance=0.0)

    def test_fires_on_a_nonpositive_mass(self) -> None:
        with pytest.raises(ValueError, match="mass must be positive"):
            replace(C_8_F2_4, mass=0.0)

    def test_records_are_frozen(self) -> None:
        with pytest.raises(AttributeError):
            C_8_F2_4.fstop = 4.0  # type: ignore[misc]
