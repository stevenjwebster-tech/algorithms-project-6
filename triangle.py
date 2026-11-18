from __future__ import annotations

from typing import Optional, Tuple

from shape import Shape
from vector2d import Vector2D

Point = Tuple[float, float]


class Triangle(Shape):

    def __init__(self, a: Point, b: Point, c: Point):
        self.a: Point = a
        self.b: Point = b
        self.c: Point = c

    # ------------------------------------------------------------------
    # Shape interface – to be implemented
    # ------------------------------------------------------------------
    def get_min_surrounding_point(self) -> Point:
        return (min(self.a[0], self.b[0], self.c[0]), min(self.a[1], self.b[1], self.c[1]))

    def get_max_surrounding_point(self) -> Point:
        return (max(self.a[0], self.b[0], self.c[0]), max(self.a[1], self.b[1], self.c[1]))

    def get_center(self) -> Point:
        return ((self.a[0] + self.b[0] + self.c[0]) / 3, (self.a[1] + self.b[1] + self.c[1]) / 3)

    def find_intersection(self, origin: Point, direction: Vector2D) -> Optional[Point]:
        ox, oy = origin
        dx = direction.get_x()
        dy = direction.get_y()
        corns = [self.a, self.b, self.c]

        near = None
        neardist = 0
        for i in range(3):
            e1 = corns[i]
            e2 = corns[(i + 1) % 3]

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

        l = self.get_min_surrounding_point()
        h = self.get_max_surrounding_point()
        if x < l[0] - Shape.EPSILON or x > h[0] + Shape.EPSILON: return False
        if y < l[1] - Shape.EPSILON or y > h[1] + Shape.EPSILON: return False

        sab = (self.b[0] - self.a[0]) * (y - self.a[1]) - (self.b[1] - self.a[1]) * (x - self.a[0])
        sbc = (self.c[0] - self.b[0]) * (y - self.b[1]) - (self.c[1] - self.b[1]) * (x - self.b[0])
        sca = (self.a[0] - self.c[0]) * (y - self.c[1]) - (self.a[1] - self.c[1]) * (x - self.c[0])

        n = sab < -Shape.EPSILON or sbc < -Shape.EPSILON or sca < -Shape.EPSILON
        p = sab > Shape.EPSILON or sbc > Shape.EPSILON or sca > Shape.EPSILON
        return not (n and p)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return f"Triangle({self.a}, {self.b}, {self.c})"

    def __eq__(self, other):
        if not isinstance(other, Triangle):
            return False
        return self.a == other.a and self.b == other.b and self.c == other.c

    def __hash__(self):
        return hash((self.a, self.b, self.c)) 