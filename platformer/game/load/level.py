from pyglet.resource import file as open_resource_file
from game.bounded_box import BoundedBox
from game.graphics import create_graphics_object
from game import viewport
from json import load as json_load
from ..settings.general_settings import TILE_SIZE, RESOURCE_PATH, LEVEL_DIRECTORY, LEVEL_FORMAT, SCRIPT_DIRECTORY, SCRIPT_FORMAT
from game import layers
from imp import load_source, new_module
from sys import modules
from tile_map import load_tile_map
from installed_level_config_translators import install_level_config_translator, translate_data_value
import game.scripts
"""Python 3
import importlib.machinery"""

# TODO Level loader tests
class Level(object):
    # TODO Documentation

    def __init__(self, level_data):
        """Loads a level from disk.

        Args:
            level_data (dict): A dictionary of level parameters.
        """
        # Add support for translating config strings to property values and registering layer graphic dependencies
        install_level_config_translator('property', self._get_property_from_string)
        install_level_config_translator('layer_graphic_property', self._register_layer_graphic_dependency)

        # Dictionary of layers and their layer graphic dependencies
        self._layer_graphic_dependencies = {}

        # TODO Implement ability to specify whether to load a script before the level is loaded or after
        # Scripts must be loaded first because they provide dynamic values which may be used
        self._load_scripts(level_data['scripts'])

        self.title = translate_data_value(level_data['title'])

        camera_target = None

        # Translate all level data values
        # Don't recurse because we'll translate the layer data individually
        level_data = translate_data_value(level_data, recurse=False)

        # Check if the boundaries of the map were specified
        if 'size' in level_data:
            level_data['size'] = translate_data_value(level_data['size'])
            rows = level_data['size']['rows']
            cols = level_data['size']['cols']
        else:
            # TODO If the size isn't specified, an unbounded camera should be used in place of this hotfix
            rows = cols = 1000

        self.layer_dict = {} # TODO Temporary method of accessing layers by title

        # Loop through layers, keeping track of the current layer for registering layer graphic dependencies
        for layer_index, layer_data in enumerate(level_data['layers']):
            self._current_layer = translate_data_value(layer_data['title'])
            level_data['layers'][layer_index] = translate_data_value(layer_data)

        # Resolve layer graphic dependencies during post-processing
        install_level_config_translator('resolve_layer_graphic_dependency', self._get_layer_graphic_property)

        # Post-process the level config and create the layers
        level_layers = []
        initialized_layer_graphics = []
        for layer_index, layer_data in enumerate(level_data['layers']):
            self._current_layer = translate_data_value(layer_data['title'])

            # Skip layers that still have unmet dependencies
            if self._current_layer in self._layer_graphic_dependencies:
                for required_layer in self._layer_graphic_dependencies[self._current_layer]:
                    if required_layer not in initialized_layer_graphics:
                        continue

            # Translate all layer data values
            layer_data = translate_data_value(layer_data)
            level_data['layers'][layer_index] = layer_data

            layer_graphic = create_graphics_object(layer_data['graphic_type'], **layer_data['graphic_data'])

            # TODO Remove the need for this hotfix
            if self._current_layer == 'player':
                layer_graphic = layer_graphic.character

            if level_data['camera_target'] == self._current_layer:
                camera_target = layer_graphic

            if 'layer_data' in layer_data:
                layer = layers.create_from(layer_graphic, **layer_data['layer_data'])
            else:
                layer = layers.create_from(layer_graphic)

            level_layers.append(layer)
            self.layer_dict[self._current_layer] = layer
            initialized_layer_graphics.append(self._current_layer)

        stage_boundary = BoundedBox(0, 0, cols*TILE_SIZE, rows*TILE_SIZE)
        # TODO Don't hardcode window size, make it a global setting
        self.camera = viewport.Camera(0, 0, 800, 600, bounds=stage_boundary, target=camera_target)
        self.camera.focus() # TODO Should this be called on init?

        self.layer_manager = layers.LayerManager(self.camera, level_layers)

    def _get_property_from_string(self, property_value):
        split = property_value.rfind('.')
        module_name = property_value[ : split]
        property_name = property_value[split + 1 : ]
        return getattr(modules[module_name], property_name)

    def _register_layer_graphic_dependency(self, property_name):
        split = property_name.find('.')
        dependecy_layer_name = property_name[ : split]
        if not self._current_layer in self._layer_graphic_dependencies:
            self._layer_graphic_dependencies[self._current_layer] = [dependecy_layer_name]
        else:
            self._layer_graphic_dependencies[self._current_layer].append(dependecy_layer_name)

        # TODO There should be a way for this method to tell the translator to stop translating tags for this property after this one
        return '::resolve_layer_graphic_dependency::' + property_name

    def _get_layer_graphic_property(self, property_name):
        split = property_name.find('.')
        layer_name = property_name[ : split]
        return getattr(self.layer_dict[layer_name].graphic, property_name[split + 1 : ])

    def _load_scripts(self, scripts):
        """Dynamically loads the given scripts. The scripts are loaded from the scripts directory.

        Args:
            scripts (list): A list of the filenames of the scripts to load.
        """
        for script in scripts:
            load_source('game.scripts.custom.'+script, RESOURCE_PATH+SCRIPT_DIRECTORY+'/'+script+'.'+SCRIPT_FORMAT)
            """Python 3
            loader = importlib.machinery.SourceFileLoader('games.scripts.custom.'+script, RESOURCE_PATH+SCRIPT_DIRECTORY+'/'+script+'.'+SCRIPT_FORMAT)
            loader.load_module('game.scripts.custom.'+script)"""

    @classmethod
    def load(cls, level_title):
        # TODO The game.level.Level class in the doc should be updated once this class is finalized
        """Loads a level from a given level title.

        Args:
            level_title (str): The title of the level to load.

        Returns:
            A :class:`game.level.Level` object.
        """
        level_file = open_resource_file(LEVEL_DIRECTORY+'/'+level_title+'.'+LEVEL_FORMAT)
        level_data = json_load(level_file)
        level_file.close()

        return cls(level_data)
