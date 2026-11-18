import cv2
import numpy as np
import math
from typing import List, Tuple

from bounded_volume_hierarchy import BoundedVolumeHierarchy
from bvh import SplitMethod
from vector2d import Vector2D
from triangle import Triangle

Point = Tuple[float, float]


class Visualization:
    """
    Handles the raycasting visualization logic.
    The 'eye' is positioned at (offset_x, offset_y) in world coordinates.
    """
    
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.bvh = None
        
        self.dx = [-10, 10, -10, 10]
        self.dy = [-10, -10, 10, 10]
    
    def set_bounding_volume_hierarchy(self, bvh):
        """Set the BVH for collision detection and raycasting."""
        self.bvh = bvh
    
    def _check_center(self, x: float, y: float) -> bool:
        """
        Check if position (x, y) collides with any shapes in the BVH.
        
        Args:
            x, y: World coordinates to check
            
        Returns:
            True if no collision, False if collision detected
        """
        if self.bvh is None:
            return True
        
        shapes = self.bvh.find_collision((x + 0.5, y + 0.5))
        
        return shapes is None or len(shapes) == 0
    
    def move_square(self, key_pressed: str) -> bool:
        """
        Attempt to move the eye/square based on WASD input.
        
        Args:
            key_pressed: Character key ('w', 'a', 's', 'd')
            
        Returns:
            True if movement occurred (requires redraw), False otherwise
        """
        key_pressed = key_pressed.lower()
        
        delta_x = 0
        delta_y = 0
        
        if key_pressed == 'w':
            delta_y -= 1
        elif key_pressed == 'a':
            delta_x -= 1
        elif key_pressed == 's':
            delta_y += 1
        elif key_pressed == 'd':
            delta_x += 1
        else:
            return False
        
        can_move = True
        for i in range(4):
            corner_x = self.offset_x + delta_x + self.dx[i]
            corner_y = self.offset_y + delta_y + self.dy[i]
            
            if not self._check_center(corner_x, corner_y):
                can_move = False
                break
        
        if can_move:
            self.offset_x += delta_x
            self.offset_y += delta_y
            return True
        
        return False
    
    def draw_gui(self) -> List[Point]:
        """
        Perform raycasting from the current eye position.
        Casts rays in a circle and returns intersection points.
        
        Returns:
            List of (x, y) tuples in screen coordinates (relative to center)
        """
        if self.bvh is None:
            return []
        
        origin: Point = (self.offset_x, self.offset_y)
        points = []
        num_rays = 1000
        
        for i in range(num_rays):
            angle_rad = math.radians(360.0 * i / num_rays)
            direction = Vector2D(math.cos(angle_rad), math.sin(angle_rad))
            
            shape = self.bvh.intersect_ray(origin, direction)
            
            if shape is None:
                continue
            
            intersection = shape.find_intersection(origin, direction)
            
            if intersection is None:
                continue
            
            screen_x = int(intersection[0]) + 200 - self.offset_x
            screen_y = int(intersection[1]) + 200 - self.offset_y
            
            points.append((screen_x, screen_y))
        
        return points


class BVHVisualizationWindow:
    
    def __init__(self, visualization: Visualization):
        self.visualization = visualization
        self.width = 400
        self.height = 400
        self.window_name = "BVH Visualization"
        
    def render(self) -> np.ndarray:
        img = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        
        points = self.visualization.draw_gui()
        
        for point in points:
            x, y = point
            if 0 <= x < self.width and 0 <= y < self.height:
                cv2.circle(img, (x, y), 1, (0, 0, 0), -1)
        
        cv2.rectangle(img, (190, 190), (210, 210), (255, 0, 0), -1)
        
        return img
    
    def run(self):
        """
        Main event loop for the visualization window.
        """
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, self.width, self.height)
        
        img = self.render()
        cv2.imshow(self.window_name, img)
        
        print("Controls: W/A/S/D to move, ESC or Q to quit")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27 or key == ord('q'):
                break
            elif key in [ord('w'), ord('a'), ord('s'), ord('d'),
                        ord('W'), ord('A'), ord('S'), ord('D')]:
                if self.visualization.move_square(chr(key)):
                    img = self.render()
                    cv2.imshow(self.window_name, img)
        
        cv2.destroyAllWindows()


def main():
    visualization = Visualization()
    
    shapes = []
    t1 = Triangle((0, -100), (-100, 0), (-50, 80))
    t2 = Triangle((-50, 90), (20, 100), (0, 40))
    t3 = Triangle((-100, 100), (-100, 50), (0, 100))
    shapes.extend([t1, t2, t3])
    
    bvh = BoundedVolumeHierarchy()
    bvh.set_split_method(SplitMethod.SPLIT_MEDIAN)
    bvh.build_bvh(shapes)
    visualization.set_bounding_volume_hierarchy(bvh)
    
    window = BVHVisualizationWindow(visualization)
    window.run()


if __name__ == "__main__":
    main()
