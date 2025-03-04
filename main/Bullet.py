import pyglet
import pymunk
from Projectile import Projectile
from GLOBAL import BULLET_COLLISION


class Bullet(Projectile):
    def __init__(self, img, space, x, y, angle, speed, batch):
        super().__init__(img, space, x, y, angle, speed, batch)
        self.scale = 0.2  # Уменьшаем размер спрайта
        self.shape.collision_type = BULLET_COLLISION  # Тип коллизии для пули