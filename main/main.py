import pyglet
from pyglet.gl import *
import pymunk
import pymunk.pyglet_util
from pyglet.window import FPSDisplay

from GLOBAL import KEY_HANDLER, CAMERA_OFFSET, PLAYER_COLLISION, SHURIKEN_COLLISION, ENEMY_COLLISION, BULLET_COLLISION, AMMO_COLLISION, HEALTH_COLLISION
from Player import Player
from Enemy import Enemy
from KARTA_ZAGRUZKA import KARTA_ZAGRUZOCHNIK
from Bullet import Bullet
from Shuriken import Shuriken
from AmmoPickup import AmmoPickup
from HealthPickup import HealthPickup

DRAW_OPTIONS = pymunk.pyglet_util.DrawOptions()
window = pyglet.window.Window(width=800, height=600)
fps = FPSDisplay(window)
window.push_handlers(KEY_HANDLER)
main_batch = pyglet.graphics.Batch()
space = pymunk.Space()
space.gravity = 0, -1750

# Обработчик коллизий игрока и сюрикенов
colision_handler = space.add_collision_handler(PLAYER_COLLISION, SHURIKEN_COLLISION)
def collision_handler_func(arbiter, space, data):
    return False
colision_handler.pre_solve = collision_handler_func

# Загрузка спрайтов
wall_sprite = pyglet.image.load('ASSETS/IMAGES/wall.png')
wall_sprite.anchor_x, wall_sprite.anchor_y = wall_sprite.width // 2, wall_sprite.height // 2
enemy_static_image = pyglet.image.load('ASSETS/IMAGES/Enemy.jpeg')
ammo_pickup_image = pyglet.image.load('ASSETS/IMAGES/shuriken.png')
health_pickup_image = pyglet.image.load('ASSETS/IMAGES/Enemy.jpeg')  # Загрузите изображение для баночек со здоровьем

# Загрузчик карты
map_loader = KARTA_ZAGRUZOCHNIK(window, main_batch, space)
map_data = map_loader.load("ASSETS/MAPS/MAP_1_UHAUHAUHAUAHUAHUHA", wall_sprite, enemy_static_image, ammo_pickup_image, health_pickup_image)

# Загрузка анимаций для игрока
player_idle_images = pyglet.image.ImageGrid(pyglet.image.load('ASSETS/IMAGES/IDLE.png'), 1, 10, item_height=65)
player_run_images = pyglet.image.ImageGrid(pyglet.image.load('ASSETS/IMAGES/RUN.png'), 1, 16, item_height=65)
player_start_image = player_idle_images[0]

# Создание игрока
player = Player(player_start_image, space, map_data["player_position"][0], map_data["player_position"][1], batch=main_batch)
player.scale = 3
player.add_sprites("IDLE", player_idle_images, 10)
player.add_sprites("RUN", player_run_images, 20)
window.push_handlers(player)

# Полоска здоровья
foreground_group = pyglet.graphics.Group(order=1)  # Группа для переднего плана
health_bar_bg = pyglet.shapes.Rectangle(10, window.height - 30, 200, 20, color=(255, 0, 0), batch=main_batch, group=foreground_group)
health_bar_fg = pyglet.shapes.Rectangle(10, window.height - 30, 200, 20, color=(0, 255, 0), batch=main_batch, group=foreground_group)

# Счётчик патронов
ammo_label = pyglet.text.Label(
    text=f"Shurikens: {player.shurikens}",
    font_name="Calibri",
    font_size=16,
    x=10,
    y=window.height - 60,
    color=(255, 255, 255, 255),
    batch=main_batch,
    group=foreground_group
)

game_over_label = pyglet.text.Label('GAME OVER', font_name="Calibri", font_size=36, color=(255, 255, 255))

# Установка статического изображения для каждого врага
for enemy in map_data.get("enemies"):
    enemy.image = enemy_static_image
    enemy.window = window

# Обработчик коллизий пуль и игрока
def bullet_player_collision(arbiter, space, _):
    bullet_shape = arbiter.shapes[0]
    player_shape = arbiter.shapes[1]

    # Удаляем пулю из пространства
    for enemy in map_data["enemies"]:
        for bullet in enemy.bullets:
            if bullet.shape == bullet_shape:
                space.remove(bullet.body, bullet.shape)
                enemy.bullets.remove(bullet)
                break

    # Наносим урон игроку
    player.take_damage(10)  # Урон от пули
    print(f"Player hit by bullet! Health: {player.health}")
    return True

