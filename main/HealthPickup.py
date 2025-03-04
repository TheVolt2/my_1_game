import pyglet
import pymunk


class HealthPickup(pyglet.sprite.Sprite):
    def __init__(self, img, space, x, y, batch):
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super().__init__(img, x, y, batch=batch)
        self.body = pymunk.Body(1, float("inf"), pymunk.Body.KINEMATIC)
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, 10)  # Размер объекта
        self.shape.collision_type = 6  # Тип коллизии для баночки со здоровьем
        space.add(self.body, self.shape)

    def collect(self, player):
        player.health = min(player.health + 20, 100)  # Пополняем здоровье
        self.delete()  # Удаляем объект после сбора