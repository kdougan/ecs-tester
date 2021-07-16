
from random import randint

from pygame import Vector2

from .components import Clickable
from .components import FollowMouse
from .components import ParticleEmitter
from .components import Physics
from .components import PlayerControlled
from .components import Position
from .components import Renderable
from .components import Size
from .components import Text
from .processors import RenderProcessor
from .types import AlignmentType
from .types import LayerType


def create_square(world, pos, size):
    world.create_entity(
        Position(*pos),
        Size(*size),
        Renderable(size=size, color=(255, 255, 255), layer=LayerType.ui)
    )


def create_mouse_entity(world):
    return world.create_entity(
        Position(0, 0),
        Size(20, 20),
        FollowMouse(),
    )


def create_button(world, position, size, text):
    ent = world.create_entity(
        Clickable(action=lambda: clicked(world)),
        Position(*position),
        Size(*size),
        Renderable(size=size, color=(100, 100, 100),
                   layer=LayerType.ui),
    )
    world.create_entity(
        Text(string=text, align=AlignmentType.center),
        Position(attach=ent, offset=(size[0]/2, size[1]/2)),
        Size(anchor=AlignmentType.center)
    )


def create_particle_emitter(world, position):
    world.create_entity(
        ParticleEmitter(rate=.01, particle_lifetime=4.0),
        Position(*position),
        Size(0, 0),
        Physics(velocity=((randint(0, 1000)-500), (randint(0, 1000)-500))),
        PlayerControlled()
    )


def clicked(world):
    renderer = world.get_processor(RenderProcessor)
    create_particle_emitter(
        world, (randint(0, renderer.display.get_width()), randint(0, renderer.display.get_height())))