# Обработчик коллизий сюрикена и врага
def shuriken_enemy_collision(arbiter, space, _):
    projectile_shape = arbiter.shapes[0]
    enemy_shape = arbiter.shapes[1]

    # Находим врага по его shape
    for enemy in map_data["enemies"]:
        if enemy.shape == enemy_shape:
            # Удаляем сюрикен из пространства
            for projectile in player.projectiles:
                if projectile.shape == projectile_shape:
                    space.remove(projectile.body, projectile.shape)
                    player.projectiles.remove(projectile)
                    break

            # Наносим урон врагу
            enemy.take_damage(10)  # Урон от сюрикена
            print(f"Enemy hit by shuriken! Health: {enemy.health}")
            if enemy.health <= 0:
                print("Enemy defeated!")
                space.remove(enemy.shape, enemy.body)
                map_data["enemies"].remove(enemy)
            return True

    return False

# Обработчик коллизий для сбора патронов
def ammo_player_collision(arbiter, space, _):
    ammo_shape = arbiter.shapes[0]
    player_shape = arbiter.shapes[1]

    for ammo in map_data.get("ammo_pickups", []):
        if ammo.shape == ammo_shape:
            ammo.collect(player)
            space.remove(ammo.body, ammo.shape)
            map_data["ammo_pickups"].remove(ammo)
            break
    return True

# Обработчик коллизий для сбора баночек со здоровьем
def health_player_collision(arbiter, space, _):
    health_shape = arbiter.shapes[0]
    player_shape = arbiter.shapes[1]

    for health_pickup in map_data.get("health_pickups", []):
        if health_pickup.shape == health_shape:
            health_pickup.collect(player)
            space.remove(health_pickup.body, health_pickup.shape)
            map_data["health_pickups"].remove(health_pickup)
            break
    return True

# Добавляем обработчики коллизий
handler_bullet_player = space.add_collision_handler(BULLET_COLLISION, PLAYER_COLLISION)
handler_bullet_player.begin = bullet_player_collision

handler_shuriken_enemy = space.add_collision_handler(SHURIKEN_COLLISION, ENEMY_COLLISION)
handler_shuriken_enemy.begin = shuriken_enemy_collision

handler_ammo_player = space.add_collision_handler(AMMO_COLLISION, PLAYER_COLLISION)
handler_ammo_player.begin = ammo_player_collision

handler_health_player = space.add_collision_handler(HEALTH_COLLISION, PLAYER_COLLISION)
handler_health_player.begin = health_player_collision

@window.event
def on_draw():
    window.clear()
    space.debug_draw(DRAW_OPTIONS)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    main_batch.draw()
    if player.health <= 0:
        game_over_label.position = (238 - CAMERA_OFFSET[0], 300 - CAMERA_OFFSET[1], 0)
        game_over_label.draw()

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        player.jump()

def update(dt):
    if player.health > 0:
        player.update(dt=dt)
        window.view = pyglet.math.Mat4()

        CAMERA_OFFSET[0] = -player.position[0] + 300
        CAMERA_OFFSET[1] = -player.position[1] + 250

        window.view = window.view.translate(
            pyglet.math.Vec3(CAMERA_OFFSET[0], CAMERA_OFFSET[1], 0)
        )

        # Обновляем врагов и передаем игрока
        for enemy in map_data["enemies"]:
            enemy.update(dt, player)

        # Обновляем полоску здоровья
        health_bar_fg.width = (player.health / 100) * 200


        health_bar_fg.position = player.position[0] + 250, player.position[1] + 300
        health_bar_bg.position = player.position[0] + 250, player.position[1] + 300

        # Обновляем счётчик патронов
        ammo_label.text = f"Shurikens: {player.shurikens}"
        ammo_label.position = player.position[0] + 250, player.position[1] + 280, 0

def fixed_update(dt):
    space.step(dt)

pyglet.clock.schedule(update)
pyglet.clock.schedule_interval(fixed_update, 1 / 120)
pyglet.app.run()