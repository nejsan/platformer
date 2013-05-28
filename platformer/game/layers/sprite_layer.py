import basic_layer

class SpriteLayer(basic_layer.BasicLayer):
	"""A layer which contains a :class:`pyglet.sprite.Sprite` as its content."""

	def __init__(self, *args, **kwargs):
		super(SpriteLayer, self).__init__(*args, **kwargs)

	def update(self, dt):
		self.graphic.update(dt)