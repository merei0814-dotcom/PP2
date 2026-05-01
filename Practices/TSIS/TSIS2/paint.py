import pygame
from datetime import datetime
from tools import flood_fill, draw_rhombus, draw_equilateral_triangle, draw_right_triangle

pygame.init()

# Window settings
WIDTH = 1000
HEIGHT = 700
TOOLBAR_HEIGHT = 100

CANVAS_WIDTH = WIDTH
CANVAS_HEIGHT = HEIGHT - TOOLBAR_HEIGHT

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS2 Paint")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 18)
big_font = pygame.font.SysFont("Arial", 28)

# Canvas is the drawing area.
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
canvas.fill((255, 255, 255))

# Current settings
current_tool = "pencil"
current_color = (0, 0, 0)
brush_size = 5

drawing = False
start_pos = None
last_pos = None

# Text tool settings
typing = False
text_pos = None
text_value = ""

# Tools and colors
tools = [
    "pencil", "line", "rect", "circle", "square",
    "right_tri", "eq_tri", "rhombus", "eraser",
    "fill", "text"
]

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 180, 0),
    (150, 0, 200),
    (255, 255, 255)
]


def canvas_position(mouse_pos):
    """Convert window position to canvas position."""
    x, y = mouse_pos

    if y < TOOLBAR_HEIGHT:
        return None

    return x, y - TOOLBAR_HEIGHT


def make_rect(pos1, pos2):
    """Create rectangle from two points."""
    x1, y1 = pos1
    x2, y2 = pos2

    x = min(x1, x2)
    y = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return pygame.Rect(x, y, width, height)


def make_square(pos1, pos2):
    """Create square from two points."""
    x1, y1 = pos1
    x2, y2 = pos2

    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        x = x1 - side
    else:
        x = x1

    if y2 < y1:
        y = y1 - side
    else:
        y = y1

    return pygame.Rect(x, y, side, side)


def draw_toolbar():
    """Draw toolbar with tool buttons, color buttons, and info."""
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, TOOLBAR_HEIGHT))

    x = 10
    y = 10

    for tool in tools:
        rect = pygame.Rect(x, y, 78, 30)

        if current_tool == tool:
            pygame.draw.rect(screen, (170, 200, 255), rect)
        else:
            pygame.draw.rect(screen, (240, 240, 240), rect)

        pygame.draw.rect(screen, (0, 0, 0), rect, 1)

        label = font.render(tool, True, (0, 0, 0))
        screen.blit(label, (x + 5, y + 6))

        x += 84

    x = 10
    y = 55

    for color in colors:
        rect = pygame.Rect(x, y, 30, 30)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)

        if current_color == color:
            pygame.draw.rect(screen, (255, 0, 0), rect, 3)

        x += 38

    info = f"Brush: {brush_size}px    Keys: 1=small, 2=medium, 3=large    Ctrl+S=save"
    info_text = font.render(info, True, (0, 0, 0))
    screen.blit(info_text, (300, 60))


def check_toolbar_click(mouse_pos):
    """Check if the user clicked a button in the toolbar."""
    global current_tool, current_color

    x, y = mouse_pos

    if y >= TOOLBAR_HEIGHT:
        return False

    # Tool buttons
    button_x = 10
    button_y = 10

    for tool in tools:
        rect = pygame.Rect(button_x, button_y, 78, 30)

        if rect.collidepoint(mouse_pos):
            current_tool = tool
            return True

        button_x += 84

    # Color buttons
    color_x = 10
    color_y = 55

    for color in colors:
        rect = pygame.Rect(color_x, color_y, 30, 30)

        if rect.collidepoint(mouse_pos):
            current_color = color
            return True

        color_x += 38

    return True


