import json
import random
from pathlib import Path
import pygame
from db import setup_db, save_result, personal_best, top_scores
pygame.init()
try:
    pygame.mixer.init()
except:
    pass
W, H = 600, 700
CELL = 30
TOP = 80
COLS, ROWS = 20, 20
FPS = 60
BASE = Path(__file__).parent
SETTINGS_FILE = BASE / "settings.json"
ASSETS = BASE / "assets"
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("TSIS4 Short Snake")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 20)
BIG = pygame.font.SysFont("Arial", 38)
def load_settings():
    default = {"snake_color": [40, 200, 80], "grid": True, "sound": True}
    if not SETTINGS_FILE.exists():
        save_settings(default)
        return default
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = default
    for key in default:
        if key not in data:
            data[key] = default[key]
    return data
def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)
def sound(name, settings):
    if not settings["sound"] or not pygame.mixer.get_init():
        return
    try:
        pygame.mixer.Sound(str(ASSETS / name)).play()
    except:
        pass
def write(text, size, x, y, color=(0, 0, 0), center=True):
    font = pygame.font.SysFont("Arial", size)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y)) if center else img.get_rect(topleft=(x, y))
    screen.blit(img, rect)
def draw_button(rect, label):
    mouse = pygame.mouse.get_pos()
    color = (230, 230, 230) if rect.collidepoint(mouse) else (255, 255, 255)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=8)
    write(label, 22, rect.centerx, rect.centery)
def is_click(event, rect):
    return event.type == pygame.MOUSEBUTTONDOWN and rect.collidepoint(event.pos)
