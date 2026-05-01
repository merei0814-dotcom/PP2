import pygame
from collections import deque
import math


def flood_fill(surface, start_pos, new_color):
    """
    Fill one closed area.
    It uses get_at and set_at, as the task requires.
    """
    width = surface.get_width()
    height = surface.get_height()

    x, y = start_pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return

    old_color = surface.get_at((x, y))

    if old_color == new_color:
        return

    queue = deque()
    queue.append((x, y))

    while queue:
        x, y = queue.popleft()

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        if surface.get_at((x, y)) != old_color:
            continue

        surface.set_at((x, y), new_color)

        queue.append((x + 1, y))
        queue.append((x - 1, y))
        queue.append((x, y + 1))
        queue.append((x, y - 1))


def draw_right_triangle(surface, start_pos, end_pos, color, width):
    """Draw right triangle."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    points = [
        (x1, y1),
        (x1, y2),
        (x2, y2)
    ]

    pygame.draw.polygon(surface, color, points, width)


def draw_equilateral_triangle(surface, start_pos, end_pos, color, width):
    """Draw simple equilateral-like triangle."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    left = min(x1, x2)
    right = max(x1, x2)
    bottom = max(y1, y2)

    side = right - left
    height = int(side * math.sqrt(3) / 2)

    top_x = (left + right) // 2
    top_y = bottom - height

    points = [
        (top_x, top_y),
        (left, bottom),
        (right, bottom)
    ]

    pygame.draw.polygon(surface, color, points, width)


def draw_rhombus(surface, start_pos, end_pos, color, width):
    """Draw rhombus."""
    x1, y1 = start_pos
    x2, y2 = end_pos

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    points = [
        (center_x, y1),
        (x2, center_y),
        (center_x, y2),
        (x1, center_y)
    ]

    pygame.draw.polygon(surface, color, points, width)
