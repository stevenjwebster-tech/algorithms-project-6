from __future__ import annotations

from typing import List, Set, Tuple, Optional
import random

from bvh import BVH, SplitMethod
from rectangle import Rectangle
from shape import Shape
from vector2d import Vector2D

Point = Tuple[float, float]


class BoundedVolumeHierarchy(BVH):

    root = None

    def __init__(self):
        self._split_method: SplitMethod = SplitMethod.SPLIT_MEDIAN

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def set_split_method(self, split_method: SplitMethod) -> None:
        self._split_method = split_method

    # ------------------------------------------------------------------
    # Construction & mutation
    # ------------------------------------------------------------------
    def build_bvh(self, shape_list: List[Shape]) -> None:
        self.root = None
        if len(shape_list) == 0: return

        pile = [(list(shape_list), 0, None, "")]
        inters = []

        while len(pile) > 0:
            shapes, dep, dad, side = pile.pop()

            if len(shapes) == 1:
                box = Rectangle(shapes[0].get_min_surrounding_point(), shapes[0].get_max_surrounding_point())
                node = Node(shapes[0], None, None, box, 0)
            else:
                xy = dep % 2
                ranks = []
                for i in range(len(shapes)): ranks.append((shapes[i].get_center()[xy], i, shapes[i]))
                ranks.sort()
                sorted = []
                for rk in ranks: sorted.append(rk[2])

                mid = len(sorted) // 2

                node = Node(None, None, None, None, 0)
                inters.append(node)
                pile.append((sorted[mid:], dep + 1, node, "right"))
                pile.append((sorted[:mid], dep + 1, node, "left"))

            if dad is None: self.root = node
            elif side == "left": dad.l = node
            else: dad.r = node

        for j in reversed(inters):
            lmin = j.l.box.min_pos
            lmax = j.l.box.max_pos
            rmin = j.r.box.min_pos
            rmax = j.r.box.max_pos
            j.box = Rectangle((min(lmin[0], rmin[0]), min(lmin[1], rmin[1])), (max(lmax[0], rmax[0]), max(lmax[1], rmax[1])))
            j.h = 1 + max(j.l.h, j.r.h)

    def insert(self, shape: Shape) -> None:
        nmin = shape.get_min_surrounding_point()
        nmax = shape.get_max_surrounding_point()
        nleaf = Node(shape, None, None, Rectangle(nmin, nmax), 0)

        if self.root is None:
            self.root = nleaf
            return

        path = []
        node = self.root
        while node.tri is None:
            path.append(node)
            l = node.l
            r = node.r

            lleaf = l.tri is not None
            rleaf = r.tri is not None
            if lleaf != rleaf: goleft = lleaf
            else:
                lmin = l.box.min_pos
                lmax = l.box.max_pos
                bigmin = (min(lmin[0], nmin[0]), min(lmin[1], nmin[1]))
                bigmax = (max(lmax[0], nmax[0]), max(lmax[1], nmax[1]))
                lgrow = 2 * ((bigmax[0] - bigmin[0]) + (bigmax[1] - bigmin[1])) - 2 * ((lmax[0] - lmin[0]) + (lmax[1] - lmin[1]))

                rmin = r.box.min_pos
                rmax = r.box.max_pos
                bigmin = (min(rmin[0], nmin[0]), min(rmin[1], nmin[1]))
                bigmax = (max(rmax[0], nmax[0]), max(rmax[1], nmax[1]))
                rgrow = 2 * ((bigmax[0] - bigmin[0]) + (bigmax[1] - bigmin[1])) - 2 * ((rmax[0] - rmin[0]) + (rmax[1] - rmin[1]))

                if not Shape.is_close(lgrow, rgrow): goleft = lgrow < rgrow
                elif l.h != r.h: goleft = l.h < r.h
                else: goleft = random.random() < 0.5

            if goleft: node = l
            else: node = r

        omin = node.box.min_pos
        omax = node.box.max_pos
        pbox = Rectangle((min(omin[0], nmin[0]), min(omin[1], nmin[1])), (max(omax[0], nmax[0]), max(omax[1], nmax[1])))
        duo = Node(None, node, nleaf, pbox, 1)
        if len(path) == 0: self.root = duo
        elif path[-1].l is node: path[-1].l = duo
        else: path[-1].r = duo

        while len(path) > 0:
            node = path.pop()
            l = node.l
            r = node.r

            redo = [node]

            if l.h - r.h > 1:
                if l.l.h >= l.r.h:
                    node.l = l.r
                    l.r = node
                    redo = [node, l]
                else:
                    lr = l.r
                    l.r = lr.l
                    node.l = lr.r
                    lr.l = l
                    lr.r = node
                    redo = [l, node, lr]
            elif r.h - l.h > 1:
                if r.r.h >= r.l.h:
                    node.r = r.l
                    r.l = node
                    redo = [node, r]
                else:
                    rl = r.l
                    r.l = rl.r
                    node.r = rl.l
                    rl.r = r
                    rl.l = node
                    redo = [r, node, rl]

            for j in redo:
                lmin = j.l.box.min_pos
                lmax = j.l.box.max_pos
                rmin = j.r.box.min_pos
                rmax = j.r.box.max_pos
                j.box = Rectangle((min(lmin[0], rmin[0]), min(lmin[1], rmin[1])), (max(lmax[0], rmax[0]), max(lmax[1], rmax[1])))
                j.h = 1 + max(j.l.h, j.r.h)

            newtop = redo[-1]
            if len(path) == 0: self.root = newtop
            elif path[-1].l is node: path[-1].l = newtop
            else: path[-1].r = newtop

    def remove(self, shape: Shape) -> None:
        if self.root is None: return

        cen = shape.get_center()
        gone = None
        path = []
        pile = [(self.root, [])]
        while len(pile) > 0:
            node, anc = pile.pop()
            if node.tri is None:
                if not node.box.contains_point(cen): continue
                pile.append((node.r, anc + [node]))
                pile.append((node.l, anc + [node]))
            elif node.tri == shape:
                gone = node
                path = anc
                break

        if gone is None: return

        if len(path) == 0:
            self.root = None
            return

        dad = path.pop()
        if dad.l is gone: sib = dad.r
        else: sib = dad.l
        if len(path) == 0: self.root = sib
        elif path[-1].l is dad: path[-1].l = sib
        else: path[-1].r = sib

        while len(path) > 0:
            node = path.pop()
            l = node.l
            r = node.r

            redo = [node]

            if l.h - r.h > 1:
                if l.l.h >= l.r.h:
                    node.l = l.r
                    l.r = node
                    redo = [node, l]
                else:
                    lr = l.r
                    l.r = lr.l
                    node.l = lr.r
                    lr.l = l
                    lr.r = node
                    redo = [l, node, lr]
            elif r.h - l.h > 1:
                if r.r.h >= r.l.h:
                    node.r = r.l
                    r.l = node
                    redo = [node, r]
                else:
                    rl = r.l
                    r.l = rl.r
                    node.r = rl.l
                    rl.r = r
                    rl.l = node
                    redo = [r, node, rl]

            for j in redo:
                lmin = j.l.box.min_pos
                lmax = j.l.box.max_pos
                rmin = j.r.box.min_pos
                rmax = j.r.box.max_pos
                j.box = Rectangle((min(lmin[0], rmin[0]), min(lmin[1], rmin[1])), (max(lmax[0], rmax[0]), max(lmax[1], rmax[1])))
                j.h = 1 + max(j.l.h, j.r.h)

            newtop = redo[-1]
            if len(path) == 0: self.root = newtop
            elif path[-1].l is node: path[-1].l = newtop
            else: path[-1].r = newtop

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def find_collision(self, point: Point) -> Set[Shape]:
        hits = set()
        if self.root is None: return hits

        pile = [self.root]
        while len(pile) > 0:
            node = pile.pop()

            if not node.box.contains_point(point): continue

            if node.tri is None:
                pile.append(node.l)
                pile.append(node.r)
            elif node.tri.contains_point(point):
                hits.add(node.tri)
        return hits

    def intersect_ray(self, origin: Point, direction: Vector2D) -> Optional[Shape]:
        if self.root is None: return None

        near = None
        neardist = float("inf")

        pile = [self.root]
        while len(pile) > 0:
            node = pile.pop()
            if node.tri is None:
                if node.box.does_ray_intersect(origin, direction):
                    pile.append(node.l)
                    pile.append(node.r)
            else:
                pt = node.tri.find_intersection(origin, direction)
                if pt is not None:
                    dist = BVH.distance_between_points(origin, pt)
                    if dist < neardist:
                        near = node.tri
                        neardist = dist
        return near

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def __str__(self) -> str:  # noqa: Dunder missing
        out = ""
        if self.root is None: return out

        pile = [(self.root, 0)]
        while len(pile) > 0:
            node, dep = pile.pop()
            ind = "\t" * dep
            if node.tri is None:
                l = node.box.min_pos
                h = node.box.max_pos
                out += f"{ind}[({l[0]}, {l[1]}), ({h[0]}, {h[1]})]\n"
                pile.append((node.r, dep + 1))
                pile.append((node.l, dep + 1))
            else:
                a = node.tri.a
                b = node.tri.b
                c = node.tri.c
                out += f"{ind}({a[0]}, {a[1]}) ({b[0]}, {b[1]}) ({c[0]}, {c[1]})\n"
        return out


class Node:

    def __init__(self, tri, l, r, box, h):
        self.tri = tri
        self.l = l
        self.r = r
        self.box = box
        self.h = h
