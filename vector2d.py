class Vector2D:
    """Simple 2-D vector class used by the starter code."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y

    def __repr__(self) -> str:
        return f"Vector2D({self.x}, {self.y})" 