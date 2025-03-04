import pyglet


window = pyglet.window.Window(1280, 600)

max_hp = 200
current_hp = 180
hp_bar_scale = 5

@window.event
def on_draw():
    window.clear()
    pyglet.shapes.Rectangle(640 - max_hp * hp_bar_scale / 2, 300, (max_hp * hp_bar_scale), 20, (255, 0, 0)).draw()
    x = 640 - max_hp * hp_bar_scale / 2
    width = current_hp * hp_bar_scale
    pyglet.shapes.Rectangle(x + (max_hp - current_hp) * hp_bar_scale, 300, width, 20, (0, 255, 0)).draw()


pyglet.app.run()