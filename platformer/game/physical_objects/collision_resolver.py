# -*- coding: utf-8 -*-

from ..settings import general_settings
from ..util import coordinate_to_tile

def resolve_collisions(obj):
	# Don't resolve horizontal collisions if the object has no horizontal velocity
	if obj.moving_to_x is not obj.hitbox.x:
		# Handle horizontal component first in case of slopes
		_resolve_collision_x(obj, obj.stage)

	_resolve_collision_y(obj, obj.stage)

def _resolve_collision_x(obj, tile_map):
	x_range = _get_axis_range(obj, 'x', obj.moving_to_x)

	tile_found = False
	for y in obj.y_tile_span:
		if tile_found:
			break

		for x in x_range:
			collision_tile = tile_map[y][x]
			if collision_tile and collision_tile.is_collidable:
				# TODO Implement hooks for custom tiles to determine exceptions and say whether tiles should be ignored
				if x != 0:
					left_tile = tile_map[y][x-1]

					"""Ignore adjacent tiles connected to left-facing slopes (allows for ascending connected left-facing slopes)
					 ◢□■
					◢□■■
					"""
					# TODO obj.hitbox.x + obj.hitbox.half_width should be obj.bottom_center or something similar
					# TODO This check used to end with ` and obj.y >= left_tile.y`. I should test if that was really necessary or not.
					if left_tile and left_tile.type is 'slope' and left_tile.faces_left and obj.hitbox.x + obj.hitbox.half_width <= collision_tile.x:
						continue

					if y != 0:
						bottom_left = tile_map[y-1][x-1]

						"""Allow ascending connected left-facing slopes by bypassing protection against entering
						slopes which are above the bottom of the object.
						Assuming an object 2 lines tall, it should not pass through the second figure, but should
						be allowed to continue seamlessly up to the second slope in the first figure.
						1:  ◿■■    2:   ◢
						   ◢■■■
						"""
						if collision_tile.type is 'slope' and bottom_left and bottom_left.type is 'slope' and not collision_tile.is_ceiling and collision_tile.faces_left and bottom_left.faces_left:
							continue

				if x+1 < len(tile_map[0]):
					right_tile = tile_map[y][x+1]

					"""Ignore adjacent tiles connected to right-facing slopes if the object's center is over the slope
					(allows for ascending connected right-facing slopes)
					■□◣
					■■□◣
					"""
					# TODO This check used to end with ` and obj.y >= right_tile.y`. I should test if that was really necessary or not.
					if right_tile and right_tile.type is 'slope' and right_tile.faces_right and obj.hitbox.x + obj.hitbox.half_width >= collision_tile.x2:
						continue

					if y != 0:
						bottom_right = tile_map[y-1][x+1]

						# Allow us to ascend continuous rightward slopes, because you can not enter a slope tile that's above your current y
						# position unless it is facing the same direction as the tile you are currently on
						"""Allow ascending connected right-facing slopes by bypassing protection against entering
						slopes which are above the bottom of the object.
						Assuming an object 2 lines tall, it should not pass through the second figure, but should
						be allowed to continue seamlessly up to the second slope in the first figure.
						1:  ■■◺    2:   ◣
						    ■■■◣
						"""
						if collision_tile.type is 'slope' and bottom_right and bottom_right.type is 'slope' and not collision_tile.is_ceiling and collision_tile.faces_right and bottom_right.faces_right:
							continue

				tile_found = collision_tile.resolve_collision_x(obj)

				if tile_found:
					break

	new_x = int(obj.moving_to_x)

	obj.facing_right = new_x > obj.hitbox.x

	obj.hitbox.set_x(new_x)
	obj.x = obj.hitbox.x - obj.hitbox.rel_x
	obj.tile_x = obj.hitbox.x / general_settings.TILE_SIZE
	obj.sub_tile_x = obj.hitbox.x % general_settings.TILE_SIZE / general_settings.TILE_SIZE_FLOAT
	obj.x_tile_span = obj.get_x_tile_span()

def _resolve_collision_y(obj, tile_map):
	y_range = _get_axis_range(obj, 'y', obj.moving_to_y)

	tile_found = False

	# TODO Make this pre-check more efficient
	for y in y_range:
		# If the object is centered over a slope, always use the slope
		# Tile that the object's center is over
		centered_tile = tile_map[y][coordinate_to_tile(obj.hitbox.x + obj.hitbox.half_width)]
		if centered_tile and centered_tile.is_collidable and centered_tile.type is 'slope':
			tile_found = centered_tile.resolve_collision_y(obj)
			if tile_found: break

	for y in y_range:
		if tile_found:
			break

		for x in obj.x_tile_span:
			collision_tile = tile_map[y][x]

			if collision_tile and collision_tile.is_collidable:
				tile_found = collision_tile.resolve_collision_y(obj)

				if tile_found:
					break

	# If we didn't collide with a tile and we weren't already in the air, we fell
	if not (tile_found or obj.in_air):
		obj.in_air = True

	obj.hitbox.set_y(obj.moving_to_y)
	obj.y = obj.hitbox.y - obj.hitbox.rel_y
	obj.tile_y = obj.hitbox.y / general_settings.TILE_SIZE
	obj.sub_tile_y = obj.hitbox.y % general_settings.TILE_SIZE / general_settings.TILE_SIZE_FLOAT
	obj.y_tile_span = obj.get_y_tile_span()


# Returns the tiles covered by single-dimensional movement on the specified axis
def _get_axis_range(obj, axis, new_position):
	# Initiate our values based on the axis we're checking
	if axis == 'x':
		current_position = obj.hitbox.x
		current_tile = obj.tile_x
		axis_dimension = obj.tile_width
		axis_tile_boundary = obj.max_stage_x - 1
	else: # Y axis
		current_position = obj.hitbox.y
		current_tile = obj.tile_y
		axis_dimension = obj.tile_height
		axis_tile_boundary = obj.max_stage_y - 1

	new_tile = new_position / general_settings.TILE_SIZE

	# Ensure that we include the most tiles possible in the calculated range
	if new_position > current_position:
		new_tile = int(new_tile + axis_dimension) # Value is floored
		current_tile =	int(current_tile + axis_dimension)

		# Only check within the bounds of the stage
		if current_tile < 0:
			current_tile = 0

		if new_tile >= axis_tile_boundary:
			new_tile = axis_tile_boundary

		return xrange(current_tile, new_tile + 1)
	else:
		new_tile = int(new_tile) # Value is floored

		# Only check within the bounds of the stage
		if current_tile >= axis_tile_boundary:
			current_tile = axis_tile_boundary

		if new_tile < 0:
			new_tile = 0

		# Optimize for left-to-right or top-to-bottom checking
		return xrange(current_tile, new_tile - 1, -1)