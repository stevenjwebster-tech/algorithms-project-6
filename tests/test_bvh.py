import pytest
from triangle import Triangle
from vector2d import Vector2D
from bounded_volume_hierarchy import BoundedVolumeHierarchy


def test_empty_bvh():
    bvh = BoundedVolumeHierarchy()


def test_edge_cases():
    t = Triangle((3, 0), (5, 0), (5, 1))
    assert t.contains_point((3, 0))
    assert t.contains_point((4, 0))

    origin = (0, 0)
    direction = Vector2D(1, 0)
    assert t.find_intersection(origin, direction) == (3, 0)

    origin = (4, -1)
    direction = Vector2D(0, 1)
    assert t.find_intersection(origin, direction) == (4, 0)

    origin = (4, 0)
    direction = Vector2D(1, 0)
    assert t.find_intersection(origin, direction) == (5, 0)

    origin = (4, 0)
    direction = Vector2D(0, 1)
    assert t.find_intersection(origin, direction) == (4, 0)

    origin = (4.5, 0.5)
    direction = Vector2D(0, 1)
    assert t.find_intersection(origin, direction) == (4.5, 0.75)
