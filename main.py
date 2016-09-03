""" Layering Demo

This should demonstrate the various layers involved in the Turn Based Strategy game I'm working on.
"""

from __future__ import division, print_function, unicode_literals

import pyglet
from pyglet.graphics.vertexattribute import GLubyte

import cocos
from cocos.actions import *
from cocos import tiles, rect

class ScrollableLayerManager(cocos.layer.scrolling.ScrollingManager, pyglet.event.EventDispatcher):
    """This Manager holds multiple scrollable layers.
    """
    is_event_handler = True
    def __init__(self, screen_width, screen_height):
        self.viewport = rect.Rect(0,0,screen_width, screen_height)
        super(ScrollableLayerManager, self).__init__(self.viewport)

        # Selector Layer
        self.selector_layer = SelectorLayer()
        self.add(self.selector_layer, 6, 'selector')

        # Overlay Layer
        self.overlay_layer = OverlayLayer()
        self.add(self.overlay_layer, 5, 'overlay')

        # Shading Layer
        self.shading_layer = ShadingLayer()
        self.add(self.shading_layer, 4, 'shading')

        # Unit Layer
        self.unit_layer = UnitLayer()
        self.add(self.unit_layer, 3, 'units')

        # Obstacle Layer
        self.obstacle_layer = ObstacleLayer()
        self.add(self.obstacle_layer, 2, 'obstacles')

        # Terrain Layer
        self.terrain_layer = TerrainLayer(screen_width, screen_height)
        self.add(self.terrain_layer, 1, 'terrain')

        # Track the camera's position
        self.camera_x = 0
        self.camera_y = 0

        # Track the camera's direction
        self.camera_direction_x = 0
        self.camera_direction_y = 0

        # Focus the camera.
        self.camera_x = self.terrain_layer.layer_width / 2
        self.camera_y = self.terrain_layer.layer_height / 2
        self.set_focus(self.camera_x, self.camera_y)

        # Schedule a function that is called every frame. Pass this object as an argument.
        self.schedule(self.update, self)

    def update(dt, *item_args):
        this = item_args[1]
        # Move the camera in the x direction.
        if (this.camera_direction_x < 0):
            this.camera_x -= 10
        if (this.camera_direction_x > 0):
            this.camera_x += 10

        # Move the camera in the y direction.
        if (this.camera_direction_y < 0):
            this.camera_y -= 10
        if (this.camera_direction_y > 0):
            this.camera_y += 10

        # Bind the camera within the edges of the screen.
        if this.camera_x < this.viewport.width / 2:
            this.camera_x = this.viewport.width / 2

        if this.camera_x > this.terrain_layer.layer_width - this.viewport.width / 2:
            this.camera_x = this.terrain_layer.layer_width - this.viewport.width / 2

        if this.camera_y < this.viewport.height / 2:
            this.camera_y = this.viewport.height / 2

        if this.camera_y > this.terrain_layer.layer_height - this.viewport.height / 2:
            this.camera_y = this.terrain_layer.layer_height - this.viewport.height / 2

        # Update the focus point of the camera.
        this.set_focus(this.camera_x, this.camera_y)

    def on_mouse_motion(self, x,y,dx,dy):
        # Scroll the window over if it's at the edge.
        scroll_sensitivity = 30

        # If the camera is at the left side, move the camera left
        if x < self.viewport.left + scroll_sensitivity:
            self.camera_direction_x = -1
        # If the camera is at the right side, move the camera left
        elif x > self.viewport.right - scroll_sensitivity:
            self.camera_direction_x = 1
        else:
            self.camera_direction_x = 0

        # If the camera is at the bottom side, move the camera down
        if y < self.viewport.bottom + scroll_sensitivity and y > self.viewport.bottom:
            self.camera_direction_y = -1
        # If the camera is at the top side, move the camera up
        elif y > self.viewport.top - scroll_sensitivity:
            self.camera_direction_y = 1
        else:
            self.camera_direction_y = 0

class SelectorLayer(cocos.layer.scrolling.ScrollableLayer):
    def __init__ (self):
        super(SelectorLayer, self).__init__()

        self.primary_selector_sprite = cocos.sprite.Sprite('primary_selector.png')
        self.primary_selector_sprite.image_anchor_x = 0
        self.primary_selector_sprite.image_anchor_y = 0
        self.primary_selector_sprite.position = (0, 0)

        self.add(self.primary_selector_sprite)

