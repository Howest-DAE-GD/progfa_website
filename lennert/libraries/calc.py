"""
Created on 22/01/2025

 this document contains all 'advanced' calculations for a dot product for rotating the player

@author: Lennert
"""
# imports
import math
import random
import time

from pygame.transform import scale


# GEOGRAPHIC math functions
def unit_circle(origin: (0, 0), radius: float or tuple = 1, angle: float = (time.time_ns() * 1000) * (math.pi * 2), angle_type: str = "deg") -> tuple:
    """
    a point on the circle

    :param origin: the origin point of the circle

    :param radius: the radius of the circle

    :param angle: the angle of the point on the circle

    :param angle_type: the type of the angle
    options: 'rad' or 'deg'

    :return: a coordinate of the point on the circle based on the given angle
    """
    # CONTROL
    if angle_type == "deg":
        angle = math.radians(angle)

    # CALCULATIONS
    value_X = math.cos(angle)
    value_Y = math.sin(angle)

    # multiply radius
    if    type(radius) == tuple and len(radius) == 2:
        value_X *= radius[0]
        value_Y *= radius[1]
    elif  type(radius) == float or type(radius) == int:
        value_X *= radius
        value_Y *= radius
    else: print("error, value error, radius has to be float or tuple with, 2 floats in it")

    # add origin
    value_X += origin[0]
    value_Y += origin[1]

    return value_X, value_Y
# def point_on_circle(origin: tuple = (0, 0), values: tuple = (random.uniform(0, 360), random.uniform(0, 360)), angle_type: str = "deg", scaler: float or tuple = 1) -> tuple:
#     """
#     calculates a point in the circle
#
#     :param origin: the coordinates of the center point of the circle
#
#     :param values: the location of your point on the circle
#
#     :param angle_type: the type of your angle,
#     options: deg, rad
#     standard == deg
#     recommended == rad
#
#     :param scaler: the scaler of your circle
#
#     :return: the coordinate of a point on a circle
#     """
#     # unpacking values
#     origin_X, origin_Y = origin
#     value_X, value_Y = values
#
#     # converts deg to rad
#     if angle_type.strip().lower() == "deg":
#         value_X = math.radians(value_X)
#         value_Y = math.radians(value_Y)
#
#     # calculate point on unit circle on point 0
#     unit_X = math.cos(value_X)
#     unit_Y = math.sin(value_Y)
#
#     time.sleep(1)
#     print("length:", value_X, "| cos", unit_X)
#     print("height:", value_Y, "| sin", unit_Y)
#
#     # add the radius to point
#     if type(scaler) == tuple:
#         scale_X, scale_Y = scaler
#
#         unit_X *= scale_X
#         unit_Y *= scale_Y
#
#     elif type(scaler) == float:
#         unit_X *= scaler
#         unit_Y *= scaler
#
#     # translate all to center point or origin
#     unit_X += origin_X
#     unit_Y += origin_Y
#
#     return unit_X, unit_Y

def flip_vector(direction: tuple):
    """
    calculates the flipped vector
    reverses both values

    # function not completely ready
    # TODO:
    #  add origin: tuple = (0, 0) parameter, change name vector to direction parameter
    #  direction can also acts as

    :param direction: vector to flip

    :return: the flipped vector
    """
    # unpacking
    direction_X, direction_Y = direction

    direction_X *= -1
    direction_Y *= -1

    return direction_X, direction_Y
def mirror_vector(direction: tuple, mirror_axes: str = "x"):
    """
    calculates the mirrored vector

    :param direction: the vectors direction to mirror
    :param mirror_axes: the axes where you will mirror over


    :return: the mirrored vector
    """
    # unpacking
    direction_X, direction_Y = direction

    if mirror_axes.strip().lower() == "x":
        direction_Y *= -1
    elif mirror_axes.strip().lower() == "y":
        direction_X *= -1

    return direction_X, direction_Y

# contains trigonometry and such
def vector(vector_origin: tuple or list, vector_direction: tuple or list = (None, None)) -> tuple:
    """
    calculates, the vector,

    :param vector_origin: the origin from where the vector stats.

    :param vector_direction: the direction where the vector faces towards

    :return: -
    """
    # convertor if needed
    if type(vector_origin) == list(): vector_origin = tuple(vector_origin)
    if type(vector_direction) == list(): vector_direction = tuple(vector_direction)

    # unpacking variables
    origin_X, origin_Y = vector_origin # unpack
    direction_X, direction_Y = vector_direction # unpack

    # calculation
    vector_X = direction_X - origin_X
    vector_Y = (direction_Y - origin_Y) * -1

    return vector_X, vector_Y

def vector_length(vector: tuple or list) -> float:
    """
    calculates, the vectors length

    :param vector: the vector with 1 direction coordinate, the origin is 0
    » not a line with 2 point coordinates
    :return: the length of a vector
    """
    # convertor if needed
    if type(vector) == list(): vector = tuple(vector)

    # calculation
    return math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))

def normalize_vector(vector: tuple or list, length: float) -> tuple:
    """
    calculates, the normalized version of a vector

    :param vector: the vector tuple with 1 direction coordinate, the origin is 0
    :param length: the vectors length
    :return: the length of a vector
    """
    # convertor if needed
    if type(vector) == list(): vector = tuple(vector)

    # calculation
    return vector[0] / length, vector[1] / length

def dot_product(vector_1: tuple, vector_2: tuple, length_1: float, length_2: float, return_angle: bool = True) -> float:
    """
    calculates, the dot product of a normalized vector

    :param vector_1: first vector direction
    :param vector_2: second vector direction

    :param length_1: first vector length
    :param length_2: second vector length

    :return: -
    """

    # cosine = vector_length * dot_product_vector_length
    dot_product = (vector_1[0] * vector_2[0]) + (vector_1[1] * vector_2[1])
    if return_angle:
        length_multiplication = length_1 * length_2
        cosine = dot_product / length_multiplication
        angle = math.acos(cosine)
        return angle
    else:
        return -1
        # dot_product