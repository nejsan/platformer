from game.extended_sprite import ExtendedSprite

class Tile(ExtendedSprite):
	"""A tile for use in maps.

	Attributes:
		is_collidable (bool): Whether the tile can be collided with.
		type (str): The type of tile.
	"""

	type = 'basic'

	def __init__(self, *args, **kwargs):
		"""Creates a new tile.

		Kwargs:
			is_collidable (bool): Whether the tile can be collided with.
		"""
		self.is_collidable = kwargs.pop('is_collidable', True)

		super(Tile, self).__init__(*args, **kwargs)

	def resolve_collision_x(self, obj):
		"""Resolves a collision with a physical object on the x-axis.

		Args:
			obj (:class:`game.physical_objects.physical_object.PhysicalObject`): The physical object to resolve a collision with.

		Returns:
			True if a collision occurred, False otherwise.
		"""
		# If the object is moving left
		if obj.moving_to_x < obj.hitbox.x:
			obj.moving_to_x = self.x2
			obj.on_left_collision(self)

			return True
		# If the object is moving right
		else:
			obj.moving_to_x = self.x - obj.hitbox.width
			obj.on_right_collision(self)

			return True

	def resolve_collision_y(self, obj):
		"""Resolves a collision with a physical object on the y-axis.

		Args:
			obj (:class:`game.physical_objects.physical_object.PhysicalObject`): The physical object to resolve a collision with.

		Returns:
			True if a collision occurred, False otherwise.
		"""
		# If the object is moving down through the tile
		if obj.moving_to_y < obj.hitbox.y:
			# Move it on top of the tile
			obj.moving_to_y = self.y2
			obj.on_bottom_collision(self)

			return True
		# If the object is moving up from below the tile
		elif obj.moving_to_y < self.y2:
			# Move it under the tile
			obj.moving_to_y = self.y - obj.hitbox.height
			obj.on_top_collision(self)

			return True

		return False
