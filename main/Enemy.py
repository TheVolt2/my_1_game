import math
import pyglet
import pymunk
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.graphics import Batch, Group
from pyglet.image import AbstractImage, Animation
from Bullet import Bullet

BULLET_IMAGE = pyglet.image.load('ASSETS/IMAGES/bullet.png')


class Enemy(pyglet.sprite.Sprite):
    def __init__(self,
                 img: AbstractImage | Animation, space: pymunk.Space,
                 x: float = 0, y: float = 0, z: float = 0,
                 blend_src: int = GL_SRC_ALPHA,
                 blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
                 batch: Batch | None = None,
                 group: Group | None = None,
                 subpixel: bool = False,
                 window: pyglet.window.Window = None) -> None:
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super().__init__(img, x, y, z, blend_src, blend_dest, batch, group, subpixel)

        self.scale_x = 22 / self.image.width
        self.scale_y = 33 / self.image.width
        self.speed = 60
        self.detection_radius = 200  # Радиус обнаружения игрока
        self.shoot_cooldown = 1.0  # Время между выстрелами
        self.shoot_timer = 0.0
        self.health = 50  # Здоровье врага
        self.shooting = False  # Флаг, указывающий, что враг стреляет
        self.shoot_distance = 200  # Дистанция, на которой враг начинает стрелять
        self.chase_distance = 200  # Дистанция, на которой враг начинает преследовать игрока

        self.body = pymunk.Body(1000, float("inf"))
        self.body.position = x, y
        self.shape = pymunk.Poly.create_box(self.body, (220 * self.scale_x, 330 * self.scale_y))
        self.shape.collision_type = 4  # Тип коллизии для врага
        space.add(self.body, self.shape)
        self.space = space
        self.batch = batch
        self.window = window
        self.bullets = []  # Список пуль врага
        self.sprites = dict()
        self.current_state = "IDLE"

    def update(self, dt, player):
        self.position = self.body.position.x, self.body.position.y, self.position[2]
        self.move(dt, player)
        self.update_animation(dt)

        # Обновляем пули
        for bullet in self.bullets:
            bullet.update(dt)

    def move(self, dt, player):
        distance_to_player = math.sqrt((player.body.position.x - self.body.position.x) ** 2 +
                                       (player.body.position.y - self.body.position.y) ** 2)

        if distance_to_player < self.shoot_distance:
            if self.shoot_timer >= self.shoot_cooldown:
                self.shoot(player)
                self.shooting = True
                self.shoot_timer = 0.0
            self.body.velocity = pymunk.Vec2d(0, 0)  # Останавливаем врага, если он стреляет
        elif distance_to_player > self.chase_distance:
            self.shooting = False
            direction = pymunk.Vec2d(player.body.position.x - self.body.position.x,
                                     player.body.position.y - self.body.position.y).normalized()
            self.body.velocity = direction * self.speed
        #else:
        #    self.body.velocity = pymunk.Vec2d(0, 0)  # Останавливаем врага, если игрок в зоне стрельбы

        self.shoot_timer += dt

    def shoot(self, player):
        dx = player.body.position.x - self.body.position.x
        dy = player.body.position.y - self.body.position.y
        angle = math.atan2(dy, dx)

        bullet = Bullet(
            BULLET_IMAGE, self.space, self.body.position.x, self.body.position.y, angle, 200, self.batch
        )
        self.bullets.append(bullet)

    def update_animation(self, dt):
        if not hasattr(self, 'sprites') or self.current_state not in self.sprites:
            return

        prev_index = int(self.animation_index)
        self.animation_index += dt * self.animation_speed
        if self.animation_index >= len(self.sprites[self.current_state]["sprites"]):
            self.animation_index = 0
        if int(self.animation_index) != prev_index:
            new_sprite = self.sprites[self.current_state]["sprites"][int(self.animation_index)]
            new_sprite.anchor_x = new_sprite.width // 2
            new_sprite.anchor_y = new_sprite.height // 2
            self.image = new_sprite

    def change_state(self, state: str) -> None:
        if self.current_state != state and state in self.sprites:
            self.current_state = state
            self.animation_index = 0
            self.animation_speed = self.sprites[self.current_state]["animation_speed"]

    def remove_bullet(self, bullet):
        try:
            self.bullets.remove(bullet)
            self.space.remove(bullet.body, bullet.shape)
        except ValueError:
            pass

    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            print("Enemy defeated!")
            self.delete()  # Удаляем спрайт при смерти
