
import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 900, 600
TOOLBAR_HEIGHT = 70
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Practice 11 - Paint")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (220, 40, 40)
GREEN = (40, 180, 80)
BLUE = (50, 100, 230)

font = pygame.font.SysFont("Verdana", 18)

# Drawing surface. We draw saved shapes here.
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# Current settings
current_color = BLACK
current_tool = "brush"
line_width = 4

# Mouse state
is_drawing = False
start_pos = None
last_pos = None


def canvas_pos(mouse_pos):
    """Convert screen mouse position to canvas position."""
    return mouse_pos[0], mouse_pos[1] - TOOLBAR_HEIGHT


def draw_toolbar():
    """Draw instruction toolbar."""
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))
    text = (
        "Tools: 1 Brush | 2 Square | 3 Right Triangle | "
        "4 Equilateral Triangle | 5 Rhombus | Colors: R/G/B/K | C Clear"
    )
    info = font.render(text, True, BLACK)
    screen.blit(info, (10, 10))

    tool_info = font.render(f"Current tool: {current_tool} | Width: {line_width}", True, BLACK)
    screen.blit(tool_info, (10, 38))

    pygame.draw.rect(screen, current_color, (WIDTH - 60, 20, 40, 30))
    pygame.draw.rect(screen, BLACK, (WIDTH - 60, 20, 40, 30), 2)


def draw_square(surface, start, end, color, width):
    """Draw square from start position to mouse position."""
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))

    # Keep direction of mouse drag.
    if x2 < x1:
        side = -side
    height = abs(side)
    if y2 < y1:
        height = -height

    rect = pygame.Rect(x1, y1, side, height)
    rect.normalize()
    pygame.draw.rect(surface, color, rect, width)


def draw_right_triangle(surface, start, end, color, width):
    """Draw right triangle inside rectangle made by start and end points."""
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y1), (x1, y2), (x2, y2)]
    pygame.draw.polygon(surface, color, points, width)


def draw_equilateral_triangle(surface, start, end, color, width):
    """Draw equilateral triangle. Side length depends on mouse drag."""
    x1, y1 = start
    x2, y2 = end
    side = int(math.hypot(x2 - x1, y2 - y1))
    if side < 5:
        return

    height = int(side * math.sqrt(3) / 2)

    # Triangle points: top, bottom-left, bottom-right.
    points = [
        (x1, y1),
        (x1 - side // 2, y1 + height),
        (x1 + side // 2, y1 + height),
    ]
    pygame.draw.polygon(surface, color, points, width)


def draw_rhombus(surface, start, end, color, width):
    """Draw rhombus using start and end as bounding rectangle corners."""
    x1, y1 = start
    x2, y2 = end
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    points = [
        (center_x, y1),   # top
        (x2, center_y),   # right
        (center_x, y2),   # bottom
        (x1, center_y),   # left
    ]
    pygame.draw.polygon(surface, color, points, width)


def draw_shape(surface, tool, start, end):
    """Draw selected shape."""
    if tool == "square":
        draw_square(surface, start, end, current_color, line_width)
    elif tool == "right_triangle":
        draw_right_triangle(surface, start, end, current_color, line_width)
    elif tool == "equilateral_triangle":
        draw_equilateral_triangle(surface, start, end, current_color, line_width)
    elif tool == "rhombus":
        draw_rhombus(surface, start, end, current_color, line_width)


def main():
    global current_color, current_tool, is_drawing, start_pos, last_pos

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Select tools.
                if event.key == pygame.K_1:
                    current_tool = "brush"
                elif event.key == pygame.K_2:
                    current_tool = "square"
                elif event.key == pygame.K_3:
                    current_tool = "right_triangle"
                elif event.key == pygame.K_4:
                    current_tool = "equilateral_triangle"
                elif event.key == pygame.K_5:
                    current_tool = "rhombus"

                # Select colors.
                elif event.key == pygame.K_r:
                    current_color = RED
                elif event.key == pygame.K_g:
                    current_color = GREEN
                elif event.key == pygame.K_b:
                    current_color = BLUE
                elif event.key == pygame.K_k:
                    current_color = BLACK

                # Clear canvas.
                elif event.key == pygame.K_c:
                    canvas.fill(WHITE)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and event.pos[1] > TOOLBAR_HEIGHT:
                    is_drawing = True
                    start_pos = canvas_pos(event.pos)
                    last_pos = start_pos

            if event.type == pygame.MOUSEMOTION:
                if is_drawing and event.pos[1] > TOOLBAR_HEIGHT:
                    current_pos = canvas_pos(event.pos)

                    # Brush draws immediately while mouse is moving.
                    if current_tool == "brush":
                        pygame.draw.line(canvas, current_color, last_pos, current_pos, line_width)
                        last_pos = current_pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_drawing:
                    end_pos = canvas_pos(event.pos)

                    # Shapes are drawn when mouse button is released.
                    if current_tool != "brush":
                        draw_shape(canvas, current_tool, start_pos, end_pos)

                    is_drawing = False
                    start_pos = None
                    last_pos = None

        # Draw screen.
        screen.fill(WHITE)
        draw_toolbar()
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        # Preview shape while dragging.
        if is_drawing and current_tool != "brush" and start_pos is not None:
            preview = canvas.copy()
            mouse = pygame.mouse.get_pos()
            if mouse[1] > TOOLBAR_HEIGHT:
                end_pos = canvas_pos(mouse)
                draw_shape(preview, current_tool, start_pos, end_pos)
            screen.blit(preview, (0, TOOLBAR_HEIGHT))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
