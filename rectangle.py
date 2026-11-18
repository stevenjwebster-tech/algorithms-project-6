from __future__ import annotations

from typing import Tuple, Optional

from shape import Shape
from vector2d import Vector2D

Point = Tuple[float, float]


class Rectangle(Shape):
    """Axis-aligned bounding box used by the BVH. This starter version only contains
    the public API signatures"""

    def __init__(self, min_pos: Point, max_pos: Point):
        self.min_pos: Point = min_pos
        self.max_pos: Point = max_pos

    # ---------------------------------------------------------------
    # Shape interface – to be implemented
    # ---------------------------------------------------------------
    def get_min_surrounding_point(self) -> Point:  # noqa: D401
        return self.min_pos

    def get_max_surrounding_point(self) -> Point:  # noqa: D401
        return self.max_pos

    def get_center(self) -> Point:
        return ((self.min_pos[0] + self.max_pos[0]) / 2, (self.min_pos[1] + self.max_pos[1]) / 2)

    def find_intersection(self, origin: Point, direction: Vector2D) -> Optional[Point]:
        ox, oy = origin
        dx = direction.get_x()
        dy = direction.get_y()
        corns = [self.min_pos, (self.max_pos[0], self.min_pos[1]), self.max_pos, (self.min_pos[0], self.max_pos[1])]

        near = None
        neardist = 0
        for i in range(4):
            e1 = corns[i]
            e2 = corns[(i + 1) % 4]

            pt = Shape.line_line_intersection(ox, oy, ox + dx, oy + dy, e1[0], e1[1], e2[0], e2[1])
            if pt is None: continue
            x, y = pt

            if not Shape.is_close_or_greater(x, min(e1[0], e2[0])): continue
            if not Shape.is_close_or_greater(max(e1[0], e2[0]), x): continue
            if not Shape.is_close_or_greater(y, min(e1[1], e2[1])): continue
            if not Shape.is_close_or_greater(max(e1[1], e2[1]), y): continue

            if not Shape.is_close_or_greater((x - ox) * dx + (y - oy) * dy, 0): continue

            sq = (x - ox) ** 2 + (y - oy) ** 2
            if near is None or sq < neardist:
                near = pt
                neardist = sq
        return near

    def contains_point(self, point: Point) -> bool:
        x, y = point
        if x < self.min_pos[0] - Shape.EPSILON or x > self.max_pos[0] + Shape.EPSILON: return False
        if y < self.min_pos[1] - Shape.EPSILON or y > self.max_pos[1] + Shape.EPSILON: return False
        return True

    # ---------------------------------------------------------------
    # Additional helpers needed by BVH – to be implemented
    # ---------------------------------------------------------------
    def does_ray_intersect(self, origin: Point, direction: Vector2D) -> bool:
        o = [origin[0], origin[1]]
        d = [direction.get_x(), direction.get_y()]
        tmin = 0.0
        tmax = float("inf")
        for xy in range(2):
            l = self.min_pos[xy] - Shape.EPSILON
            h = self.max_pos[xy] + Shape.EPSILON
            if d[xy] == 0:
                if o[xy] < l or o[xy] > h: return False
            else:
                tn = (l - o[xy]) / d[xy]
                tf = (h - o[xy]) / d[xy]
                if tn > tf:
                    hold = tn
                    tn = tf
                    tf = hold
                if tn > tmin: tmin = tn
                if tf < tmax: tmax = tf
        return tmin <= tmax