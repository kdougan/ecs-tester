import sys

import pygame

from .entities import create_button
from .entities import create_mouse_entity
from .entities import create_square
from .modules.esper import World
from .processors import CollisionProcessor
from .processors import EventProcessor
from .processors import MovementProcessor
from .processors import ParticleProcessor
from .processors import PhysicsProcessor
from .processors import RenderProcessor


class App:
    def __init__(self):
        self._running = True
        self.clock = pygame.time.Clock()
        self.world = None

    def on_init(self):
        pygame.init()
        self.world = World()
        self.world.game = self

        self.create_processors()

        # self.mouse_entity = create_mouse_entity(self.world)

        self._running = True

    def create_processors(self):
        self.world.add_processor(EventProcessor(), 5)
        self.world.add_processor(ParticleProcessor(), 4)
        self.world.add_processor(PhysicsProcessor(), 3)
        self.world.add_processor(MovementProcessor(), 2)
        self.world.add_processor(CollisionProcessor(), 1)
        self.world.add_processor(RenderProcessor(), 0)

    def on_cleanup(self):
        pygame.quit()
        sys.exit()

    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        while(self._running):
            dt = self.clock.tick(60)/1000

            self.world.process(dt)

        self.on_cleanup()
