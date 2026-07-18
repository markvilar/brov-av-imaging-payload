"""Allied Vision's approved C-mount fixed focal length lenses.

The source for every field is the Allied Vision *C-Mount Lenses User Guide*
V1.2.0 (2025-Oct-16), committed at
``vendors/allied-vision/alvium-c-mount-lenses-user-guide.pdf``. These are the
vendor's own approved lenses, tested against the C-mount flange focal distance
(17.526 mm) and the Alvium sensor formats.

Scope is the seven fixed focal length lenses covering up to Type 2/3, the agreed
maximum sensor format. The 25 MP / Type 1.2 series (⌀19.3 mm image circle) is
excluded as built for larger formats.

Two provenance notes carried across the records:

- ``fstop`` is the *widest* aperture. The lenses have an adjustable aperture
  published as a range (e.g. F2.4–F16); the model stores the wide-open end.
- The datasheet's measured "Relative illumination" (a corner falloff percentage)
  is deliberately not stored — the model derives a relative-aperture figure of
  the same name from ``fstop`` instead. See issue #15.

The types these are built from live in :mod:`camsel.models`, and validate every
record on construction.

See issue #15.
"""

from camsel.models import LensModel, LensMount

#: Source of every field. Constant across the records, so not a field.
USER_GUIDE_VERSION = "V1.2.0"

#: Manufacturer, constant across the records.
VENDOR = "Allied Vision"

# The C-6 image circle (⌀9.5 mm, Type 1/1.8) is smaller than a Type 2/3 diagonal
# (~11 mm): it under-covers a full Type 2/3 sensor and vignettes on it. Kept as a
# short-focal option for smaller candidate sensors only. `LensModel.covers` is
# what flags this — see issue #15.
C_6_F2_8 = LensModel(
    model_label="C-6-F2.8-6MP-T1-1.8",
    vendor=VENDOR,
    product_code="18497",
    mount=LensMount.C,
    focal_length=6.0,
    image_circle=9.5,
    fstop=2.8,
    max_format="Type 1/1.8",
    min_focus_distance=0.1,
    mass=66,
)

C_8_F2_4 = LensModel(
    model_label="C-8-F2.4-10MP-T2-3",
    vendor=VENDOR,
    product_code="17870",
    mount=LensMount.C,
    focal_length=8.0,
    image_circle=11.0,
    fstop=2.4,
    max_format="Type 2/3",
    min_focus_distance=0.1,
    mass=103,
)

C_12_F2_0 = LensModel(
    model_label="C-12-F2.0-10MP-T2-3",
    vendor=VENDOR,
    product_code="17871",
    mount=LensMount.C,
    focal_length=12.0,
    image_circle=11.0,
    fstop=2.0,
    max_format="Type 2/3",
    min_focus_distance=0.1,
    mass=105,
)

C_16_F1_8 = LensModel(
    model_label="C-16-F1.8-10MP-T2-3",
    vendor=VENDOR,
    product_code="17872",
    mount=LensMount.C,
    focal_length=16.0,
    image_circle=11.0,
    fstop=1.8,
    max_format="Type 2/3",
    min_focus_distance=0.1,
    mass=90,
)

C_25_F1_8 = LensModel(
    model_label="C-25-F1.8-10MP-T2-3",
    vendor=VENDOR,
    product_code="17873",
    mount=LensMount.C,
    focal_length=25.0,
    image_circle=11.0,
    fstop=1.8,
    max_format="Type 2/3",
    min_focus_distance=0.15,
    mass=64,
)

C_35_F2_0 = LensModel(
    model_label="C-35-F2.0-10MP-T2-3",
    vendor=VENDOR,
    product_code="17874",
    mount=LensMount.C,
    focal_length=35.0,
    image_circle=11.0,
    fstop=2.0,
    max_format="Type 2/3",
    min_focus_distance=0.2,
    mass=98,
)

C_50_F2_8 = LensModel(
    model_label="C-50-F2.8-10MP-T2-3",
    vendor=VENDOR,
    product_code="17875",
    mount=LensMount.C,
    focal_length=50.0,
    image_circle=11.0,
    fstop=2.8,
    max_format="Type 2/3",
    min_focus_distance=0.3,
    mass=93,
)


#: The seven approved C-mount lenses covering up to Type 2/3. See issue #15.
C_MOUNT_LENSES: tuple[LensModel, ...] = (
    C_6_F2_8,
    C_8_F2_4,
    C_12_F2_0,
    C_16_F1_8,
    C_25_F1_8,
    C_35_F2_0,
    C_50_F2_8,
)
