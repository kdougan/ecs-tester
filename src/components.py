from random import randint
from typing import Any
from typing import Callable
from typing import Tuple

import pygame
from pygame import Vector2

from .types import AlignmentType
from .types import ParticleType
from .types import LayerType


class Position(Vector2):
    """
    A class to contain the Position data of a single component.

    Attributes:
        x : int
            The x coordinate of the component.
        y : int
            The y coordinate of the component.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, offset: Tuple[int, int] = (0, 0), attach: int = None):
        super().__init__(x, y)
        self.delta = Vector2(x, y)
        self.offset = Vector2(offset[0], offset[1])
        self.attach = attach


class Size(Vector2):
    """
    A class to contain the Size data of a single component.

    Attributes:
        width : int
            The width of the component.
        height : int
            The height of the component.
    """

    def __init__(self, width: float = 0.0, height: float = 0.0, anchor: AlignmentType = AlignmentType.top_left, scale: float = 1.0):
        super().__init__(width, height)
        self.anchor = anchor
        self.scale = scale

    @property
    def width(self) -> int:
        return self.x

    @width.setter
    def width(self, value: int) -> None:
        self.x = value

    @property
    def height(self) -> int:
        return self.y

    @height.setter
    def height(self, value: int) -> None:
        self.y = value


class Collider:
    """
    A class to contain the spatial data of a single spatial component.

    Attributes:
        anchor : AlignmentType
            The alignment of the component.
        fixed : bool
            True if the collider is fixed, False otherwise.
    """

    def __init__(self, anchor: AlignmentType = AlignmentType.center, fixed: bool = False) -> None:
        self.anchor = anchor
        self.fixed = fixed


class Collision:
    """
    A component to contain the spatial data of a single spatial component.

    Attributes:
        ent : int
            The entity ID of the component collided with.
    """

    def __init__(self, ent: int) -> None:
        self.ent = ent


class Physics:
    """
    A class to contain the physical data of a single Physics component.

    Atrtributes:
        mass : float
            The mass of the component.
        velocity : float
            The velocity of the component.
        acceleration : float
            The acceleration of the component.
    """

    def __init__(self,
                 velocity: Tuple[float, float] = (0.0, 0.0),
                 accelleration: Tuple[float, float] = (0.0, 0.0),
                 mass: float = 0.0, density: float = 0.0) -> None:
        self.velocity = Vector2(*velocity)
        self.accelleration = Vector2(*accelleration)
        self.mass = mass
        self.density = density


class Particle:
    """
    A class to contain the spatial data of a single Particle component.

    Attributes:
        lifetime : float
            The lifetime of the particle.
        age : float
            The age of the particle.   
        emitter : int
            The emitter of the particle.
    """

    def __init__(self, lifetime: float = 1.0, particle_type: ParticleType = ParticleType.none) -> None:
        self.lifetime = lifetime
        self.age = 0
        self.type = particle_type


class ParticleEmitter:
    """
    A class to contain the spatial data of a single particle system.

    Attributes:
        rate : float
            The rate of the particle system.
        last_spawn : float
            The time since the last spawn.
        particle_lifetime : float
            The lifetime of the particle.
        particle_count : int
            The number of particles in the system.
        particle_type : ParticleType
            The type of particle.
    """

    def __init__(self, rate: float = 1.0, particle_lifetime: float = 1.0, particle_count: int = None, particle_type: ParticleType = None):
        self.rate = rate
        self.last_spawn = rate
        self.particle_lifetime = particle_lifetime
        self.particle_count = particle_count
        self.particle_type = particle_type
        self.particles = set()


class Renderable:
    """
    A class to contain the renderable data of a single spatial component.

    Attributes:
        size : tuple
            The size of the renderable (required if no 'file_path').
        file_path : str
            The path to the image file (optional. overwrites 'size').
        surface : pygame.Surface
            The the renderable surface.
        visible : bool
            Whether or not the renderable is visible.
        is_animated : bool
            Whether or not the renderable is animated.
    """

    paths = {}

    def __init__(self, size: tuple = None, file_path: str = None, visible: bool = True, is_animated: bool = False, color: tuple = None, layer: LayerType = LayerType.none) -> None:
        self.file_path = file_path
        self.is_animated = is_animated
        self.surface = None
        self.size = size
        self.visible = visible
        self.layer = layer

        if file_path:
            if file_path not in self.paths:
                self.paths[file_path] = pygame.image.load(file_path)
                self.paths[file_path].convert_alpha()
            self.surface = self.paths[file_path]
            self.surface.convert_alpha()
        else:
            if not self.size:
                raise AttributeError('missing size attr')
            self.surface = pygame.Surface(self.size)
            rand_color = (randint(0, 255),
                          randint(0, 255),
                          randint(0, 255))
            self.surface.fill(color or rand_color)

    @property
    def has_image(self) -> bool:
        return self.file_path is not None


class PlayerControlled:
    def __init__(self, speed: float = 4.0):
        self.speed = speed


class Text:
    def __init__(self, string: str, size: int = 1,
                 color: tuple = (255, 255, 255),
                 align: AlignmentType = AlignmentType.top_left,
                 offset_x: float = 0.0, offset_y: float = 0.0,
                 attach: int = None,
                 visible: bool = True):
        self.string = string
        self.size = size
        self.color = color
        self.align = align
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.attach = attach
        self.visible = visible
        self.dirty = True


class FollowMouse:
    def __init__(self, speed: float = 0.0):
        self.speed = speed


class Clickable:
    def __init__(self, action: Callable):
        self.action = action
        self.pressed = False
        self.pressed_start_time = None
        self.pressed_start = 0.0


class Camera:
    def __init__(self, position: Tuple[float, float] = (0.0, 0.0),
                 zoom: float = 1.0,
                 target: int = None):
        self.position = Vector2(*position)
        self.zoom = zoom
        self.target = target
        self.offset = Vector2(0.0, 0.0)
        self.dirty = True
