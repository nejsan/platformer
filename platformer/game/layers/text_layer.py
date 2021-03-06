from graphics_layer import StaticGraphicsLayer
from fixed_layer import FixedLayer
from ..text import Text

class StaticTextLayer(StaticGraphicsLayer):
	"""A layer of static text content.

	The contents of this layer are never updated.
	"""

	def __init__(self, *args, **kwargs):
		super(StaticTextLayer, self).__init__(*args, **kwargs)

	def _set_batch(self, batch):
		self.graphic.begin_update()
		self.graphic.batch = batch
		self.graphic.end_update()

	batch = property(lambda self: self.graphic.batch, _set_batch)

	def _set_group(self, group):
		self.graphic.begin_update()
		self.graphic.group = group
		self.graphic.end_update()

	group = property(lambda self: self.graphic.group, _set_group)



class TextLayer(StaticTextLayer):
	"""A layer of text content which updates each frame."""

	def __init__(self, *args, **kwargs):
		super(TextLayer, self).__init__(*args, **kwargs)

	def update(self, dt):
		"""Updates the layer's text contents.

		This is performed by calling ``self.graphic.update(dt)``.

		Args:
			dt (float): The number of seconds that elapsed between the last update.
		"""
		self.graphic.update(dt)



class FixedStaticTextLayer(FixedLayer, StaticTextLayer):
	"""A layer of static text fixed relative to the viewport."""

	def __init__(self, *args, **kwargs):
		super(FixedStaticTextLayer, self).__init__(*args, **kwargs)

		# If a viewport was given, fix the graphic to it
		if self.viewport:
			self.update(0)

	def update(self, dt):
		self.fix_graphic()



class FixedTextLayer(FixedStaticTextLayer):
	"""A layer of text fixed relative to the viewport."""

	def __init__(self, *args, **kwargs):
		super(FixedTextLayer, self).__init__(*args, **kwargs)

		# If a viewport was given, fix the graphic to it
		if self.viewport:
			self.update(0)

	def update(self, dt):
		super(FixedTextLayer, self).update(dt)
		self.graphic.update(dt)


def recognizer(graphic):
	"""Recognizes whether this layer type supports the graphics object."""
	return isinstance(graphic, Text)

def factory(static=False, fixed=False):
	"""Returns the proper class for the given layer properties."""
	if fixed and static:
		return FixedStaticTextLayer

	if fixed:
		return FixedTextLayer

	if static:
		return StaticTextLayer

	return TextLayer
