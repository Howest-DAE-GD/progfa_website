import pygame
import asyncio
import math
import os
import re
import sys
from urllib.parse import urlparse  # image url check
import urllib.request  # image url check
from io import BytesIO  # image url check
from typing import Union  # hint for multiple possible parameter types
from typing import List, Tuple
from enum import Enum

from progfa.progfa_image import ProgfaImage
from pygame.math import Vector2


class MouseButton(Enum):
    NONE = 0
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3
    SCROLL_UP = 4
    SCROLL_DOWN = 5
    SIDE_1 = 6
    SIDE_2 = 7


class ShapeMode(Enum):
    CENTER = 0
    CORNER = 1


def _hex_to_rgb(hex_color: Union[int, str]) -> Tuple[int, int, int, int]:
    """
    *Engine helper function, advised not to use this function.*\n
    """
    hex_pattern = r'^[0-9A-Fa-f]+$'

    assert isinstance(hex_color, (int, str)), '[ENGINE ERROR] hex_color should be a hex value (e.g. 0xFF0000) " \
                                              "or a hex string (e.g. "#FF0000")'

    if isinstance(hex_color, int):
        hex_value = hex(hex_color)[2:].zfill(6)  # Convert integer to hexadecimal string with leading zeros
    else:  # isinstance(args[0], str) automatically , since checked in assert
        if hex_color.startswith("#"):
            hex_value = hex_color[1:]
        else:
            hex_value = hex_color
        hex_value = hex_value.zfill(6)

    is_valid_hex = re.match(hex_pattern, hex_value)
    assert is_valid_hex, "[ENGINE ERROR] Invalid input format for hex color value; should be proper hex " \
                         "value (e.g. 0xFF0000) or hex string (e.g. #FF0000)"

    hex_string = "#" + hex_value.upper()  # Prepend "#" to the hexadecimal string
    clr = pygame.Color(hex_string)
    return clr.r, clr.g, clr.b, clr.a


def _get_host():
    if sys.platform == 'emscripten':
        import js
        url = js.window.location.href
        host = url.rsplit('/', 1)[0]
        print(f'RUNNING IN BROWSER ON {host}')
        return host
    else:
        print('RUNNING IN PYTHON')
        return None


