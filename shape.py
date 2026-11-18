from __future__ import annotations

from abc import ABC, abstractmethod
from math import fabs, isfinite
from typing import Optional, Tuple

Point = Tuple[float, float]


class Shape(ABC):

    EPSILON: float = 1e-9

    # ---------------------------------------------------------------------
    # Abstract API expected from all Shape implementations
    # ---------------------------------------------------------------------
    @abstractmethod
    def get_min_surrounding_point(self) -> Point:
        """Return (min_x, min_y) across the shape."""
        raise NotImplementedError

    @abstractmethod
    def get_max_surrounding_point(self) -> Point:
        """Return (max_x, max_y) across the shape."""
        raise NotImplementedError

    @abstractmethod
    def get_center(self) -> Point:
        """Return the centroid of the shape."""
        raise NotImplementedError

    @abstractmethod
    def find_intersection(self, origin: Point, direction: "Vector2D") -> Optional[Point]:
        """Return first intersection between the ray (origin, direction) and the shape, or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def contains_point(self, point: Point) -> bool:
        """Return ``True`` if ``point`` is inside the shape."""
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Static helper utilities
    # ------------------------------------------------------------------
    @staticmethod
    def line_line_intersection(x1: float, y1: float, x2: float, y2: float,
                               x3: float, y3: float, x4: float, y4: float) -> Optional[Point]:
        """Calculate intersection point of two lines if they intersect, else ``None``."""
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None  # Parallel or coincidental
        x_point = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
        y_point = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
        return (x_point, y_point)

    @staticmethod
    def is_close(a: float, b: float) -> bool:
        if not isfinite(a) or not isfinite(b):
            return False
        return fabs(a - b) <= Shape.EPSILON

    @staticmethod
    def is_close_or_greater(a: float, b: float) -> bool:
        if not isfinite(a) or not isfinite(b):
            return False
        if a > b:
            return True
        return fabs(a - b) <= Shape.EPSILON 