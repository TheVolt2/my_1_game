import math
import pyglet
import pymunk


class Projectile(pyglet.sprite.Sprite):
    def __init__(self, img, space, x, y, angle, speed, batch):
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super().__init__(img, x, y, batch=batch)

        self.angle = angle
        self.dx = speed * math.cos(angle)
        self.dy = speed * math.sin(angle)
        self.speed = speed

        self.body = pymunk.Body(1, float("inf"), pymunk.Body.KINEMATIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, 10)  # Размер снаряда
        space.add(self.body, self.shape)

    def update(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.body.position = self.x, self.y