from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Set, Tuple, Optional

from vector2d import Vector2D

Point = Tuple[float, float]


class SplitMethod(Enum):
    SPLIT_MIDRANGE = auto()
    SPLIT_MEDIAN = auto()
    SPLIT_SURFACE_AREA = auto()


SPLIT_DEFAULT = SplitMethod.SPLIT_MIDRANGE


class BVH(ABC):

    # ------------------------------------------------------------------
    # Configuration API
    # ------------------------------------------------------------------
    @abstractmethod
    def set_split_method(self, split_method: SplitMethod) -> None:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Construction & mutation
    # ------------------------------------------------------------------
    @abstractmethod
    def build_bvh(self, shape_list: List["Shape"]) -> None:
        raise NotImplementedError

    @abstractmethod
    def insert(self, shape: "Shape") -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, shape: "Shape") -> None:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    @abstractmethod
    def find_collision(self, point: Point) -> Set["Shape"]:
        raise NotImplementedError

    @abstractmethod
    def intersect_ray(self, origin: Point, direction: Vector2D) -> Optional["Shape"]:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Diagnostic helpers
    # ------------------------------------------------------------------
    @abstractmethod
    def __str__(self) -> str:  # noqa: Dunder missing
        raise NotImplementedError

    # ------------------------------------------------------------------
    # Utility (static)
    # ------------------------------------------------------------------
    @staticmethod
    def distance_between_points(p1: Point, p2: Point) -> float:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return (dx * dx + dy * dy) ** 0.5 