def username_screen():
    name = ""
    while True:
        screen.fill((235, 235, 235))
        write("Snake Game", 46, W // 2, 150)
        write("Enter username", 26, W // 2, 240)
        box = pygame.Rect(170, 295, 260, 50)
        pygame.draw.rect(screen, (255, 255, 255), box)
        pygame.draw.rect(screen, (0, 0, 0), box, 2)
        screen.blit(FONT.render(name + "|", True, (0, 0, 0)), (box.x + 10, box.y + 14))
        write("Press ENTER", 20, W // 2, 390, (60, 60, 60))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name.strip() or "Player"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 14 and (event.unicode.isalnum() or event.unicode in "_-"):
                    name += event.unicode
        pygame.display.flip()
        clock.tick(FPS)
def menu_screen(username):
    buttons = [
        (pygame.Rect(200, 230, 200, 50), "Play", "play"),
        (pygame.Rect(200, 305, 200, 50), "Leaderboard", "leaderboard"),
        (pygame.Rect(200, 380, 200, 50), "Settings", "settings"),
        (pygame.Rect(200, 455, 200, 50), "Quit", "quit")
    ]
    while True:
        screen.fill((70, 150, 90))
        write("SNAKE", 58, W // 2, 110, (255, 255, 255))
        write("User: " + username, 24, W // 2, 170, (255, 255, 255))
        for rect, label, action in buttons:
            draw_button(rect, label)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            for rect, label, action in buttons:
                if is_click(event, rect):
                    return action
        pygame.display.flip()
        clock.tick(FPS)
def leaderboard_screen():
    back = pygame.Rect(200, 620, 200, 50)
    while True:
        rows = top_scores()
        screen.fill((245, 245, 245))
        write("Leaderboard", 40, W // 2, 55)
        write("Rank", 18, 30, 105, center=False)
        write("Name", 18, 100, 105, center=False)
        write("Score", 18, 260, 105, center=False)
        write("Level", 18, 350, 105, center=False)
        write("Date", 18, 430, 105, center=False)
        y = 140
        if not rows:
            write("No database data", 24, W // 2, 300)
        else:
            for i, row in enumerate(rows):
                name, score, level, date = row
                write(str(i + 1), 18, 40, y, center=False)
                write(str(name), 18, 100, y, center=False)
                write(str(score), 18, 270, y, center=False)
                write(str(level), 18, 365, y, center=False)
                write(str(date)[:16], 16, 430, y, center=False)
                y += 40
        draw_button(back, "Back")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if is_click(event, back):
                return
        pygame.display.flip()
        clock.tick(FPS)
def settings_screen(settings):
    colors = [
        [40, 200, 80],
        [70, 140, 255],
        [230, 70, 70],
        [230, 200, 50],
        [170, 80, 220]
    ]
    while True:
        screen.fill((238, 238, 238))
        write("Settings", 42, W // 2, 90)
        grid_btn = pygame.Rect(180, 180, 240, 50)
        sound_btn = pygame.Rect(180, 260, 240, 50)
        color_btn = pygame.Rect(180, 340, 240, 50)
        back = pygame.Rect(180, 530, 240, 50)
        draw_button(grid_btn, "Grid: " + ("On" if settings["grid"] else "Off"))
        draw_button(sound_btn, "Sound: " + ("On" if settings["sound"] else "Off"))
        draw_button(color_btn, "Change snake color")
        draw_button(back, "Save & Back")
        pygame.draw.rect(screen, settings["snake_color"], (270, 420, 60, 40))
        pygame.draw.rect(screen, (0, 0, 0), (270, 420, 60, 40), 2)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings)
                return settings
            if is_click(event, grid_btn):
                settings["grid"] = not settings["grid"]
            if is_click(event, sound_btn):
                settings["sound"] = not settings["sound"]
            if is_click(event, color_btn):
                i = colors.index(settings["snake_color"]) if settings["snake_color"] in colors else 0
                settings["snake_color"] = colors[(i + 1) % len(colors)]
            if is_click(event, back):
                save_settings(settings)
                return settings
        pygame.display.flip()
        clock.tick(FPS)
def game_over_screen(result):
    retry = pygame.Rect(150, 500, 130, 50)
    menu = pygame.Rect(320, 500, 130, 50)
    while True:
        screen.fill((35, 35, 35))
        write("GAME OVER", 50, W // 2, 120, (230, 60, 60))
        write("Score: " + str(result["score"]), 28, W // 2, 220, (255, 255, 255))
        write("Level: " + str(result["level"]), 28, W // 2, 270, (255, 255, 255))
        write("Personal best: " + str(result["best"]), 28, W // 2, 320, (255, 255, 255))
        draw_button(retry, "Retry")
        draw_button(menu, "Menu")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if is_click(event, retry):
                return "retry"
            if is_click(event, menu):
                return "menu"
        pygame.display.flip()
        clock.tick(FPS)
def cell_rect(pos, margin=2):
    x, y = pos
    return pygame.Rect(
        x * CELL + margin,
        TOP + y * CELL + margin,
        CELL - margin * 2,
        CELL - margin * 2
    )
def empty_cell(snake, obstacles, food=None, poison=None, power=None):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos in snake or pos in obstacles:
            continue
        if food and pos == food["pos"]:
            continue
        if poison and pos == poison["pos"]:
            continue
        if power and pos == power["pos"]:
            continue
        return pos
def make_food(snake, obstacles, poison=None, power=None):
    options = [
        ("normal", 1, (60, 220, 80), 70),
        ("bonus", 3, (240, 210, 50), 25),
        ("super", 5, (60, 220, 220), 5)
    ]
    name, points, color, weight = random.choices(
        options,
        weights=[item[3] for item in options]
    )[0]
    return {
        "pos": empty_cell(snake, obstacles, poison=poison, power=power),
        "points": points,
        "color": color,
        "born": pygame.time.get_ticks()
    }
def make_poison(snake, obstacles, food, power):
    return {
        "pos": empty_cell(snake, obstacles, food=food, power=power),
        "born": pygame.time.get_ticks()
    }
def make_power(snake, obstacles, food, poison):
    kind = random.choice(["speed", "slow", "shield"])
    colors = {
        "speed": (60, 130, 255),
        "slow": (180, 80, 220),
        "shield": (70, 220, 130)
    }
    return {
        "pos": empty_cell(snake, obstacles, food=food, poison=poison),
        "type": kind,
        "color": colors[kind],
        "born": pygame.time.get_ticks()
    }
def make_obstacles(level, snake):
    if level < 3:
        return []
    blocks = []
    head_x, head_y = snake[0]
    safe = set()
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            safe.add((head_x + dx, head_y + dy))
    while len(blocks) < level + 3:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos in snake or pos in blocks or pos in safe:
            continue
        blocks.append(pos)
    return blocks
def play_game(username, settings):
    best = personal_best(username)
    snake = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)
    next_direction = (1, 0)
    score = 0
    level = 1
    eaten = 0
    obstacles = []
    food = make_food(snake, obstacles)
    poison = make_poison(snake, obstacles, food, None)
    power = None
    active_power = None
    power_end = 0
    shield = False
    last_move = pygame.time.get_ticks()
    last_power_spawn = pygame.time.get_ticks()
    running = True
    paused = False
    while running:
        now = pygame.time.get_ticks()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key in [pygame.K_UP, pygame.K_w] and direction != (0, 1):
                    next_direction = (0, -1)
                if event.key in [pygame.K_DOWN, pygame.K_s] and direction != (0, -1):
                    next_direction = (0, 1)
                if event.key in [pygame.K_LEFT, pygame.K_a] and direction != (1, 0):
                    next_direction = (-1, 0)
                if event.key in [pygame.K_RIGHT, pygame.K_d] and direction != (-1, 0):
                    next_direction = (1, 0)
        if not paused:
            if food and now - food["born"] > 7000:
                food = make_food(snake, obstacles, poison, power)
            if poison and now - poison["born"] > 8000:
                poison = None
            if power and now - power["born"] > 8000:
                power = None
            if not power and now - last_power_spawn > 9000:
                power = make_power(snake, obstacles, food, poison)
                last_power_spawn = now
            if active_power in ["speed", "slow"] and now > power_end:
                active_power = None
            delay = max(70, 190 - level * 15)
            if active_power == "speed":
                delay = int(delay * 0.6)
            if active_power == "slow":
                delay = int(delay * 1.5)
            if now - last_move > delay:
                direction = next_direction
                head_x, head_y = snake[0]
                dx, dy = direction
                new_head = (head_x + dx, head_y + dy)
                crash = (
                    new_head[0] < 0 or new_head[0] >= COLS or
                    new_head[1] < 0 or new_head[1] >= ROWS or
                    new_head in snake or
                    new_head in obstacles
                )
                if crash:
                    if shield:
                        shield = False
                        active_power = None
                    else:
                        sound("bad.wav", settings)
                        running = False
                else:
                    snake.insert(0, new_head)
                    grow = False
                    if food and new_head == food["pos"]:
                        score += food["points"]
                        eaten += 1
                        grow = True
                        sound("eat.wav", settings)
                        food = make_food(snake, obstacles, poison, power)
                        if random.random() < 0.4:
                            poison = make_poison(snake, obstacles, food, power)
                        if eaten % 5 == 0:
                            level += 1
                            obstacles = make_obstacles(level, snake)
                    if poison and new_head == poison["pos"]:
                        sound("bad.wav", settings)
                        poison = None
                        for _ in range(3):
                            if snake:
                                snake.pop()
                        if len(snake) <= 1:
                            running = False
                        last_move = now
                        continue
                    if power and new_head == power["pos"]:
                        sound("power.wav", settings)
                        if power["type"] == "shield":
                            active_power = "shield"
                            shield = True
                        else:
                            active_power = power["type"]
                            power_end = now + 5000
                        power = None
                    if not grow:
                        snake.pop()
                last_move = now
        screen.fill((25, 25, 25))
        pygame.draw.rect(screen, (45, 45, 45), (0, 0, W, TOP))
        write("User: " + username, 18, 10, 8, (255, 255, 255), center=False)
        write("Score: " + str(score), 18, 150, 8, (255, 255, 255), center=False)
        write("Level: " + str(level), 18, 270, 8, (255, 255, 255), center=False)
        write("Best: " + str(max(best, score)), 18, 390, 8, (255, 255, 255), center=False)
        power_text = "Power: " + (active_power if active_power else "None")
        write(power_text, 18, 10, 45, (255, 255, 255), center=False)
        write("SPACE pause | ESC quit", 18, 350, 45, (255, 255, 255), center=False)
        if settings["grid"]:
            for x in range(0, W, CELL):
                pygame.draw.line(screen, (45, 45, 45), (x, TOP), (x, H))
            for y in range(TOP, H, CELL):
                pygame.draw.line(screen, (45, 45, 45), (0, y), (W, y))
        for block in obstacles:
            pygame.draw.rect(screen, (120, 120, 120), cell_rect(block), border_radius=5)
        if food:
            pygame.draw.rect(screen, food["color"], cell_rect(food["pos"], 4), border_radius=6)
            write(str(food["points"]), 16, food["pos"][0] * CELL + 15, TOP + food["pos"][1] * CELL + 15)
        if poison:
            pygame.draw.rect(screen, (120, 0, 0), cell_rect(poison["pos"], 4), border_radius=6)
            write("P", 16, poison["pos"][0] * CELL + 15, TOP + poison["pos"][1] * CELL + 15, (255, 255, 255))
        if power:
            pygame.draw.rect(screen, power["color"], cell_rect(power["pos"], 4), border_radius=6)
            write(power["type"][0].upper(), 16, power["pos"][0] * CELL + 15, TOP + power["pos"][1] * CELL + 15)
        snake_color = tuple(settings["snake_color"])
        for i, part in enumerate(snake):
            color = (255, 255, 255) if i == 0 else snake_color
            margin = 1 if i == 0 else 3
            pygame.draw.rect(screen, color, cell_rect(part, margin), border_radius=6)
        if shield:
            x, y = snake[0]
            pygame.draw.circle(screen, (70, 220, 130), (x * CELL + 15, TOP + y * CELL + 15), 24, 3)
        if paused:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            write("PAUSED", 42, W // 2, H // 2, (255, 255, 255))
        pygame.display.flip()
    result = {
        "score": score,
        "level": level,
        "best": max(best, score)
    }
    save_result(username, score, level)
    return result
def main():
    setup_db()
    settings = load_settings()
    username = username_screen()
    if not username:
        pygame.quit()
        return
    while True:
        action = menu_screen(username)
        if action == "play":
            result = play_game(username, settings)
            after = game_over_screen(result)
            while after == "retry":
                result = play_game(username, settings)
                after = game_over_screen(result)
        elif action == "leaderboard":
            leaderboard_screen()
        elif action == "settings":
            settings = settings_screen(settings)
        elif action == "quit":
            break
    pygame.quit()
main()
