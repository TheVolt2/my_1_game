import pyglet.window.key as key

KEY_HANDLER = key.KeyStateHandler()
CAMERA_OFFSET = [0, 0]
PLAYER_COLLISION = 1  # Любые числа
SHURIKEN_COLLISION = 3
ENEMY_COLLISION = 4
BULLET_COLLISION = 2
AMMO_COLLISION = 5
HEALTH_COLLISION = 6  # Тип коллизии для баночек со здоровьем