def draw_preview(surface, mouse_pos):
    """Draw live preview while dragging."""
    if not drawing or start_pos is None or mouse_pos is None:
        return

    color = current_color

    if current_tool == "line":
        pygame.draw.line(surface, color, start_pos, mouse_pos, brush_size)

    elif current_tool == "rect":
        rect = make_rect(start_pos, mouse_pos)
        pygame.draw.rect(surface, color, rect, brush_size)

    elif current_tool == "circle":
        rect = make_rect(start_pos, mouse_pos)
        pygame.draw.ellipse(surface, color, rect, brush_size)

    elif current_tool == "square":
        rect = make_square(start_pos, mouse_pos)
        pygame.draw.rect(surface, color, rect, brush_size)

    elif current_tool == "right_tri":
        draw_right_triangle(surface, start_pos, mouse_pos, color, brush_size)

    elif current_tool == "eq_tri":
        draw_equilateral_triangle(surface, start_pos, mouse_pos, color, brush_size)

    elif current_tool == "rhombus":
        draw_rhombus(surface, start_pos, mouse_pos, color, brush_size)


def draw_final_shape(end_pos):
    """Draw final shape on canvas after mouse release."""
    color = current_color

    if current_tool == "line":
        pygame.draw.line(canvas, color, start_pos, end_pos, brush_size)

    elif current_tool == "rect":
        rect = make_rect(start_pos, end_pos)
        pygame.draw.rect(canvas, color, rect, brush_size)

    elif current_tool == "circle":
        rect = make_rect(start_pos, end_pos)
        pygame.draw.ellipse(canvas, color, rect, brush_size)

    elif current_tool == "square":
        rect = make_square(start_pos, end_pos)
        pygame.draw.rect(canvas, color, rect, brush_size)

    elif current_tool == "right_tri":
        draw_right_triangle(canvas, start_pos, end_pos, color, brush_size)

    elif current_tool == "eq_tri":
        draw_equilateral_triangle(canvas, start_pos, end_pos, color, brush_size)

    elif current_tool == "rhombus":
        draw_rhombus(canvas, start_pos, end_pos, color, brush_size)


def save_canvas():
    """Save canvas as png with timestamp."""
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"paint_{now}.png"
    pygame.image.save(canvas, filename)
    print("Saved:", filename)


running = True

while running:
    mouse_window_pos = pygame.mouse.get_pos()
    mouse_canvas_pos = canvas_position(mouse_window_pos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()

            # Ctrl + S saves canvas
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if event.key == pygame.K_s:
                    save_canvas()

            # Brush sizes
            if event.key == pygame.K_1:
                brush_size = 2
            elif event.key == pygame.K_2:
                brush_size = 5
            elif event.key == pygame.K_3:
                brush_size = 10

            # Text input
            if typing:
                if event.key == pygame.K_RETURN:
                    text_surface = big_font.render(text_value, True, current_color)
                    canvas.blit(text_surface, text_pos)
                    typing = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_ESCAPE:
                    typing = False
                    text_value = ""
                    text_pos = None

                elif event.key == pygame.K_BACKSPACE:
                    text_value = text_value[:-1]

                else:
                    text_value += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if check_toolbar_click(event.pos):
                continue

            pos = canvas_position(event.pos)

            if pos is None:
                continue

            if current_tool == "fill":
                flood_fill(canvas, pos, current_color)

            elif current_tool == "text":
                typing = True
                text_pos = pos
                text_value = ""

            else:
                drawing = True
                start_pos = pos
                last_pos = pos

        elif event.type == pygame.MOUSEMOTION:
            if drawing and mouse_canvas_pos is not None:
                if current_tool == "pencil":
                    pygame.draw.line(canvas, current_color, last_pos, mouse_canvas_pos, brush_size)
                    last_pos = mouse_canvas_pos

                elif current_tool == "eraser":
                    pygame.draw.line(canvas, (255, 255, 255), last_pos, mouse_canvas_pos, brush_size)
                    last_pos = mouse_canvas_pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing and mouse_canvas_pos is not None:
                if current_tool not in ["pencil", "eraser"]:
                    draw_final_shape(mouse_canvas_pos)

            drawing = False
            start_pos = None
            last_pos = None

    screen.fill((200, 200, 200))
    draw_toolbar()

    preview_surface = canvas.copy()

    if drawing and mouse_canvas_pos is not None and current_tool not in ["pencil", "eraser"]:
        draw_preview(preview_surface, mouse_canvas_pos)

    screen.blit(preview_surface, (0, TOOLBAR_HEIGHT))

    if typing and text_pos is not None:
        preview_text = big_font.render(text_value + "|", True, current_color)
        screen.blit(preview_text, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
