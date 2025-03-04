import math
import pyglet
import pymunk
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.graphics import Batch, Group
from pyglet.image import AbstractImage, Animation
from Shuriken import Shuriken

from GLOBAL import KEY_HANDLER, CAMERA_OFFSET


def get_axis(negative, positive):
    return int(positive) - int(negative)


class Player(pyglet.sprite.Sprite, pyglet.window.EventDispatcher):
    def __init__(self,
                 img: AbstractImage | Animation, space: pymunk.Space,
                 x: float = 0, y: float = 0, z: float = 0,
                 blend_src: int = GL_SRC_ALPHA,
                 blend_dest: int = GL_ONE_MINUS_SRC_ALPHA,
                 batch: Batch | None = None,
                 group: Group | None = None,
                 subpixel: bool = False,
                 program=None) -> None:
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super().__init__(img, x, y, z, blend_src, blend_dest, batch, group, subpixel, program)

        self.scale = 3
        self.speed = 120
        self.health = 100  # Здоровье игрока
        self.jump_speed = 700  # Скорость прыжка
        self.on_ground = False  # Флаг, указывающий, что игрок на земле
        self.max_shurikens = 10  # Максимальное количество сюрикенов
        self.shurikens = self.max_shurikens  # Текущее количество сюрикенов
        self.shoot_cooldown = 0.5  # Время между выстрелами
        self.shoot_timer = 0.0  # Таймер для отслеживания времени между выстрелами

        self.body = pymunk.Body(1000, float("inf"))
        self.body.position = x, y
        self.shape = pymunk.Poly.create_box(self.body, (22 * self.scale, 33 * self.scale))
        self.shape.collision_type = 1  # Тип коллизии игрока
        space.add(self.body, self.shape)

        self.sprites = dict()
        self.current_state = "IDLE"
        self.animation_index = 0
        self.animation_speed = 10

        self.projectiles = []

        self.shuriken_sprite = pyglet.image.load("ASSETS/IMAGES/shuriken.png")

    def update(self, dt=None):
        self.position = self.body.position.x, self.body.position.y, self.position[2]
        self.move(dt)
        self.update_animation(dt)
        for projectile in self.projectiles:
            projectile.update(dt)

        # Проверка, что игрок на земле
        self.on_ground = self.body.velocity.y == 0

        # Обновляем таймер стрельбы
        self.shoot_timer += dt

    def move(self, dt):
        velocity_x = get_axis(KEY_HANDLER[pyglet.window.key.A], KEY_HANDLER[pyglet.window.key.D]) * self.speed
        self.body.velocity = pymunk.Vec2d(velocity_x, self.body.velocity.y)

        if velocity_x != 0:
            if velocity_x < 0:
                self.scale_x = -1
            elif velocity_x > 0:
                self.scale_x = 1
            self.change_state("RUN")
        else:
            self.change_state("IDLE")

    def jump(self):
        if self.on_ground:
            self.body.velocity = pymunk.Vec2d(self.body.velocity.x, self.jump_speed)
            self.on_ground = False

    def update_animation(self, dt):
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
        if self.current_state != state:
            self.current_state = state
            self.animation_index = 0
            self.animation_speed = self.sprites[self.current_state]["animation_speed"]

    def add_sprites(self, state_key: str, images: pyglet.image.ImageGrid, animation_speed: int = 5):
        self.sprites[state_key] = {
            "sprites": images,
            "animation_speed": animation_speed
        }

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == pyglet.window.mouse.LEFT and self.shurikens > 0 and self.shoot_timer >= self.shoot_cooldown:
            world_x, world_y = (-CAMERA_OFFSET[0] + x), (-CAMERA_OFFSET[1] + y)

            dx = world_x - self.body.position.x
            dy = world_y - self.body.position.y

            direction = pyglet.math.Vec2(dx, dy)
            direction.normalize()
            angle = math.atan2(dy, dx)

            projectile = Shuriken(
                self.shuriken_sprite, self.body.space, self.body.position.x,
                self.body.position.y, angle, 200, self.batch
            )
            projectile.scale = 0.15
            self.projectiles.append(projectile)
            self.shurikens -= 1
            self.shoot_timer = 0.0
            print(f"Осталось сюрикенов: {self.shurikens}")  # Вывод в консоль

    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            print("Player defeated!")
            # self.delete()