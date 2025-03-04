import math
import pyglet
import pymunk
from Projectile import Projectile
from GLOBAL import SHURIKEN_COLLISION

class Shuriken(Projectile):
    def __init__(self, img, space, x, y, angle, speed, batch):
        super().__init__(img, space, x, y, angle, speed, batch)
        self.rotation_speed = 360  # Скорость вращения в градусах в секунду
        self.shape.collision_type = SHURIKEN_COLLISION  # Тип коллизии для сюрикена

    def update(self, dt):
        super().update(dt)
        self.rotation += self.rotation_speed * dt  # Вращение спрайта