import random
from time import time

import pygame
from pygame import Vector2

from .components import Clickable
from .components import Collider
from .components import FollowMouse
from .components import Particle
from .components import ParticleEmitter
from .components import Physics
from .components import PlayerControlled
from .components import Renderable
from .components import Text
from .components import Position
from .components import Size
from .modules.esper import Processor
from .types import AlignmentType
from .util import char_widths


class RenderProcessor(Processor):

    text_surfs = {}

    def __init__(self):
        super().__init__()
        self.scale = 2.0
        self.size = self.width, self.height = 800, 600
        self.window = pygame.display.set_mode(self.size,
                                              pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.display = pygame.Surface(
            (int(self.width/self.scale), int(self.height/self.scale)))

        self.font_image = pygame.image.load('./src/assets/font.png').convert()
        self.font_image.set_colorkey((255, 255, 255))

        self.test_fill = pygame.image.load(
            './src/assets/test_fill.png').convert()

    def process(self, dt) -> None:
        self.display.fill((30, 10, 30))

        layers = {}

        for ent, (renderable, position, size) in self.world.get_components(Renderable, Position, Size):
            if not renderable.visible:
                continue
            text = self.world.try_component(ent, Text)
            if text:
                surf = self.get_text_surf(ent)
            else:
                surf = pygame.transform.scale(
                    renderable.surface,
                    (max(int(size.width * size.scale), 0),
                     max(int(size.height * size.scale), 0)))

            anchor = self.get_anchor_offsets(size, surf)
            actual_pos = position + position.offset + anchor
            if not self.check_visible(surf, actual_pos):
                continue

            layers.setdefault(renderable.layer, []).append((surf, actual_pos))

        self.display.blit(self.test_fill, (0, 0))

        for layer in sorted(layers):
            for surf, pos in layers[layer]:
                self.display.blit(
                    surf, (int(pos.x/self.scale), int(pos.y/self.scale))
                )

        self.window.blit(pygame.transform.scale(
            self.display, self.size), (0, 0))

        pygame.display.flip()

    def get_text_surf(self, ent: int) -> pygame.Surface:
        chars = list(char_widths.keys())

        for ent in self.text_surfs:
            if not self.world.entity_exists(ent):
                del self.text_surfs[ent]

        text = self.world.component_for_entity(ent, Text)
        if ent not in self.text_surfs or text.dirty:
            string = text.string
            width = max(sum(char_widths.get(c, 3)+1 for c in string), 1)
            height = self.font_image.get_height()
            x, y = 0, 0
            surf = pygame.Surface((width, height)).convert_alpha()
            for char in str(string):
                if char == ' ':
                    x += 3
                    continue
                char_width = char_widths[char]
                surf.blit(
                    self.font_image, (x, y),
                    (sum(char_widths[c]+1 for c in chars[:chars.index(char)]), 0,
                        char_width, height))
                x += char_width + 1
            self.text_surfs[ent] = surf
            text.dirty = False

        self.color_surface(self.text_surfs[ent], *text.color)
        return self.text_surfs[ent]

    def get_anchor_offsets(self, size: object, surface: pygame.Surface) -> Vector2:
        offset = Vector2(0, 0)
        width, height = surface.get_width(), surface.get_height()
        if size.anchor == AlignmentType.top_center:
            offset.x -= width / 2
        elif size.anchor == AlignmentType.top_right:
            offset.x -= width
        elif size.anchor == AlignmentType.center_left:
            offset.y -= height / 2
        elif size.anchor == AlignmentType.center:
            offset.x -= width / 2
            offset.y -= height / 2
        elif size.anchor == AlignmentType.center_right:
            offset.x -= width
            offset.y -= height / 2
        elif size.anchor == AlignmentType.bottom_left:
            offset.y -= height
        elif size.anchor == AlignmentType.bottom_center:
            offset.x -= width / 2
            offset.y -= height
        elif size.anchor == AlignmentType.bottom_right:
            offset.x -= width
            offset.y -= height
        return offset

    def color_surface(self, surface: pygame.Surface, red: int, green: int, blue: int) -> None:
        arr = pygame.surfarray.pixels3d(surface)
        arr[:, :, 0] = red
        arr[:, :, 1] = green
        arr[:, :, 2] = blue

    def check_visible(self, surf: pygame.Surface, pos: Vector2) -> bool:
        surf_rect = surf.get_rect()
        window_rect = self.window.get_rect()
        return (
            pos.x + surf_rect.width >= window_rect.x
            and pos.y + surf_rect.height >= window_rect.y
            and pos.x <= window_rect.x + window_rect.width
            and pos.y <= window_rect.y + window_rect.height
        )


class MovementProcessor(Processor):
    def process(self, dt: float):
        for ent, position in self.world.get_component(Position):
            position.x += position.delta.x
            position.y += position.delta.y

            if self.world.try_component(ent, FollowMouse):
                pos = pygame.mouse.get_pos()
                position.x = pos[0]
                position.y = pos[1]
                continue
            if position.attach:
                attach_position = self.world.try_component(
                    position.attach, Position)
                if attach_position:
                    position.x = attach_position.x
                    position.y = attach_position.y

            position.delta.x = 0
            position.delta.y = 0


class PhysicsProcessor(Processor):
    def __init__(self, friction: float = 0.99):
        super().__init__()
        self.friction = friction

    def process(self, dt: float):
        for ent, (physics, position) in self.world.get_components(Physics, Position):
            physics.velocity *= (1-(self.friction * dt))

            if abs(physics.velocity.x) < 0.001:
                physics.velocity.x = 0
            if abs(physics.velocity.y) < 0.001:
                physics.velocity.y = 0

            position.delta += physics.velocity * dt


class CollisionProcessor(Processor):
    def process(self, dt: float):
        processed = set()
        for ent, (position, size, _) in self.world.get_components(Position, Size, Collider):
            if not position.delta.x or not position.delta.y:
                # if the entity hasnt moved since last frame, ignore it
                continue
            for other_ent, (other_position, other_size, _) in self.world.get_components(Position, Size, Collider):
                key = str(sorted([ent, other_ent]))
                if ent == other_ent or key in processed:
                    continue

                rect = self.get_collider_rect(position, size)
                other_rect = self.get_collider_rect(other_position, other_size)

                # TODO: handle collisions
                # get the direction of each position's movement
                rect.x += position.delta.x
                if rect.colliderect(other_rect):
                    moving_right = position.delta.x > 0
                    moving_left = position.delta.x < 0
                    if moving_right and rect.right > other_rect.left:
                        rect.right = other_rect.left
                    if moving_left and rect.left < other_rect.right:
                        rect.left = other_rect.right

                rect.y += position.delta.y
                if rect.colliderect(other_rect):
                    moving_up = position.delta.y > 0
                    moving_down = position.delta.y < 0
                    if moving_up and rect.top > other_rect.bottom:
                        rect.top = other_rect.bottom
                    if moving_down and rect.bottom < other_rect.top:
                        rect.bottom = other_rect.top
                position.delta.x = rect.x - position.x
                position.delta.y = rect.y - position.y

                processed.add(key)

    def get_collider_rect(self, position: Position, size: Size) -> pygame.Rect:
        return pygame.Rect(position.x, position.y, size.width * size.scale, size.height * size.scale)


class ParticleProcessor(Processor):
    particles = {}

    def process(self, dt: float):
        for ent, (position, emitter) in self.world.get_components(Position, ParticleEmitter):
            emitter.last_spawn += dt
            if emitter.last_spawn >= emitter.rate and (
                not emitter.particle_count
                or len(self.emitters.get(ent, set())) < emitter.particle_count
            ):
                particle_ent = self.spawn_particle(ent, position, emitter)
                emitter.particles.add(particle_ent)
                self.particles[particle_ent] = emitter
                emitter.last_spawn = 0

        for ent, (particle, position, size) in self.world.get_components(Particle, Position, Size):
            particle.age += dt
            if particle.age > particle.lifetime:
                if ent in self.particles:
                    self.particles[ent].particles.remove(ent)
                    del self.particles[ent]
                self.world.delete_entity(ent)
                continue
            size.scale = 1 - (particle.age / particle.lifetime)

    def spawn_particle(self, ent, position, emitter):
        size = random.randint(8, 16)
        return self.world.create_entity(
            Position(position.x-int(size/2), position.y - int(size/2)),
            Size(size, size),
            Collider(),
            Particle(emitter.particle_lifetime,
                     particle_type=emitter.particle_type),
            Renderable((size, size), color=(255, 255, 255)),
            Physics(velocity=(random.randint(-100, 100),
                    random.randint(-100, 100)))
        ) if random.random() < emitter.spawn_chance else None


class EventProcessor(Processor):
    clicked = None

    def process(self, _):
        for event in pygame.event.get():
            if (
                event.type != pygame.QUIT
                and event.type == pygame.KEYDOWN
                and event.key == pygame.K_ESCAPE
                or event.type == pygame.QUIT
            ):
                self.world.game.on_cleanup()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.check_click_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.check_click_up(event.pos)

        pressed = pygame.key.get_pressed()
        for ent, (physics, player_controlled) in self.world.get_components(Physics, PlayerControlled):
            if pressed[pygame.K_w]:
                physics.velocity.y -= player_controlled.speed
            if pressed[pygame.K_s]:
                physics.velocity.y += player_controlled.speed
            if pressed[pygame.K_a]:
                physics.velocity.x -= player_controlled.speed
            if pressed[pygame.K_d]:
                physics.velocity.x += player_controlled.speed

    def check_click_down(self, pos):
        x, y = pos
        self.clicked = None
        for ent, (clickable, position, size) in self.world.get_components(Clickable, Position, Size):
            if x >= position.x and x <= position.x+size.width and y >= position.y and y <= position.y+size.height:
                clickable.pressed = True
                clickable.pressed_start_time = time()
                self.clicked = ent
        if not self.clicked:
            # print('create emmitter', pos)
            self.world.create_entity(
                ParticleEmitter(rate=.01, particle_lifetime=4.0,
                                spawn_chance=random.random()),
                Renderable(color=(255, 255, 255), size=(8, 8)),
                Position(pos),
                Size(),
                PlayerControlled()
            )

    def check_click_up(self, pos):
        x, y = pos
        if not self.clicked:
            return
        # position = self.world.try_component(self.clicked, Position)
        # size = self.world.try_component(self.clicked, Size)
        # if not (position and size):
        #     return
        # if (
        #     x < position.x
        #     or x > position.x + size.width
        #     or y < position.y
        #     or y > position.y + size.height
        # ):
        #     return
        # clickable = self.world.try_component(self.clicked, Clickable)
        # if not clickable:
        #     return
        # clickable.pressed_time = time() - clickable.pressed_start_time
        # clickable.pressed = False
        # print(clickable.pressed_time)
        # clickable.action()