class TintLayer(cocos.layer.scrolling.ScrollableLayer):
    """This creates layers to put a tint on the terrain.
    """
    def __init__(self, style):
        super(TintLayer, self).__init__()

        # Set up some parameters based on the style.
        self.make_tint_image = None
        self.set_function_by_style(style)

        # Get the dimensions of the map.
        map_dimensions = {
            'width':25,
            'height':15
        }

        # Get the tile_size
        tile_size = 32

        # Compose the layer image.
        self.tint_image = self.make_tint_image(map_dimensions, tile_size)

        # Center the image overlay on top of the terrain.
        self.tint_image.image_anchor_x = 0
        self.tint_image.image_anchor_y = 0
        self.tint_image.position = (0, 0)

        # Now add the image to this object.
        self.add(self.tint_image)

    def set_function_by_style(self, style):
        """Set up functions based on the style of the TintLayer.
        """
        functions_by_style = {
            'shading' :  self.make_shading_image,
            'overlay' : self.make_overlay_image
        }

        self.make_tint_image = functions_by_style[style]

    def make_overlay_image(self, map_dimensions, tile_size):
        """Return a single image that contains the overlay colors
        """
        # Calculate dimensions of the master image.
        image_width = map_dimensions['width'] * tile_size;
        image_height = map_dimensions['height'] * tile_size;

        # Prepare data to store the raw colors.
        image_data = []
        tile_colors = {
            'red' : [128,0,0,255],
            'blue' : [0,0,128,255],
            'transparent' : [0,0,0,0],
        }

        overlay_by_coordinate = {
            0 : {
                0 : 'blue',
                1 : 'blue',
            },
            1 : {
                0 : 'red',
            },
            2 : {
                0 : 'blue',
            },
            10 : {
                0 : 'blue',
            }
        }

        for y in range(0, image_height):
            for x in range(0, image_width):
                map_coordinate_i = int(x / tile_size)
                map_coordinate_j = int(y / tile_size)

                # Get the overlay color found at this coordinate.
                tile_color = 'transparent'

                if map_coordinate_j in overlay_by_coordinate and map_coordinate_i in overlay_by_coordinate[map_coordinate_j]:
                    tile_color = overlay_by_coordinate[map_coordinate_j][map_coordinate_i]
                image_data.extend(tile_colors[tile_color])

        # Translate the data to cbytes.
        rawData = (GLubyte * len(image_data))(*image_data)

        # Create an image containing the image data.
        highlighted_image = pyglet.image.ImageData(
            image_width,
            image_height,
            'RGBA',
            rawData
        )

        composed_image = cocos.sprite.Sprite(highlighted_image)

        # Add an action to fade the terrain overlay.
        fade_action = FadeTo(64, 2) + FadeTo(192, 1)
        composed_image.do(Repeat(fade_action))

        return composed_image

    def make_shading_image(self, map_dimensions, tile_size):
        """Return a single image that contains the
        """
        # Calculate dimensions of the master image.
        image_width = map_dimensions['width'] * tile_size;
        image_height = map_dimensions['height'] * tile_size;

        # Prepare data to store the raw colors.
        image_data = []
        shade_color = [0,0,0,127]
        transparent_color = [0,0,0,0]

        for y in range(0, image_height):
            for x in range(0, image_width):
                map_coordinate_i = int(x / tile_size)
                map_coordinate_j = int(y / tile_size)

                # Determine the shading color based on the coordinate.
                if map_coordinate_i == 10 and map_coordinate_j == 5:
                    tile_color = transparent_color
                else:
                    tile_color = shade_color

                image_data.extend(tile_color)

        # Translate the data to cbytes.
        rawData = (GLubyte * len(image_data))(*image_data)

        # Create an image containing the image data.
        shaded_image = pyglet.image.ImageData(
            image_width,
            image_height,
            'RGBA',
            rawData
        )

        shaded_sprite = cocos.sprite.Sprite(shaded_image)

        return shaded_sprite

class OverlayLayer(TintLayer):
    # This layer applies a colored overlay.
    def __init__(self):
        super(OverlayLayer, self).__init__('overlay')

class ShadingLayer(TintLayer):
    # This layer applies a shaded overlay on the screen.
    def __init__(self):
        super(ShadingLayer, self).__init__('shading')

class UnitLayer(cocos.layer.scrolling.ScrollableLayer):
    """Displays graphical representations of the Units on the map.
    """
    def __init__(self):
        super(UnitLayer, self).__init__()

        tilesize = 32

        # Load some sprites
        self.unit_sprite = cocos.sprite.Sprite("StickUnitRed.png", anchor=(0,0))

        # Move sprites into position
        self.unit_sprite.do(Place((10 * tilesize, 5 * tilesize)))

        # Add the sprites to the layer.
        self.add(self.unit_sprite)

class ObstacleLayer(cocos.layer.scrolling.ScrollableLayer):
    """Displays graphical representations of the Units on the map.
    """
    def __init__(self):
        super(ObstacleLayer, self).__init__()

        tilesize = 32

        # Load some sprites
        self.unit_sprite = cocos.sprite.Sprite("ObstacleRock.png", anchor=(0,0))

        # Move sprites into position
        self.unit_sprite.do(Place((2 * tilesize, 3 * tilesize)))

        # Add the sprites to the layer.
        self.add(self.unit_sprite)

class TerrainLayer(cocos.tiles.RectMapLayer):
    """Builds the surface the units will travel across.
    """
    def __init__(self, width, height):
        tile_cells = tiles.load_tmx('red_and_gray.tmx')
        layer1 = tile_cells['Tile Layer 1']

        super(TerrainLayer, self).__init__(
            layer1.id,
            layer1.tw,
            layer1.th,
            layer1.cells
        )

        # Set the width and height of the layer.
        self.layer_width = self.px_width
        self.layer_height = self.px_height

class BackgroundColorLayer(cocos.layer.util_layers.ColorLayer):
    """Draws a static background.
    """
    def __init__(self, screen_width, screen_height):
        super(BackgroundColorLayer, self).__init__(192,192,192,255,width=screen_width, height=screen_height)
        self.position = (0,0)

if __name__ == "__main__":
    screen_width = 800
    screen_height = 600

    cocos.director.director.init(width=screen_width, height=screen_height)

    # Make the layers here
    background_layer = BackgroundColorLayer(screen_width, screen_height)
    scrolling_layer_manager = ScrollableLayerManager(screen_width, screen_height)

    # Make the Scene here
    battle_scene = cocos.scene.Scene(
        background_layer,
        scrolling_layer_manager
    )
    cocos.director.director.run(battle_scene)

# Menu Layer
# Dialogue Layer
# Hit Spark Layer
# Combat Status Layer

# How do I hide layers?
