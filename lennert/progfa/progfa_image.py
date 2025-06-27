from typing import Union

import pygame


class ProgfaImage:
    def __init__(self, engine, surface):
        self._engine = engine
        self._surface = surface
        self._width = self._surface.get_width()
        self._height = self._surface.get_height()

    @property
    def width(self) -> int:
        """
        Get the width of the image.
        """
        return self._surface.get_width()

    @property
    def height(self) -> int:
        """
        Get the height of the image.
        """
        return self._surface.get_height()

    def resize(self, width: Union[int, float], height: Union[int, float], keep_ratio: bool = True) -> None:
        """
        Resizes the image to the requested width and height.
        If keep_ratio is set to True (default), it will try to resize proportionally
        (therefore either actual width or height may be different).
        For exact dimensions of the given width and height, choose keep_ratio=False
        :param width: The desired width for the image.
        :param height: The desired height for the image.
        :param keep_ratio: Choose True to resize proportionally, False to resize with exact dimensions.
        :return: Nothing
        Example:
        >>> img.resize(100, 200)  # resize, keep original proportions
        >>> img.resize(100, 200, False)  # resize, ignore proportions
        """
        actual_height = height
        actual_width = width
        if keep_ratio:
            aspect_ratio = self._surface.get_width() / self._surface.get_height()
            actual_height = int(width / aspect_ratio)
            actual_width = int(height * aspect_ratio)
            if actual_width > width:
                actual_width = width
            else:
                actual_height = height
        self._width = actual_width
        self._height = actual_height
        self._surface = pygame.transform.scale(self._surface, [actual_width, actual_height])

    def draw(self, x: Union[int, float], y: Union[int, float]) -> None:
        """
        Draws the image in the specified position (either from corner or center, based on the current ShapeMode set).
        :param x: x position to draw the image in
        :param y: y position to draw the image in
        :return: Nothing
        Example:
        >>> img.draw(100, 200)  # draw image img in position 100, 200
        """
        actual_pos = self._engine._get_coordinates(x, y, self._surface.get_width(), self._surface.get_height())
        self._engine._screen.blit(self._surface, (actual_pos.x, actual_pos.y))

    def draw_full_size(self, x: Union[int, float], y: Union[int, float]) -> None:
        """
        Draws the image full size in the specified position
        (either from corner or center, based on the current ShapeMode set).
        :param x: x position to draw the image in
        :param y: y position to draw the image in
        :return: Nothing
        Example:
        >>> img.draw_full_size(100, 200)  # draw image img full size in position 100, 200
        """
        actual_pos = self._engine._get_coordinates(x, y, self._surface.get_width(), self._surface.get_height())
        self._surface = pygame.transform.scale(self._surface, [self._surface.get_width(), self._surface.get_height()])
        self._engine._screen.blit(self._surface, (actual_pos.x, actual_pos.y))

    def draw_fixed_size(self, x: Union[int, float], y: Union[int, float],
                        width: Union[int, float], height: Union[int, float], keep_ratio: bool = True) -> None:
        """
        Draws the image in the specified position, in the given weight and height to draw in.
        This does not resize the original image!
        :param x: x position to draw the image in
        :param y: y position to draw the image in
        :param width: the width to use to draw the image
        :param height: the height to use to draw the image
        :param keep_ratio: choose True to keep proportions while drawing in a different size, False to ignore them.
        :return: Nothing
        Example:
        >>> img.draw_fixed_size(10, 20, 100, 200)  # draw image img in position 10, 20, dimensions 100x200, proportional
        >>> img.draw_fixed_size(10, 20, 100, 200, False)  # draw image img in this position/size, ignore proportions
        """
        actual_pos = self._engine._get_coordinates(x, y, width, height)
        # self.surface = pygame.transform.scale(self.surface, (width, height))
        actual_height = height
        actual_width = width
        if keep_ratio:
            aspect_ratio = self._surface.get_width() / self._surface.get_height()
            actual_height = int(width / aspect_ratio)
            actual_width = int(height * aspect_ratio)
            if actual_width > width:
                actual_width = width
            else:
                actual_height = height
        # Create a new surface of the desired size
        new_surface = pygame.Surface([actual_width, actual_height], pygame.SRCALPHA)

        # Draw the original surface onto the new surface, stretching it to the new size
        new_surface.blit(pygame.transform.smoothscale(self._surface, [actual_width, actual_height]), [0, 0])

        # Draw the new surface onto the screen
        self._engine._screen.blit(new_surface, (actual_pos.x, actual_pos.y))

    def draw_partial(self, pos_x: Union[int, float], pos_y: Union[int, float],
                     source_rect: Union[tuple[int, int, int, int], tuple[float, float, float, float]]) -> None:
        """
        Used to draw only a part of an image.
        :param pos_x: the target x position to draw in
        :param pos_y: the target y position to draw in
        :param source_rect: the source rectangle to cut,
        starting from the top left (0, 0) in the image (cut_x, cut_y, cut_width, cut_height).
        :return: Nothing
        Example:
        >>> img.draw_partial(10, 20, (40, 60, 200, 100))  # draw cut part in position 10, 20
        """
        actual_pos = self._engine._get_coordinates(pos_x, pos_y, self._surface.get_width(), self._surface.get_height())
        # self.engine._screen.blit(self.surface,  (x, y), area=rect)
        src = pygame.Rect(source_rect[0], source_rect[1], source_rect[2], source_rect[3])
        self._engine._screen.blit(self._surface, (actual_pos.x, actual_pos.y), area=src)

    def draw_sprite_frame(self, x: Union[int, float], y: Union[int, float], num_frames: int, num_columns: int,
                          current_frame: int) -> None:
        """
        Draws a single frame from a spritesheet
        :param x: the x position to draw the frame in (from corner or center, based on ShapeMode)
        :param y: the y position to draw the frame in (from corner or center, based on ShapeMode)
        :param num_frames: the number of frames in the spritesheet
        :param num_columns: the number of columns in the spritesheet
        :param current_frame: the frame number to show (counting from left to right, top to bottom)
        :return: Nothing
        """
        num_rows = num_frames // num_columns
        curr_col = current_frame % num_columns
        curr_row = current_frame // num_columns
        frame_width = self.width / num_columns
        frame_height = self.height / num_rows

        actual_pos = self._engine._get_coordinates(x, y, self._surface.get_width(), self._surface.get_height())
        self.draw_partial(actual_pos.x, actual_pos.y,
                          (curr_col * frame_width, curr_row * frame_height, frame_width, frame_height))

    def get_width(self) -> int:
        """
        Asks for the current width of the image.
        :return: the width of this image.
        """
        return self._surface.get_width()

    def get_height(self) -> int:
        """
        Asks for the current height of the image.
        :return: the height of this image.
        """
        return self._surface.get_height()
