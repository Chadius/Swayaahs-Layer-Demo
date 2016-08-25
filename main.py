""" Layering Demo

This should demonstrate the various layers involved in the Turn Based Strategy game I'm working on.
"""

from __future__ import division, print_function, unicode_literals

import pyglet
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
        # Shading Layer
        # Unit Layer
        # Obstacle Layer
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

        # TODO: Add a 50 pixel buffer.
        # Set the width and height of the layer.
        self.layer_width = self.px_width + 100
        self.layer_height = self.px_height + 100

class BackgroundColorLayer(cocos.layer.util_layers.ColorLayer):
    """Draws a static background.
    """
    def __init__(self, screen_width, screen_height):
        super(BackgroundColorLayer, self).__init__(192,192,192,255,width=screen_width, height=screen_height)
        self.position = (0,0)

if __name__ == "__main__":
    screen_width = 800
    screen_height = 300

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

