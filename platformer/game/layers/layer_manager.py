from pyglet.graphics import Batch, OrderedGroup

# TODO Layer manager should support hiding layers (no drawing) and deactivating layers (no drawing or updating)
# TODO Layer manager should support being disabled and re-enabled (like when you enter a sublevel and the current layer manager changes to the sub-level's)

# TODO This should probably support the naming of layers so that layers can be added later relative to a pre-existing layer more easily.

# TODO Write tests for this
# TODO When writing tests, test coalescing and freeing of deleted layers, for ALL types of layers
class LayerManager(object):
	"""Manager for updating and drawing layers in a specified order.

	Attributes:
		viewport: The viewport that the layers will be viewed through.
	"""

	def __init__(self, viewport, layers):
		"""Begins managing the given layers.

		Args:
			viwport: The viewport that the layers will be viewed through.
			layers (list of :class:`game.layers.BaseLayer`): The layers to maintain, with the highest index being the top foreground layer and the first index being the bottom background layer.
		"""
		self.viewport = viewport

		self._drawing_queue = []

		self._update_queue = []
		self._viewport_target_layer = None
		self._depth = 0 # Used for setting draw order with OrderedGroups

		# Begin managing the layers
		map(self.manage_layer, layers)


	def update(self, dt):
		"""Updates all managed layers which support updating.

		Args:
			dt (float): The number of seconds since the last update.
		"""
		# TODO Ideally this would always be set regardless of whether the viewport has a target because that eliminates this IF every frame
		if self._viewport_target_layer:
			self._viewport_target_layer.update(dt)

		self.viewport.update(dt)
		map(lambda item: item.update(dt), self._update_queue)


	def draw(self):
		"""Draws all managed layers in the specified order."""
		map(lambda item: item.draw(), self._drawing_queue)


	def manage_layer(self, layer):
		"""Begins managing a layer.

		Args:
			layer (:class:`game.layers.BaseLayer`): The layer to begin managing.
		"""
		layer.viewport = self.viewport

		self._append_to_drawing_queue(layer)
		self._push_layer_event_handlers(layer)

		# Add the layer to the update queue if it supports updating
		if hasattr(layer, 'update'):
			# TODO This viewport target check is awful. Stop checking for a hitbox once physical_object is refactored to retun its x as its hitbox's x
			if hasattr(self.viewport, 'target'):
				if hasattr(layer.graphic, 'hitbox') and layer.graphic.hitbox is self.viewport.target:
					self._viewport_target_layer = layer
					return

			self._update_queue.append(layer)


	def _get_current_graphics_batch(self):
		"""Returns the batch at the top of the drawing queue.

		Returns:
			:class:`pyglet.graphics.Batch`.
		"""
		# Create a new batch if the current drawing item is not a batch
		if not self._drawing_queue or not isinstance(self._drawing_queue[-1], Batch):
			self._drawing_queue.append(Batch())

		return self._drawing_queue[-1]


	def _get_current_graphics_group(self):
		"""Returns the group at the current layer depth.

		Returns:
			:class:`pyglet.graphics.OrderedGroup`.
		"""
		group = OrderedGroup(self._depth)
		self._depth += 1 # Render the next layer at the next depth

		return group


	def _append_to_drawing_queue(self, layer):
		"""Adds a layer to the end of the drawing queue.

		If the layer supports batches, it will be added to a batch
		at the end of the queue. If the layer does not support batches,
		the layer itself will be added to the end of the queue and will
		be expected to draw itself.

		Args:
			layer (:class:`game.layers.BaseLayer`): The layer to append to the drawing queue.
		"""
		# Add the layer to the current batch if it supports batches
		if hasattr(layer, 'batch'):
			layer.batch = self._get_current_graphics_batch()
			layer.group = self._get_current_graphics_group()
		# The layer should draw itself if it doesn't support batches
		else:
			self._drawing_queue.append(layer)

	def _push_layer_event_handlers(self, layer):
		"""Sets event handlers for when a layer dispatches an event.

		Args:
			layer (:class:`game.layers.BaseLayer`): The layer to set event handlers on.
		"""
		layer.set_handler('on_delete', self._on_layer_delete)



	# Event handlers

	def _on_layer_delete(self, layer):
		"""Event handler for when a layer is deleted.

		The layer will cease to be managed, and any resulting adjacent
		batches in the drawing queue will be coalesced if possible.

		Args:
			layer (:class:`game.layers.BaseLayer`): The layer which was deleted.
		"""
		if layer in self._update_queue:
			self._update_queue.remove(layer)

		# TODO What if it was the viewport target?
		# TODO What if there are no more layers? Should the viewport target layer then be set as a dummy lambda?

		# TODO If this was the last thing in its batch/group, delete the group
		if layer in self._drawing_queue:
			self._drawing_queue.remove(layer)

		# TODO Coalesce batches if necessary
		# TODO Whichever batch has less items in it should be merged into the batch with more
