from .util import ValueOrderedEnum


class ParticleType(ValueOrderedEnum):
    none = 0
    smoke = 1
    fire = 2
    water = 3
    dust = 4
    snow = 5
    fog = 6
    rain = 7


class AlignmentType(ValueOrderedEnum):
    top_left = 0
    top_center = 1
    top_right = 2
    center_left = 3
    center = 4
    center_right = 5
    bottom_left = 6
    bottom_center = 7
    bottom_right = 8


class LayerType(ValueOrderedEnum):
    none = 0
    background = 1
    objects = 2
    foreground = 3
    ui = 4
    cursors = 5