class ProgfaEngine:
    """
    A class representing the programming for artists 1 engine, using pygame.
    """
    _frames = []  # Class variable, behaves like a static variable

    def __init__(self, width, height):
        self._host = _get_host()

        self._background_color = 0, 0, 0
        self._outline_color = pygame.Color(255, 0, 255, 255)
        self._fill_color = pygame.Color(0, 255, 255, 255)

        self._shape_mode = ShapeMode.CORNER

        pygame.init()
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode([width, height])
        self._fps = 60

        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_pressed = False
        self._mouse_button = MouseButton.NONE

        self._key = None
        self._key_pressed = False

        self._clock = pygame.time.Clock()
        self._font_name = 'arial'
        self._default_font = True
        self._font = pygame.font.SysFont(self._font_name, 16)

        pygame.mouse.set_cursor(*pygame.cursors.diamond)

    @property
    def width(self) -> Union[float, int]:
        """
        Returns the width of the window.
        """
        return self._width

    @width.setter
    def width(self, value: Union[float, int]):
        """
        Changes the width of the window.
        """
        self.set_resolution(value, self._height)

    @property
    def height(self) -> Union[float, int]:
        """
        Returns the height of the window.
        """
        return self._height

    @height.setter
    def height(self, value: Union[float, int]):
        """
        Changes the height of the window.
        """
        self.set_resolution(self._width, value)

    @property
    def fps(self) -> int:
        """
        Get the current frames per second that is being used as the speed of the game loop.
        """
        return self._fps

    @fps.setter
    def fps(self, value: int):
        """
        Changes the speed of the game loop by changing the frames per second.
        """
        self._fps = value

    def set_fps(self, fps: int):
        """
        Changes the speed of the game loop by changing the frames per second.
        :param fps: frames per second
        """
        self._fps = fps

    @property
    def shape_mode(self):
        """Returns the current shape mode used to draw shapes from. 0 = ShapeMode.CENTER, 1 = ShapeMode.CORNER."""
        return self._shape_mode

    @shape_mode.setter
    def shape_mode(self, value: Union[ShapeMode | int]):
        """
        Defines if shapes will be drawn from their center point or top-left corner.
        ShapeMode.CENTER or ShapeMode.CORNER
        :Examples:
        >>> engine.shape_mode = ShapeMode.CENTER
        """
        assert value == ShapeMode.CENTER or value == ShapeMode.CORNER \
               or value == 0 or value == 1, \
            "[ENGINE ERROR] shape_mode should be set to either ShapeMode.CENTER (0) or ShapeMode.CORNER (1)!"
        self._shape_mode = value if isinstance(value, ShapeMode) else ShapeMode(value)

    @property
    def mouse_x(self) -> float:
        """
        Get the current x-coordinate of the mouse.
        """
        return self._mouse_x

    @property
    def mouse_y(self) -> float:
        """
        Get the current y-coordinate of the mouse.
        """
        return self._mouse_y

    @property
    def mouse_pressed(self) -> bool:
        """
        Returns True if a mouse button is currently pressed, otherwise it returns False.
        """
        return self._mouse_pressed

    @property
    def mouse_button(self) -> MouseButton:
        """
        Returns the number of the mouse button that was pressed (readonly).
        Possible return values: see MouseButton information.
        """
        if not self._mouse_pressed:
            return MouseButton.NONE
        return self._mouse_button

    @property
    def key(self):
        """
        Get the current key that was pressed.
        """
        return self._key

    def key_pressed(self) -> bool:
        """
        Returns True if a key is currently pressed, or False if no key is currently pressed.
        """
        return self._key_pressed

    def __getattr__(self, name):
        if hasattr(pygame.Surface, name):
            return getattr(self._screen, name)
        raise AttributeError(f"'ProgfaEngine' object has no attribute '{name}'")

    def set_resolution(self, width: float, height: float) -> None:
        """
        Changes the window size.

        :param width: The new width of the window.
        :param height: The new height of the window.

        :return: 

        :Examples:
        >>> engine.set_resolution(500, 300)
        >>> engine.set_resolution(width=500, height=300)
        """
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode([width, height])

    # endregion Shape mode

    def _get_coordinates(self, x, y, width, height):
        """
        Engine helper function, translates coordinates to top left based on shape mode.
        """
        if self._shape_mode == ShapeMode.CENTER:
            return Vector2(x - width / 2, y - height / 2)
        else:
            return Vector2(x, y)

    # endregion Shape mode

    # region Colors

    @property
    def transparency(self) -> float:
        """
        Returns the transparency component of the fill color.
        :raises ValueError: If no color is set (fill color is None).
        """
        return self._fill_color.a / 255.0

    @transparency.setter
    def transparency(self, value: Union[float, int]):
        """
        Changes the red value of the fill color. Give a decimal percentage (value between 0.0 and 1.0).
        """
        if self._fill_color is None:
            self._fill_color = pygame.Color(0, 0, 0)
        # Ensure the value is within the valid range (0.0 - 1.0)
        value = max(0.0, min(1.0, float(value)))
        self._fill_color.a = int(value * 255)

    @property
    def color(self) -> Union[Tuple[float, float, float, float], None]:
        """
        Returns the fill color as a tuple of RGBA components.
        """
        if self._fill_color is None:
            return None
        r = self._fill_color.r / 255.0
        g = self._fill_color.g / 255.0
        b = self._fill_color.b / 255.0
        a = self._fill_color.a / 255.0
        return r, g, b, a

    @color.setter
    def color(self, value: Union[Tuple[float, float, float], Tuple[float, float, float, float], None]):
        """
        Changes the fill color based on a tuple of RGB or RGBA components.
        Ensure these are decimal percentages (values between 0.0 and 1.0).
        Choose None to remove the fill (color) for following shapes.

        :Examples:
        >>> engine.color = None                 # removes the fill color

        >>> engine.color = (1, 0.2, 0)          # color_r = 1, color_g = 0.2, color_b = 0 (fully opaque)
        >>> engine.color = (1, 0.2, 0, 0.5)     # color_r = 1, color_g = 0.2, color_b = 0, transparency = 0.5
        """
        if value is None:
            self._fill_color = None
            return
        elif len(value) == 3:
            r, g, b = value
            alpha = 1.0  # Default alpha value
        elif len(value) == 4:
            r, g, b, alpha = value
        else:
            raise ValueError("Invalid input tuple. Use (R, G, B) or (R, G, B, A).")

        # Ensure the RGB values are within the valid range (0.0 - 1.0)
        r = max(0.0, min(1.0, r))
        g = max(0.0, min(1.0, g))
        b = max(0.0, min(1.0, b))
        a = max(0.0, min(1.0, alpha))
        self._fill_color = pygame.Color(0, 0, 0)
        self._fill_color.r = int(r * 255)
        self._fill_color.g = int(g * 255)
        self._fill_color.b = int(b * 255)
        self._fill_color.a = int(a * 255)

    @property
    def background_color(self) -> Tuple[float, float, float]:
        """
        Gets the current background color of the window (r, g, b).
        :return: current background color
        """
        return self._background_color

    @background_color.setter
    def background_color(self, value: Union[Tuple[float, float, float], None]):
        """
        Changes the background color based on a tuple of RGB components.
        Ensure these are decimal percentages (values between 0.0 and 1.0).

        :Examples:
        >>> engine.background_color = (1, 0.2, 0)
        """
        if value is None:
            return
        elif len(value) == 3:
            r, g, b = value
        else:
            raise ValueError("Invalid input tuple. Use (R, G, B) for background color.")

        # Ensure the RGB values are within the valid range (0.0 - 1.0)
        r = max(0.0, min(1.0, r))
        g = max(0.0, min(1.0, g))
        b = max(0.0, min(1.0, b))
        self._background_color = r, g, b
        self._screen.fill((int(r * 255), int(g * 255), int(b * 255)))

    @property
    def outline_color(self) -> Union[Tuple[float, float, float], None]:
        """
        Returns the outline color as a tuple of RGBA components, or None if there is currently no outline.
        """
        if self._outline_color is None:
            return None
        r = self._outline_color.r / 255.0
        g = self._outline_color.g / 255.0
        b = self._outline_color.b / 255.0
        return r, g, b

    @outline_color.setter
    def outline_color(self, value: Union[Tuple[float, float, float], None]):
        """
        Changes the outline color based on a tuple of RGB components.
        Ensure these are decimal percentages (values between 0.0 and 1.0).
        Choose None to remove the outline for following shapes.

        :Examples:
        >>> engine.outline_color = None             # removes the fill color
        >>> engine.outline_color = (1, 0.2, 0)      # outline_color_r = 1, outline_color_g = 0.2, outline_color_b = 0
        """
        if value is None:
            self._outline_color = None
            return
        elif len(value) == 3:
            r, g, b = value
        else:
            raise ValueError("Invalid input tuple. Use (R, G, B) for outline colors, or None to remove it.")

        # Ensure the RGB values are within the valid range (0.0 - 1.0)
        r = max(0.0, min(1.0, r))
        g = max(0.0, min(1.0, g))
        b = max(0.0, min(1.0, b))
        self._outline_color = pygame.Color(0, 0, 0)
        self._outline_color.r = int(r * 255)
        self._outline_color.g = int(g * 255)
        self._outline_color.b = int(b * 255)

    def has_outline(self) -> bool:
        """
        Checks if the object has a stroke color (True) or not (False).
        Will return False after executing unset_outline_color.
        """
        return self._outline_color is not None and self._outline_color != (None, None, None)

    def has_fill(self) -> bool:
        """
        Checks if the object has a fill color (True) or not (False).
        Will return False after executing unset_fill_color.
        """
        return self._fill_color is not None and self._fill_color != (None, None, None)

    # endregion Colors

    # region Color helpers

    @staticmethod
    def _is_decimal_percentage(value) -> bool:
        """
        *Engine helper function, advised not to use this function.*\n
        """
        if not isinstance(value, (float, int)):
            return False
        if not 0 <= value <= 1:
            return False
        return True

    # endregion Color helpers

    # region Draw basic shapes

    def draw_dot(self, x: Union[int, float], y: Union[int, float], outline_width: int = 1) -> None:
        """
        Draws a dot in position (x, y).
        The size of the dot is determined by the stroke width.
        Uses the current stroke color.

        :param x: The x-coordinate of the dot.
        :param y: The y-coordinate of the dot.
        :param outline_width: Optional. The stroke width to draw the dot (bigger stroke = bigger dot).
                             Defaults to 1.

        :return: 

        Examples:
        >>> engine.draw_dot(20, 30)       # uses stroke size 1
        >>> engine.draw_dot(20, 30, 4)    # uses stroke size 4
        """
        if self.has_outline():
            pygame.draw.circle(self._screen, self._outline_color, (x, y), outline_width)

    def draw_circle(self, x: Union[int, float], y: Union[int, float], diameter: Union[int, float],
                    outline_width: int = 1) -> None:
        """
        Draws a circle in position x, y, using diameter for dimensions (width = height = size).
        To change if position is CENTER or top left CORNER, use the .shape_mode property (default = center).

        :param x: The x position of the circle (center or top left, determined by shape mode).
        :param y: The y position of the circle (center or top left, determined by shape mode).
        :param diameter: The diameter (width/height) of the circle.
        :param outline_width: Optional (default = 1). The stroke width to use around your circle.

        :return: 

        Examples:
        >>> engine.draw_ellipse(20, 30, 200, 100)       # Circle in pos 20, 30, size 200x100, stroke 1
        >>> engine.draw_ellipse(20, 30, 200, 100, 4)    # Circle in pos 20, 30, size 200x100, stroke 4
        """
        self.draw_ellipse(x, y, diameter, diameter, outline_width)

    def draw_ellipse(self, x: Union[int, float], y: Union[int, float],
                     width: Union[int, float], height: Union[int, float], outline_width: int = 1) -> None:
        """
        Draws an ellipse in position x, y, using dimensions width, height.
        To change if position is CENTER or top left CORNER, use the .shape_mode property (default = center).

        :param x: The x position of the ellipse (center or top left, determined by shape mode).
        :param y: The y position of the ellipse (center or top left, determined by shape mode).
        :param width: The width of the ellipse.
        :param height: The height of the ellipse.
        :param outline_width: Optional (default = 1). The stroke width to use around your ellipse.

        :return: 

        Examples:
        >>> engine.draw_ellipse(20, 30, 200, 100)       # ellipse in pos 20, 30, size 200x100, stroke 1
        >>> engine.draw_ellipse(20, 30, 200, 100, 4)    # ellipse in pos 20, 30, size 200x100, stroke 4
        """
        coordinates = self._get_coordinates(x, y, width, height)
        rect = pygame.Rect(coordinates.x, coordinates.y, width, height)
        if self.has_fill():
            fill_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.ellipse(fill_surface, self._fill_color, fill_surface.get_rect())
            self._screen.blit(fill_surface, (coordinates.x, coordinates.y))
        if self.has_outline():
            pygame.draw.ellipse(self._screen, self._outline_color, rect, outline_width)

    def draw_arc(self, x: Union[int, float], y: Union[int, float], width: Union[int, float], height: Union[int, float],
                 start_angle: Union[int, float], end_angle: Union[int, float], outline_width: int = 1) -> None:
        """
        Draws an arc in position x, y, using width, height for dimensions of the surrounding ellipse,
        and angles for the arc size.

        Change stroke/fill color or shape mode (default = center) using the engine functions.

        :param x: The x position of the rectangle (center or top left, determined by shape mode).
        :param y: The y position of the rectangle (center or top left, determined by shape mode).
        :param width: The width of the circle that surrounds the arc (width if arc would be a full ellipse).
        :param height: The height of the circle that surrounds the arc (height if arc would be a full ellipse).

        :param start_angle: The angle (in degrees) in which to start the arc.
        :param end_angle: The angle (in degrees) in which to end the arc; this is not the arc (angle) size!

        :param outline_width: Optional (default = 1). The stroke width to use around your arc.

        :return: 

        Examples:
        >>> # top part of an ellipse, stroke 1:
        >>> engine.draw_arc(20, 30, 200, 100, 180, 360)
        >>> # bottom part of an ellipse, stroke 4:
        >>> engine.draw_arc(20, 30, 200, 100, 0, 180, 4)
        """
        if height is None:
            height = width
        coordinates = self._get_coordinates(x, y, width, height)
        # rect = pygame.Rect(coordinates.x, coordinates.y, width, height)
        if self.has_fill():
            angle_range = end_angle - start_angle
            if angle_range < 0:
                angle_range += 360
            num_segments = int(angle_range / 3)  # Adjust the number of segments as desired

            # Calculate the angle step size for each triangle
            angle_step = math.radians((end_angle - start_angle) / num_segments)
            current_angle = math.radians(start_angle)

            # Iterate through the segments and draw triangles to approximate the filled arc
            for _ in range(num_segments):
                x1 = coordinates.x + width // 2
                y1 = coordinates.y + height // 2
                x2 = coordinates.x + width // 2 + int(math.cos(current_angle) * width / 2)
                y2 = coordinates.y + height // 2 + int(math.sin(current_angle) * height / 2)
                x3 = coordinates.x + width // 2 + int(math.cos(current_angle + angle_step) * width / 2)
                y3 = coordinates.y + height // 2 + int(math.sin(current_angle + angle_step) * height / 2)

                pygame.draw.polygon(self._screen, self._fill_color, [(x1, y1), (x2, y2), (x3, y3)])

                current_angle += angle_step
        # Draw the stroke of the arc
        if self.has_outline():
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            # pygame.draw.arc(self.screen, self.stroke_color, rect, start_rad, end_rad, 4)
            num_segments = int(abs(end_angle - start_angle) / 10)  # Adjust the number of segments as desired

            # Calculate the angle step size for each segment
            angle_step = math.radians((end_angle - start_angle) / num_segments)
            current_angle = math.radians(start_angle)

            center_x = coordinates.x + width // 2
            center_y = coordinates.y + height // 2

            # Iterate through the segments and draw lines to approximate the arc with a thicker stroke
            for _ in range(num_segments):
                start_x = center_x + int(math.cos(current_angle) * (width + 1) / 2)
                start_y = center_y + int(math.sin(current_angle) * (height + 1) / 2)
                end_x = center_x + int(math.cos(current_angle + angle_step) * (width + 1) / 2)
                end_y = center_y + int(math.sin(current_angle + angle_step) * (height + 1) / 2)

                pygame.draw.line(self._screen, self._outline_color, (start_x, start_y), (end_x, end_y), outline_width)

                current_angle += angle_step

            # Connect the stroke to the center
            start_x = center_x + int(math.cos(start_rad) * (width + 1) / 2)
            start_y = center_y + int(math.sin(start_rad) * (height + 1) / 2)
            end_x = center_x + int(math.cos(end_rad) * (width + 1) / 2)
            end_y = center_y + int(math.sin(end_rad) * (height + 1) / 2)
            pygame.draw.line(self._screen, self._outline_color, (center_x, center_y), (start_x, start_y), outline_width)
            pygame.draw.line(self._screen, self._outline_color, (center_x, center_y), (end_x, end_y), outline_width)

    def draw_square(self, x: Union[int, float], y: Union[int, float], size: Union[int, float],
                    outline_width: int = 1) -> None:
        """
        Draws a square in position x, y, using size for dimensions (width=height=size).
        To change if position is CENTER or top left CORNER, use the .shape_mode property (default = center).
        :param x: The x position of the rectangle (center or top left, determined by shape mode).
        :param y: The y position of the rectangle (center or top left, determined by shape mode).
        :param size: The dimensions (width/height) of the square.
        :param outline_width: Optional (default = 1). The stroke width to use around your square.
        :return: 

        Examples:
        >>> engine.draw_square(20, 30, 200)     # stroke width 1
        >>> engine.draw_square(20, 30, 200, 4)  # stroke width 4
        >>> engine.draw_square(x=20, y=30, size=200)
        """
        self.draw_rectangle(x, y, size, size, outline_width)

    def draw_rectangle(self, x: Union[int, float], y: Union[int, float],
                       width: Union[int, float], height: Union[int, float], outline_width=1) -> None:
        """
        Draws a rectangle in position x, y, using dimensions width, height.
        To change if position is CENTER or top left CORNER, use the .shape_mode property (default = center).

        :param x: The x position of the rectangle (center or top left, determined by shape mode).
        :param y: The y position of the rectangle (center or top left, determined by shape mode).
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        :param outline_width: Optional (default = 1). The stroke width to use around your rectangle.

        :return: 

        Examples:
        >>> engine.draw_rectangle(20, 30, 200, 100)                   # stroke 1
        >>> engine.draw_rectangle(20, 30, 200, 100, 4)                # stroke 4
        >>> engine.draw_rectangle(x=20, y=30, width=200, height=100)  # stroke 1
        """
        coordinates = self._get_coordinates(x, y, width, height)
        rect = pygame.Rect(coordinates.x, coordinates.y, width, height)
        if self.has_fill():
            fill_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(fill_surface, self._fill_color, fill_surface.get_rect())
            self._screen.blit(fill_surface, (coordinates.x, coordinates.y))
        if self.has_outline():
            pygame.draw.rect(self._screen, self._outline_color, rect, outline_width)

    def draw_triangle(self, x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float],
                      x3: Union[int, float], y3: Union[int, float], outline_width: int = 1) -> None:
        """
        Draws a triangle with the 3 (x,y) positions given. You can choose which is the first, second and third point;
        it makes no difference.

        :param x1: The x position of the FIRST point of your triangle.
        :param y1: The y position of the FIRST point of your triangle.
        :param x2: The x position of the SECOND point of your triangle.
        :param y2: The y position of the SECOND point of your triangle.
        :param x3: The x position of the THIRD point of your triangle.
        :param y3: The y position of the THIRD point of your triangle.
        :param outline_width: Optional (default = 1). The stroke width to use around your triangle.

        :return: 

        :Examples:
        >>> engine.set_fill_color(1, 0, 0)                 # red fill
        >>> engine.unset_outline_color()                    # remove stroke
        >>> engine.draw_triangle(10, 10, 20, 50, 80, 100)  # triangle
        """
        vertices = [(x1, y1),
                    (x2, y2),
                    (x3, y3)]
        self.draw_poly(vertices, outline_width)

    def draw_quad(self, x1: Union[float, int], y1: Union[float, int], x2: Union[float, int], y2: Union[float, int],
                  x3: Union[float, int], y3: Union[float, int], x4: Union[float, int], y4: Union[float, int],
                  outline_width: int = 1) -> None:
        """
        Draws a quad with the four given x, y positions.
        The order of the arguments is the order in which they will be drawn. Quad is automatically closed.

        :param x1: The x position of the FIRST point of your quad.
        :param y1: The y position of the FIRST point of your quad.
        :param x2: The x position of the SECOND point of your quad.
        :param y2: The y position of the SECOND point of your quad.
        :param x3: The x position of the THIRD point of your quad.
        :param y3: The y position of the THIRD point of your quad.
        :param x4: The x position of the FOURTH point of your quad.
        :param y4: The y position of the FOURTH point of your quad.
        :param outline_width: Optional (default = 1). The stroke width to use around your quad.

        :return: 

        Examples:
        >>> engine.draw_quad(10, 10, 20, 50, 80, 100, 40, 30)     # stroke width 1
        >>> engine.draw_quad(10, 10, 20, 50, 80, 100, 40, 30, 4)  # stroke width 4
        """
        vertices = [(x1, y1),
                    (x2, y2),
                    (x3, y3),
                    (x4, y4)]
        self.draw_poly(vertices, outline_width)

    def draw_poly(self, vertices: List[Tuple[float, float]], outline_width: int = 1) -> None:
        """
        Draws a polygon with the given vertices.

        :param self: (ignore)
        :param vertices: List of (x,y) tuple combinations for every point of the shape.
            Format: [(x1,y1), (x2,y2), (x3,y3), (x4,y4), ...]
        :param outline_width: Optional (default = 1).
            The stroke width to use around your triangle.

        :return: 

        :Examples:
        >>> shape_vertices = [(10, 10), (20, 50), (80, 100), (40, 30)]
        >>> engine.draw_poly(shape_vertices)       # stroke width 1
        >>> engine.draw_poly(shape_vertices, 4)    # stroke width 4
        """
        if self.has_fill():
            min_x = min(vertices, key=lambda vertex: vertex[0])[0]
            max_x = max(vertices, key=lambda vertex: vertex[0])[0]
            min_y = min(vertices, key=lambda vertex: vertex[1])[1]
            max_y = max(vertices, key=lambda vertex: vertex[1])[1]
            width = max_x - min_x
            height = max_y - min_y
            fill_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            adjusted_vertices = [(x - min_x, y - min_y) for x, y in vertices]
            pygame.draw.polygon(fill_surface, self._fill_color, adjusted_vertices)
            self._screen.blit(fill_surface, (min_x, min_y))
        if self.has_outline():
            pygame.draw.polygon(self._screen, self._outline_color, vertices, outline_width)

    def draw_line(self, x1: Union[int, float], y1: Union[int, float], x2: Union[int, float], y2: Union[int, float],
                  outline_width: int = 1) -> None:
        """
        Draws a line starting in position x1, y1, and ending in position x2, y2.
        Uses stroke color. WARNING: the line will not be visible if stroke color is unset/None.

        :param self: (ignore)
        :param x1: The x position of the first point of the line.
        :param y1: The y position of the first point of the line.
        :param x2: The x position of the second point of the line.
        :param y2: The y position of the second point of the line.
        :param outline_width: Optional (default = 1). The stroke width to draw your line.
            If 0, the line will not be visible.

        :return: 

        :Examples:
        >>> engine.draw_line(20, 30, 200, 100)       # draw a line from (20, 30) to (200, 100) with a stroke width of 1
        >>> engine.draw_line(20, 30, 200, 100, 4)    # draw a line from (20, 30) to (200, 100) with a stroke width of 4
        """

        if self.has_outline():
            pygame.draw.line(self._screen, self._outline_color, (x1, y1), (x2, y2), outline_width)

    # endregion Draw basic shapes

    def take_screenshot(self, filename: str) -> None:
        """
        Takes a screenshot of the current game window and saves it.
        Supported file types are: ".png", ".jpg", ".jpeg", ".bmp", ".tga".
        Both TGA, and BMP file formats create uncompressed files.
        :param filename: the filename to use when saving the screenshot. The extension defines the format it will be
        saved in.
        :return: Nothing.
        """
        valid_extensions = {"png", "jpg", "jpeg", "bmp", "tga"}
        if not re.match(r".*\.[a-zA-Z]{3,4}$", filename):  # did they not provide an extension?
            filename = f"{filename}.png"  # png by default
        else:
            # Extract the extension (case-insensitive) and check if it's in valid extensions
            extension = filename.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise ValueError(f"Unsupported file format: '{filename}' is not a valid image format.")

        # Ensure the screenshots directory exists
        screenshots_dir = "screenshots"
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Save the screenshot in the screenshots directory
        filepath = os.path.join(screenshots_dir, filename)
        pygame.image.save(self._screen, filepath)
        print(f"-> Screenshot saved as {filepath}.")

    # region Text and fonts
    def set_font(self, font: str) -> None:
        """
        Sets the font that will be used when calling the draw_text function.

        :param font: either the name of a local file in Resources (file type .ttf or .otf), or a system font name

        :return:

        :Examples:
        >>> engine.set_font("example.ttf")            # Loads example.ttf from project's Resources folder
        >>> engine.set_font("Resources/example.otf")  # Loads example.ttf from project's Resources folder
        >>> # engine.set_font("example.vlw")          # Raises AssertionError; only supports .ttf and .otf extensions

        :raises:
        AssertionError if font has an extention, and this extenion is different from the supported .ttf or .otf.
        Error will not be raised if font has no extention, in which case it will try to use a system font.

        """
        valid_extensions = r'\.(ttf|otf)?$'  # either .otf, .ttf or no extension (for system file)
        assert re.search(valid_extensions, font), f"[ENGINE ERROR] The filename '{font}' is not a valid font file."

        if not font.startswith("Resources/"):
            font = f"Resources/{font}"
        self._font_name = font
        self._font = pygame.font.Font(font)
        self._default_font = False

    def set_font_size(self, size: Union[int, float]) -> None:
        """
        Changes the font size that will be used to draw text.

        :param size: font size that will be used to draw text
        :return:
        :examples:
        >>> engine.set_font_size(21)  # Changes font size to 21
        """
        assert isinstance(size, int)
        if self._default_font:
            self._font = pygame.font.SysFont(self._font_name, size)
        else:
            self._font = pygame.font.Font(self._font_name, size)

    def draw_text(self, text: str, x: Union[float, int], y: Union[float, int], centered: bool = False) -> None:
        """
        Draws text using the current font and fill color.
        WARNING: if fill color is unset (None), text will not be visible.

        :param text: the text that should be drawn in the window
        :param x: x position of the text. If centered, this is the center x, otherwise this is the left.
        :param y: y position of the text. If centered, this is the center y, otherwise this is the top.
        :param centered: Optional, default = False.
                If True, text will be drawn from center. If False, text is drawn from top left.
        :return:

        :Examples:
        >>> draw_text("Hello DAE", 20, 30)          # Draws "Hello DAE", top left position is 20,30
        >>> draw_text("Hello DAE", 200, 300, True)  # Draws "Hello DAE", text is centered in position 200,300
        """
        if text is None:
            return
        text_surface = self._font.render(text, True, self._fill_color)
        if centered:
            text_rect = text_surface.get_rect()
            text_rect.center = (x, y)
        else:
            text_rect = text_surface.get_rect()
            text_rect.x = x
            text_rect.y = y
        self._screen.blit(text_surface, text_rect)

    # endregion Text and fonts

    # region collision detection

    def colliding_circles(self, x: float, y: float, diameter: float, x2: float, y2: float, diameter2: float) -> bool:
        """
        Checks if two circles are colliding. The given x, y coordinates are based on the shape_mode!
        :param x: x coordinate of the first circle.
        :param y: y coordinate of the first circle.
        :param diameter: diameter of the first circle.
        :param x2: x coordinate of the second circle.
        :param y2: y coordinate of the second circle.
        :param diameter2: diameter of the second circle.
        :return: True if colliding, False if not.
        """
        pos1 = Vector2(x, y)
        pos2 = Vector2(x2, y2)
        if self._shape_mode == ShapeMode.CORNER:
            pos1.x += diameter / 2
            pos1.y += diameter / 2
            pos2.x += diameter2 / 2
            pos2.y += diameter2 / 2
        distance = math.sqrt(math.pow(pos1.x - pos2.x, 2) + math.pow(pos1.y - pos2.y, 2))
        return distance <= (diameter / 2 + diameter2 / 2)

    def colliding_point_in_circle(self, point_x: float, point_y: float,
                                  circle_x: float, circle_y: float, diameter: float) -> bool:
        """
        Checks if a certain point is inside a circle. The given x, y coordinates are based on the shape_mode!
        :param point_x: x coordinate of the point.
        :param point_y: y coordinate of the point.
        :param circle_x: x coordinate of the circle.
        :param circle_y: y coordinate of the circle.
        :param diameter: diameter of the circle.
        :return: True if point is in circle, False if not.
        """
        # pos = self._get_coordinates(circle_x, circle_y, diameter, diameter)
        pos = Vector2(circle_x, circle_y)
        if self._shape_mode == ShapeMode.CORNER:
            pos.x += diameter / 2
            pos.y += diameter / 2
        distance = math.sqrt(math.pow(pos.x - point_x, 2) + math.pow(pos.y - point_y, 2))
        return distance <= (diameter / 2)

    def colliding_rects(self, x: float, y: float, w: float, h: float, x2: float, y2: float, w2: float, h2: float) \
            -> bool:
        """
        Checks if two rectangles are colliding. The given x, y coordinates are based on the shape_mode!
        :param x: x coordinate of the first rectangle.
        :param y: y coordinate of the first rectangle.
        :param w: width of the first rectangle.
        :param h: height of the first rectangle.
        :param x2: x coordinate of the second rectangle.
        :param y2: y coordinate of the second rectangle.
        :param w2: diameter of the second rectangle.
        :param h2: height of the second rectangle.
        :return: True if colliding, False if not.
        """
        pos1 = self._get_coordinates(x, y, w, h)
        pos2 = self._get_coordinates(x2, y2, w2, h2)
        r1 = pygame.Rect(pos1.x, pos1.y, w, h)
        r2 = pygame.Rect(pos2.x, pos2.y, w2, h2)
        return r1.colliderect(r2)

    def colliding_pointinrect(self, point_x: float, point_y: float,
                              rect_x: float, rect_y: float, rect_w: float, rect_h: float) -> bool:
        """
        Checks if a certain point is inside a rectangle. The given x, y coordinates are based on the shape_mode!
        :param point_x: x coordinate of the point.
        :param point_y: y coordinate of the point.
        :param rect_x: x coordinate of the rectangle.
        :param rect_y: y coordinate of the rectangle.
        :param rect_w: diameter of the rectangle.
        :param rect_h: height of the rectangle.
        :return: True if point is in rectangle, False if not.
        """
        rect_pos = self._get_coordinates(rect_x, rect_y, rect_w, rect_h)
        rect = pygame.Rect(rect_pos.x, rect_pos.y, rect_w, rect_h)
        return rect.collidepoint(point_x, point_y)

    # endregion collision detection

    def load_image(self, path: str) -> Union[ProgfaImage, None]:
        """
        Loads a local image (located in the Resources folder of your project) or an online image and returns it as
        a ProgfaImage object. Be sure to load images in setup()!


        :param path: url or local path in Resources, including filename + extension
        :return: the loaded image object, or None if loading failed.

        :examples:
        # Loading local image:\n
        >>> img1 = engine.load_image("programmer_cat.png")   # auto searches in Resources folder in your project
        >>> img2 = engine.load_image("Resources/programmer_cat.png")  # loads from same Resources folder in your project
        # Loading online image:\n
        >>> img = engine.load_image("https://i.pinimg.com/564x/63/92/59/6392596fe9232338735189fdd6d43bd7.jpg")
        """
        # ANSI escape code for red text
        red_code = '\033[91m'
        # ANSI escape code to reset text color/formatting
        reset_code = '\033[0m'

        valid_url = False
        image = None

        parsed_url = urlparse(path)
        if parsed_url.scheme and parsed_url.netloc:
            valid_url = True
            try:
                response = urllib.request.urlopen(path)
                image_data = BytesIO(response.read())
                image = pygame.image.load(image_data)  # return online image
            except Exception as e:
                print(f"{red_code}[ERROR] loading online image ({str(e)}) {reset_code}")

        # local image?
        if path.startswith("Resources/"):
            full_path = path
        else:
            full_path = "Resources/" + path

        # Check if the value is a valid local file path
        if os.path.exists(full_path):
            valid_url = True
            image = pygame.image.load(full_path)

        if not valid_url:
            print(red_code + f"[ERROR] Wrong image path: [{path}] -- your image will not be displayed" + reset_code)
            return None
        elif image is None:
            print(red_code + f"[ERROR] loading image: [{path}] -- your image will not be displayed" + reset_code)
            return None

        return ProgfaImage(self, image)

    # region Game-loop

    async def play(self):
        """Starts game loop and listening to events."""
        clock = pygame.time.Clock()
        done = False

        await self._setup()

        while not done:
            # ui input
            # self.delta_time = clock.tick_busy_loop(self.fps) / 1000.0
            delta_time = clock.tick(self._fps) / 1000.0

            pygame.mouse.set_cursor(*pygame.cursors.arrow)  # avoid cursor changing on text, ..

            special_keys = {
                pygame.K_UP: "UP",
                pygame.K_DOWN: "DOWN",
                pygame.K_LEFT: "LEFT",
                pygame.K_RIGHT: "RIGHT",
                pygame.K_RETURN: "ENTER",
                pygame.K_KP_ENTER: "ENTER",
                pygame.K_BACKSPACE: "BACKSPACE",
                pygame.K_DELETE: "DELETE",
                pygame.K_ESCAPE: "ESCAPE",
                pygame.K_LSHIFT: "LSHIFT",
                pygame.K_RSHIFT: "RSHIFT"
            }

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                else:
                    # self.ui_manager.process_events(event)
                    # ui input
                    if event.type == pygame.USEREVENT:
                        # Handle text input events
                        # print("user event")
                        # Handle text input events
                        if self._text_input.is_focused:
                            self._text_input.process_event(event)
                    elif event.type == pygame.MOUSEMOTION:
                        self._mouse_x, self._mouse_y = event.pos
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self._mouse_pressed = True
                        if event.button < len(MouseButton):
                            self._mouse_button = MouseButton(event.button)
                        else:
                            self._mouse_button = MouseButton.NONE

                    elif event.type == pygame.MOUSEBUTTONUP:
                        self._mouse_pressed = False
                        if event.button < len(MouseButton):
                            self._mouse_button = MouseButton(event.button)
                        else:
                            self._mouse_button = MouseButton.NONE
                        mouse_x, mouse_y = pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
                        await self._mouse_pressed_event(mouse_x, mouse_y, self._mouse_button)
                        self._mouse_button = MouseButton.NONE
                    elif event.type == pygame.KEYDOWN:
                        actual_key = None
                        if event.key in special_keys.keys() or not event.unicode:
                            actual_key = special_keys.get(event.key, "UNKNOWN_KEY")
                        else:
                            actual_key = event.unicode

                        self._key_pressed = True
                        self._key = actual_key
                        await self._key_down_event(actual_key)
                    elif event.type == pygame.KEYUP:
                        if event.key in special_keys.keys() or not event.unicode:
                            actual_key = special_keys.get(event.key, "UNKNOWN_KEY")
                        else:
                            actual_key = event.unicode

                        await self._key_up_event(actual_key)
                        self._key_pressed = False
                        self._key = None

            await self._evaluate()
            # self.ui_manager.update(delta_time)
            await self._render()

            # Draw the UI elements
            # self.ui_manager.draw_ui(self)

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()

    async def _setup(self):
        """Executed only once at the start of the program, after initializing global variables."""
        pass

    async def _evaluate(self):
        """Executed in a loop, fps times per second."""
        pass

    async def _render(self):
        """Executed in a loop, fps times per second."""
        pass

    async def _mouse_pressed_event(self, mouse_x: int, mouse_y: int, mouse_button: MouseButton):
        """Executed ONLY when user presses a mouse button."""
        pass

    async def _key_down_event(self, key: str):
        """Executed ONLY when user presses a key down.\n
        *This function is executed automatically; never call it!*"""
        pass

    async def _key_up_event(self, key: str):
        """Executed ONLY when user releases a key (so first down, then release).\n
        *This function is executed automatically; never call it!*"""
        pass

    # endregion Game-loop
