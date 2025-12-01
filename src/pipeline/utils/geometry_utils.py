"""Minimal geometry utility helpers used across pipeline modules."""
from typing import Tuple
import math


def translate_point(pt: Tuple[float, float, float], offset: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (pt[0] + offset[0], pt[1] + offset[1], pt[2] + offset[2])


def rotate_point_xy(pt: Tuple[float, float, float], angle_rad: float) -> Tuple[float, float, float]:
    x, y, z = pt
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return (x * c - y * s, x * s + y * c, z)


def distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)
