import pyglet
import pymunk
from Enemy import Enemy
from AmmoPickup import AmmoPickup


class KARTA_ZAGRUZOCHNIK:
    def __init__(self, window, batch, space):
        self.window = window
        self.batch = batch
        self.space = space
        self.sprites_crutch = []

    def load(self, file_path, wall_sprite: pyglet.image.AbstractImage, enemy_sprite: pyglet.image.AbstractImage = None, ammo_pickup_image: pyglet.image.AbstractImage = None):
        cell_size = 64  # Размер стен по умолчанию
        map_file = open(file_path, 'r', encoding='utf-8')
        line = map_file.readline()

        while "KARTA" not in line:
            if "RAZMER_STEN" in line:
                cell_size = int(line.split(":")[1])
            line = map_file.readline()

        map_data = {"enemies": [], "ammo_pickups": []}
        map_file.readline()

        x = 0
        y = self.window.height
        for line in map_file.readlines():
            for symbol in line:
                if symbol == '#':
                    body = pymunk.Body(1000, float("inf"), pymunk.Body.KINEMATIC)
                    body.position = (x, y)
                    shape = pymunk.Poly.create_box(body, (cell_size, cell_size))
                    sprite = pyglet.sprite.Sprite(wall_sprite, x, y, batch=self.batch)
                    sprite.scale_x = cell_size / wall_sprite.width
                    sprite.scale_y = cell_size / wall_sprite.height
                    self.space.add(body, shape)
                    self.sprites_crutch.append(sprite)

                elif symbol == 'E' and enemy_sprite is not None:
                    enemy = Enemy(enemy_sprite, self.space, x, y, batch=self.batch, window=self.window)
                    self.sprites_crutch.append(enemy)
                    map_data["enemies"].append(enemy)

                elif symbol == "P":
                    map_data["player_position"] = (x, y)

                elif symbol == "A" and ammo_pickup_image is not None:  # Объект для пополнения патронов
                    ammo_pickup = AmmoPickup(ammo_pickup_image, self.space, x, y, self.batch)
                    self.sprites_crutch.append(ammo_pickup)
                    map_data["ammo_pickups"].append(ammo_pickup)

                x += cell_size

            x = 0
            y -= cell_size

        return map_data