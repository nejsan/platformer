import pyglet
from pyglet.window import key
from game import load, camera, stageevents, reloader, transition
from game.layers import layer_manager, fixed_layer, fixed_animation_layer, fixed_text_layer
from game.settings import general_settings
from game.resources import transition_sprite

# Graphical output window
game_window = pyglet.window.Window(800, 600, caption='Platformer Demo')
#game_window.set_icon(pyglet.resource.image('icon.png')) @TODO Load an icon

# Handler for all keyboard events
key_handler = key.KeyStateHandler()

# TODO The stage to load shouldn't be passed like this, there should be some sort of saved data handler that passes this
# TODO Stage data should be loaded by the stage loader
level_data = load.LevelData('demo') # TODO Could this be a Level class which contains Stage and LevelEvents objects?

stage = load.Stage(level_data)

#characters = load.Characters(stage_data.get_character_data(), stage.get_tiles())

# TODO Should probably just pass the reference to the stage here
player = load.Player(level_data.get_player_data(), stage.get_tiles(), key_handler)
game_window.push_handlers(player.character.key_handler)

cam = camera.Camera(player.character, game_window, stage.get_tiles())
cam.focus() # TODO Should this be called on init?

# TODO This should be handled dynamically by the level loader. I'm creating these manually until I implement that ability
background = fixed_layer.FixedLayer(pyglet.sprite.Sprite(img=pyglet.resource.image(level_data.get_background_image_file())), cam)
# TODO Remove this?
#title_overlay = overlay.Overlay(level_data.get_level_title(), cam)
transition_layer = fixed_animation_layer.FixedAnimationLayer(transition.TiledAnimation(transition_sprite.sprite, cam.width, cam.height, delay=0.5, duration=1.25, ease_power=1.75), cam)
title_layer = fixed_text_layer.FixedTextLayer(transition.Heading(level_data.get_level_title(), duration=2.25), cam, offset_x=cam.half_width, offset_y=cam.half_height)
# TODO FPS display layer
#title_layer = fixed_layer.FixedLayer(pyglet.text.Label(level_data.get_level_title(), font_name='Helvetica Neue', font_size=18, anchor_x='center', anchor_y='center'), cam)
layering = layer_manager.LayerManager([background], [transition_layer, title_layer])

# TODO This should be a LevelEvents object inside a Level class
stage_events = stageevents.StageEvents(player.character, cam, level_data.get_stage_events())

module_reloader = reloader.Reloader(stage, player, game_window, cam, background, stage_events, key_handler)

@game_window.event
def on_draw():
	# TODO It's possible that this could be removed if it's a significant performance bottleneck
	game_window.clear()

	layering.draw_background()
	stage.draw()
	#characters.draw()
	player.draw()
	layering.draw_foreground()

def update(dt):
	player.update(dt)

	stage_events.update()

	cam.update(dt)
	layering.update(dt)

	module_reloader.update()

	# @TODO characters.update() method
	"""for character in characters.get_characters():
		character.update(dt)"""

if __name__ == '__main__':
	pyglet.clock.schedule_interval(update, general_settings.FRAME_LENGTH)

	pyglet.app.run()
